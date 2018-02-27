import pickle
import staticdata as sd
import xlwt

SHEET = "game_data"

def getworkbook(wbname = "data//originaldata.xls", sheetname = SHEET):
    wb = xlwt.Workbook(encoding='utf-8')
    st = wb.add_sheet(sheetname, cell_overwrite_ok=True)
    return wb, st

def writexls(workbook, sheet, cols=sd.COLUMNNAME, data=None):
    for i in range(len(data)):
        print("write the data:%s"%i )
        eachrow = data[i]
        for j in range(len(eachrow)):
            sheet.write(i+1, j, eachrow[cols[j]])
    workbook.save("originaldata.xls")

def writecolumns(workbook, sheet, cols=sd.COLUMNNAME):
    print("write the columns:")
    for i in range(0, len(cols)):
        sheet.write(0, i, cols[i])
    workbook.save("originaldata.xls")

def get_basic_info(backup):
    wb, st = getworkbook()
    f = open(backup,"rb")
    alldata = pickle.load(f,encoding='utf-8')
    print(len(alldata))
    f.close()
    writecolumns(wb, st)
    writexls(wb, st, data = alldata)
    return alldata

get_basic_info("datadump.dat")