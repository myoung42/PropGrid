#!/usr/bin/env python3
#propgrid.py takes a property grid from a table and converts it into 
#the format required for input into PFR Engineering FRNC-5PC software.  
import pandas as pd
import pyinputplus as pyip
import os, logging, argparse
#TODO:values increasing/decreasing with temperature / pressure
#TODO:verify covers temperature and pressure ranges
#TODO:verify each phase exists on all isobars
#TODO:locate dew & bubble points & prevent filtering them out
#TODO:verify dew & bubble point data exists, and fill in if missing
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOG_LEVEL = logging.DEBUG
def getfile(name):  #getfile returns a full filepath as a string
    while True: #request a filepath and check for errors
        filepath=pyip.inputFilepath('\ninput filepath\n', blank=False)
        if os.path.isdir(filepath)==True:
            print('\n')
            break
        else:
            continue
    while True:  #request a filename and check for errors
        filename=pyip.inputMenu(os.listdir(filepath), blank=False,numbered=True)
        full=os.path.join(filepath, filename)
        if os.path.isfile(full)==True:
            print('\n')
            break
        else:
            continue
    return full
def pd_excel(f): #take an excel file and return a dataframe from the sheet
    file=pd.ExcelFile(f) #open the excel file
    sheet=pyip.inputMenu(file.sheet_names, numbered=True) #select a sheet
    df=pd.read_excel(file, sheet_name=sheet) #read data into dataframe
    return df
def pd_csv(f):  #TODO:take a csv file and return a dataframe
    logging.exception('unsupported file type')
def pd_clean(df, labels): #take a df and clean it up 
    dfcolumns=df.columns.tolist() #list df columns
    #verify TEMP, PRESS, and WEIGHT FR are in dfcolumns - kill program if not included
    baremin=['PRESS','TEMP','WEIGHT FR']
    if set(baremin).issubset(set(dfcolumns))==False:
        raise Exception('Grid must include PRESS, TEMP, and WEIGHT FR at minimum')
    newcol=list(set(labels)-set(dfcolumns)) #compare df columns to expected columns
    newdfcol=dfcolumns+newcol #combine columns lists into new list
    df=df.reindex(columns=newdfcol) #reindex to add new columns with null values
    df=df.fillna('0.0') #replace null values with zeros
    return df
def build_filter(flist, value, limit):  #take a list and remove values to build the filter
    print(f'\nthere are {len(flist)} {value}\n')
    if len(flist)>limit:    #reduce list of listures to 7 for FRNC-5
        print(f'Maximum {limit} {value} allowed\n')
        print('Delete from the following list:\n')
        for p in range(len(flist)): #convert to strings for inputMenu
            flist[p]=str(flist[p])
        while len(flist)>limit:
            response=pyip.inputMenu(flist, numbered=True)
            flist.remove(response)
        for p in range(len(flist)): #convert back to numbers
            flist[p]=float(flist[p])
    print(f'The remaining {value} are:\n')
    for p in range(len(flist)):
        print(f'{p+1}. {flist[p]}')
    return flist
def output(df2, f, num, stream, label, value, press, temp):
    folder=os.path.dirname(f) #get folder
    #open a text file with automatic filename
    output=open(folder + '\\' + str(num) + '-' + str(stream) + '.txt', 'w')
    output.write(f'STREAM,{num},{stream}') #write stream data
    for i in range(len(label)): #loop over labels
        for p in range(len(press)):  #iterate over pressure range
            df3=df2[df2['PRESS']==press[p]]  #returns a dataframe filtered for a single pressure
            df4=df3[[value[label[i]]]] #returns a dataframe of a single label for a single pressure
            output.write(f'\n{label[i]},{press[p]}') #write row label
            data=df4[value[label[i]]].tolist()  #returns a list of the items in df4 
            for d in range(0,min(6,len(data))): #iterate over temperature range
                output.write(f',{data[d]}')  #write temperature data
            if len(temp)<6: #adjust for grid size
                continue
            output.write('\n')
            output.write(f'{label[i]},{press[p]}') #write row label
            for d in range(6,min(12,len(data))): #iterate over temperature range
                output.write(f',{data[d]}') #write temperature data
            if len(temp)<12:   #adjust for grid size
                continue
            output.write('\n')
            output.write(f'{label[i]},{press[p]}')  #write row label
            for d in range(12,len(data)):  #iterate over temperature range
                output.write(f',{data[d]}') #write temperature data
    output.write('\nEND PROPERTY INPUT') #write closing 
    output.close() #close text file
