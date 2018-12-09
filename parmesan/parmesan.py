#!/usr/bin/env python
# from pathlib import Path

import numpy as np
import pandas as pd

from qvd import QvdFile, get_symbols

QLIK_EPOCH_ORIGIN_STR='1899-12-30'
QLIK_ORIGIN=pd.Timestamp(QLIK_EPOCH_ORIGIN_STR)


def transform_symbol_type(symbols, qvd_field_type):
    return (pd.to_datetime(symbols, unit='D', origin=QLIK_ORIGIN)
            if qvd_field_type in ('DATE', 'TIMESTAMP')
            else symbols)


def read_qvd(qvd_file):

    q = QvdFile()
    q.Load(qvd_file)
    th = q.GetTableHeader()
    idx_mtx = np.array(th.Indices, dtype=np.int64).reshape((th.NoOfRecords, -1))
    df = pd.DataFrame(idx_mtx)

    # insert missing columns; columns are missing if they only contain a single symbol
    for i, col in enumerate(th.Fields):
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


def convert_qvd_to_parquet(qvd_file, pq_file):
    read_qvd(qvd_file).write_parquet(pq_file)


def convert_qvd_tree(qvd_prefix, pq_prefix, recursive=False):
    pass


if __name__ == '__main__':
    import sys
    from IPython import embed
    if len(sys.argv) > 1:
        q = QvdFile()
        q.Load(sys.argv[1])
        th = q.GetTableHeader()
        idx_mtx = np.array(th.Indices, dtype=np.int64).reshape((th.NoOfRecords, -1))
        df = pd.DataFrame(idx_mtx)

        # insert missing columns; columns are missing if they only contain a single symbol
        for i, col in enumerate(th.Fields):
            if col.BitWidth == 0:
                df.insert(i, f'{i}a', 0, True)
        df.columns = range(len(th.Fields))

        # buildup a map that renames indices to their corresponding symbol
        idx_mapping = {i: pd.Series(transform_symbol_type(*get_symbols(fld))).to_dict()
                       for (i, fld) in enumerate(th.Fields)}
        df2 = pd.concat([df[i].map(idx_mapping[i]) for i in df], axis=1)

        colnames = [x.FieldName for x in th.Fields]
        df2.columns = colnames

        #df = read_qvd(sys.argv[1])

    embed()
