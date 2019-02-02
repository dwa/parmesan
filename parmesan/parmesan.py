import errno
import os

import numpy as np
import pandas as pd

from .qvd import QvdFile, get_symbols


QLIK_EPOCH_ORIGIN_STR = '1899-12-30'
QLIK_ORIGIN = pd.Timestamp(QLIK_EPOCH_ORIGIN_STR)

MAX_TS = (pd.Timestamp.max - QLIK_ORIGIN).days


def convert_qlikcol_to_dt(col):
    capped_dt = col.where(col <= MAX_TS, MAX_TS)
    return (pd.to_datetime(capped_dt, unit='D', origin=QLIK_ORIGIN)
            .astype('datetime64[ms]'))


def transform_symbol_type(symbols, qvd_field_type):
    syms = pd.Series(symbols)
    return (convert_qlikcol_to_dt(syms)
            if qvd_field_type in ('DATE', 'TIMESTAMP')
            else syms)


def read_qvd(qvd_file, use_string_default=False, invert_dual_for_field=None, field_types=None):

    if not os.path.exists(qvd_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), qvd_file)

    q = QvdFile()
    q.Load(qvd_file)
    th = q.GetTableHeader()
    idx_mtx = np.array(th.Indices, dtype=np.int64).reshape((th.NoOfRecords, -1))
    df = pd.DataFrame(idx_mtx)

    sorted_fields = sorted(th.Fields, key=lambda x: x.BitOffset)

    # insert missing columns; columns are missing if they only contain a single symbol
    for i, col in enumerate(sorted_fields):
        if col.BitWidth == 0:
            df.insert(i, f'{i}a', 0, True)
    df.columns = range(len(th.Fields))

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
        return transform_symbol_type(symbols, ftype)

    # buildup a map that renames indices to their corresponding symbol
    idx_mapping = {i: (prep_symbols(fld).to_dict())
                   for (i, fld) in enumerate(sorted_fields)}
    df2 = pd.concat([df[i].map(idx_mapping[i]) for i in df], axis=1)

    colnames = [x.FieldName for x in sorted_fields]
    df2.columns = colnames

    return df2


def qvd_to_parquet(qvd_file, pq_file, overwrite=False):

    if not overwrite and os.path.exists(pq_file):
        raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), pq_file)

    read_qvd(qvd_file).to_parquet(pq_file)


## Local Variables: ***
## mode:python ***
## coding: utf-8 ***
## End: ***
