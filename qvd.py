import cppyy
import pkgconfig

libxml2_paths = pkgconfig.cflags('libxml-2.0').split(' ')
for p in libxml2_paths:
    cppyy.add_include_path(p[2:])

libqvdreader = 'qvdreader/libqvdreader.so'
cppyy.load_library(libqvdreader)

cppyy.include('qvdreader/QvdFile.h')
from cppyy.gbl import QvdFile

cppyy.include('qvdreader/LineageInfo.h')
from cppyy.gbl import QvdLineageInfo
QvdLineageInfo.__repr__ = lambda x: repr(f'QvdLineageInfo[{x.Discriminator}|{x.Statement}]')

cppyy.include('qvdreader/QvdTableHeader.h')
from cppyy.gbl import QvdTableHeader
QvdTableHeader.__repr__ = lambda x: repr(f'QvdTableHeader[{x.TableName}|{x.NoOfRecords}|{x.QvBuildNo}|{x.CreatorDoc}|{x.CreateUtcTime}]')

cppyy.include('qvdreader/QvdField.h')
from cppyy.gbl import QvdField
QvdField.__repr__ = lambda x: repr(f'QvdField[{x.FieldName}|{x.Type}|{x.NoOfSymbols}]')

cppyy.include('qvdreader/QvdSymbol.h')
from cppyy.gbl import QvdSymbol
QvdSymbol.__repr__ = lambda x: repr(f'QvdSymbol[{x.Type}|{x.IntValue}|{x.DoubleValue}|{x.StringValue}]')

# symtype_mapping = {'REAL': 2,
#                    'INTEGER': 1,
#                    'UNKNOWN': 4}


def get_symbols(qvd_field):
    # symtype = symtype_mapping[qvd_field.Type]
    # assert
    # bit 1 = int; bit 2 = double; bit 4 = string ?
    def get_sym_by_type(qvd_symbol):
        if qvd_symbol.Type in (2, 6):
            return qvd_symbol.DoubleValue
        elif qvd_symbol.Type in (1, 5):
            return qvd_symbol.IntValue
        elif qvd_symbol.Type == 4:
            return qvd_symbol.StringValue
        else:
            # FIXME: use logging?
            print(f'Unknown type: {qvd_symbol.Type}')
            return None

    return ([get_sym_by_type(x) for x in qvd_field.Symbols], qvd_field.Type)
