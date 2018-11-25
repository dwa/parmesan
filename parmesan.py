# from pathlib import Path

import numpy as np
import pandas as pd

from qvd import QvdFile, get_symbols

# FIXME: category or datatype, should be settable based on ratio: (field length) / NoOfRecords
#
# symtype_to_dtype =  {'REAL': np.double,
#                      'INTEGER': np.int64,
#                      'UNKNOWN': np.str}

def read_qvd(qvd_file):

    q = QvdFile()
    q.Load(qvd_file)
    th = q.GetTableHeader()
    idx_mtx = np.array(th.Indices, dtype=np.int64).reshape((th.NoOfRecords, -1))
    df = pd.DataFrame(idx_mtx)


    def fix_col(i):
        col = df[i].astype('category')
        col.cat.categories, _field_type = get_symbols(th.Fields[i])
        return col

    df2 = pd.concat([fix_col(x) for x in df], axis=1)

    colnames = [x.FieldName for x in th.Fields]
    df2.columns = colnames

    return df2


def convert_qvd_to_parquet(qvd_file, pq_file):
    read_qvd(qvd_file).write_parquet(pq_file)


def convert_qvd_tree(qvd_prefix, pq_prefix, recursive=False):
    pass


# df = read_qvd('products_source.qvd')
