import errno
import os

import numpy as np
import pandas as pd

from tqdm import tqdm

from .qvd import QvdFile, get_symbols


QLIK_EPOCH_ORIGIN_STR = '1899-12-30'
QLIK_ORIGIN = pd.Timestamp(QLIK_EPOCH_ORIGIN_STR)

MAX_TS = (pd.Timestamp.max.to_pydatetime() - QLIK_ORIGIN.to_pydatetime()).days


def convert_qlikcol_to_dt(col):
    capped_dt = col.where(col <= MAX_TS, MAX_TS)
    return (pd.to_datetime(capped_dt, unit='D', origin=QLIK_ORIGIN)
            .astype('datetime64[ms]'))


def transform_symbol_type(symbols, qvd_field_type, field_name):

    if qvd_field_type in ('DATE', 'TIMESTAMP', 'TIME'):
        return convert_qlikcol_to_dt(symbols)
    qvd_types = {'REAL': np.float64,
                 'INTEGER': 'Int64',
                 'FIX': np.float64}

    convert_to = qvd_types.get(qvd_field_type, False)

    if convert_to:
        try:
            return symbols.astype(convert_to)
        except ValueError as e:
            raise RuntimeError(f"Failed to convert field '{field_name}' to type {qvd_field_type}") from e
    else:
        return symbols


def mk_series(symbols):
    try:
        return pd.Series(symbols, dtype='Int64')
    except:
        pass
    try:
        return pd.Series(symbols, dtype='float64')
    except:
        pass
    return pd.Series(symbols)


def read_qvd(qvd_file, use_string_default=False, invert_dual_for_field=None,
             field_types=None, cast_types=[], progress=True):

    if not os.path.exists(qvd_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), qvd_file)

    q = QvdFile()
    q.Load(qvd_file)
    th = q.GetTableHeader()

    sorted_fields = sorted(th.Fields, key=lambda x: x.BitOffset)

    if th.NoOfRecords > 0:
        # FIXME: set dtype based on no of rows (or max cardinality):
        idx_mtx = np.asarray(th.Indices, dtype=np.int32).reshape((th.NoOfRecords, -1))
        df = pd.DataFrame(idx_mtx)

        # insert missing columns; columns are missing if they only contain a single symbol
        for i, col in enumerate(sorted_fields):
            if col.BitWidth == 0:
                df.insert(i, f'{i}a', 0, True)
        df.columns = range(len(th.Fields))
    else:
        df = pd.DataFrame([], columns=range(len(sorted_fields)))

    def default_dual_type(field):
        if isinstance(invert_dual_for_field, list):
            default_type = (not use_string_default) if (field.FieldName in invert_dual_for_field) else use_string_default
        else:
            default_type = use_string_default
        return default_type

    def prep_symbols(field):
        symbols, ftype = get_symbols(field, default_dual_type(field))
        if isinstance(field_types, dict) and field.FieldName in field_types:
            ftype = field_types[field.FieldName]
        symbols = mk_series(list(symbols))
        return transform_symbol_type(symbols, ftype, field.FieldName) if (ftype in cast_types) else symbols

    enum_sorted_fields = enumerate(sorted_fields)
    for (i, fld) in (tqdm(enum_sorted_fields, total=len(sorted_fields)) if progress else enum_sorted_fields) :
        # buildup a map that renames indices to their corresponding symbol:
        value_mapping = prep_symbols(fld).to_dict()
        df[i] = df[i].map(value_mapping)
    df.columns = [x.FieldName for x in sorted_fields]
    return df


def qvd_to_parquet(qvd_file, pq_file, overwrite=False, cast_types=[],
                   row_group_size=500000, progress=True):

    if not overwrite and os.path.exists(pq_file):
        raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), pq_file)

    df = read_qvd(qvd_file, cast_types=cast_types, progress=progress)
    # needed to deal with columns of mixed type (pandas issue #21228):
    dtypes = {p.index: str for p in df.dtypes.reset_index().itertuples() if p._2 == 'object'}

    df.astype(dtypes).to_parquet(pq_file,
                                 engine='pyarrow',
                                 compression='snappy',
                                 index=False,
                                 row_group_size=row_group_size)


## Local Variables: ***
## mode:python ***
## coding: utf-8 ***
## End: ***
