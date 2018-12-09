import click

from .qvd import QvdFile, get_symbols
from .parmesan import read_qvd, qvd_to_parquet


@click.command()
@click.argument('qvd_file')
def debug_qvd(qvd_file):

    # import sys
    from IPython import embed
    df = read_qvd(qvd_file)
    embed()

    # if len(sys.argv) > 1:
    #     q = QvdFile()
    #     q.Load(sys.argv[1])
    #     th = q.GetTableHeader()
    #     idx_mtx = np.array(th.Indices, dtype=np.int64).reshape((th.NoOfRecords, -1))
    #     df = pd.DataFrame(idx_mtx)

    #     # insert missing columns; columns are missing if they only contain a single symbol
    #     for i, col in enumerate(th.Fields):
    #         if col.BitWidth == 0:
    #             df.insert(i, f'{i}a', 0, True)
    #     df.columns = range(len(th.Fields))

    #     # buildup a map that renames indices to their corresponding symbol
    #     idx_mapping = {i: pd.Series(transform_symbol_type(*get_symbols(fld))).to_dict()
    #                    for (i, fld) in enumerate(th.Fields)}
    #     df2 = pd.concat([df[i].map(idx_mapping[i]) for i in df], axis=1)

    #     colnames = [x.FieldName for x in th.Fields]
    #     df2.columns = colnames

    #     #df = read_qvd(sys.argv[1])

    # embed()


@click.command()
@click.argument('qvd-file')
@click.option('--out-file', default='outfile.parquet', show_default=True)
@click.option('--overwrite/--no-overwrite', default=False, show_default=True)
def convert_qvd_to_parquet(qvd_file, out_file, overwrite):
    qvd_to_parquet(qvd_file, out_file, overwrite)