def main():
    num=pyip.inputInt(prompt='Stream number: ', blank=False, min=2)  #get stream label info
    stream=pyip.inputStr(prompt='Stream name: ', blank=False)
    #get T & P range
    #tmin=pyip.inputNum(prompt='Min Grid Temperature °F: ', blank=False)
    #tmax=pyip.inputNum(prompt='Max Grid Temperature °: ', blank=False, greaterThan=tmin)
    #pmin=pyip.inputNum(prompt='Min Grid Pressure psia: ', blank=False)
    #pmax=pyip.inputNum(prompt='Max Grid Pressure psia: ', blank=False, greaterThan=pmin)
    #list input column labels
    labels=['RID','PRESS','TEMP','WEIGHT FR','LIQ ENTH','LIQ VIS','LIQ DENS',
    'LIQ TH CON','LIQ SU TEN','LIQ HE CAP','VAP ENTH','VAP VIS','VAP DENS',
    'VAP TH CON','VAP HE CAP']
    #dict to reference output labels with input labels
    value={'REF GRID':'TEMP','WEIGHT FR':'WEIGHT FR','LIQ ENTH':'LIQ ENTH',
    'VAP ENTH':'VAP ENTH','LIQ VIS':'LIQ VIS','VAP VIS':'VAP VIS',
    'LIQ DENS':'LIQ DENS','VAP DENS':'VAP DENS','LIQ TH CON':'LIQ TH CON',
    'VAP TH CON':'VAP TH CON','LIQ SU TEN':'LIQ SU TEN','LIQ HE CAP':'LIQ HE CAP',
    'VAP HE CAP':'VAP HE CAP'}
    #list output column labels
    label=['REF GRID','WEIGHT FR','LIQ ENTH','VAP ENTH','LIQ VIS','VAP VIS',
    'LIQ DENS','VAP DENS','LIQ TH CON','VAP TH CON','LIQ SU TEN','LIQ HE CAP',
    'VAP HE CAP']
    EXTENSIONS = {'xlsx': pd_excel,'xls': pd_excel,'xlsm': pd_excel,'csv': pd_csv}
    print(f'\nRename columns in the excel spreadsheet to match the following: \n{labels}\n')
    f=getfile(f:='') #get filepath to file
    extension = f.split('.')[-1]  # Obtain the extension
    if extension in EXTENSIONS:
        filetype = EXTENSIONS.get(extension)
        df=filetype(f)
    else:
        logging.exception('unsupported file type')
        raise Exception('unsupported file type')
    df=pd_clean(df, labels)
    press=df["PRESS"].unique().tolist() #get unique pressures from df
    press.sort()
    press=build_filter(press, 'isobars', 7) #build pressure filter
    dfp=df.loc[(df['PRESS'].isin(press))]  #filter dataframe for selected pressures
    tfilterby=pyip.inputMenu(['common','unique'],prompt='Filter by common or unique isotherms?:\n', blank=False,numbered=True)
    if tfilterby=='common':
        temp=dfp["TEMP"].unique().tolist()   #get unique temperatures from df
        temp.sort()
        temp=build_filter(temp, 'isotherms', 20) #build temperature filter
        df2=df.loc[(df['PRESS'].isin(press)) & (df['TEMP'].isin(temp))] #filter df using press & temp
    else:
        temp=[]
        df2=pd.DataFrame(columns=label)
        for p in range(len(press)):  #iterate over pressure range
            dft=dfp[dfp['PRESS']==press[p]]  #returns a dataframe filtered for a single pressure
            temptemp=dft["TEMP"].unique().tolist()   #get unique temperatures from df
            temptemp.sort()
            temptemp=build_filter(temptemp, 'isotherms', 20) 
            [temp.append(x) for x in temptemp if x not in temp]
            temp.sort()
            dftemp=dft.loc[(dft['PRESS'].isin(press)) & (dft['TEMP'].isin(temptemp))] #filtered dataframe for one isobar
            df2=df2.append(dftemp)         
    output(df2, f, num, stream, label, value, press, temp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', dest='log', type=str, help='log file', default=None)
    args = parser.parse_args()
    if args.log:
        logging.basicConfig(format=LOG_FORMAT, filename=args.log, level=LOG_LEVEL)
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    try:
        main()
    except Exception as exc:
        logging.exception("Error running task")
        exit(1)