import errno
import os

import numpy as np
import pandas as pd

from .qvd import QvdFile, get_symbols

QLIK_EPOCH_ORIGIN_STR='1899-12-30'
QLIK_ORIGIN=pd.Timestamp(QLIK_EPOCH_ORIGIN_STR)


def transform_symbol_type(symbols, qvd_field_type):
    return (pd.to_datetime(symbols, unit='D', origin=QLIK_ORIGIN)
            if qvd_field_type in ('DATE', 'TIMESTAMP')
            else symbols)


def read_qvd(qvd_file):

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

    # buildup a map that renames indices to their corresponding symbol
    idx_mapping = {i: pd.Series(transform_symbol_type(*get_symbols(fld))).to_dict()
                   for (i, fld) in enumerate(th.Fields)}
    df2 = pd.concat([df[i].map(idx_mapping[i]) for i in df], axis=1)

    colnames = [x.FieldName for x in th.Fields]
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
