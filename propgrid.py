#!python3
#propgrid.py takes a property grid from a spreadsheet and converts it into 
#the format required for input into PFR Engineering FRNC-5PC software.  
import pandas as pd
import pyinputplus as pyip
import os
#Get data
def getfile(name):  #getfile returns a full filepath as a string
    while True: #request a filepath and check for errors
        filepath=pyip.inputFilepath('\ninput filepath\n', blank=False)
        if os.path.isdir(filepath)==True:
            break
        else:
            continue
    while True:  #request a filename and check for errors
        filename=pyip.inputMenu(os.listdir(filepath), blank=False,numbered=True)
        full=os.path.join(filepath, filename)
        if os.path.isfile(full)==True:
            break
        else:
            continue
    return full

#get stream label info
num=pyip.inputInt(prompt='Stream number: ', blank=False, min=2)
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

print(f'\nRename columns in the excel spreadsheet to match the following: \n{labels}\n')

f=''
f=getfile(f) #get filepath to file
#TODO: address different filetypes (ie. csv)
file=pd.ExcelFile(f) #open the excel file
sheet=pyip.inputMenu(file.sheet_names, numbered=True) #select a sheet
df=pd.read_excel(file, sheet_name=sheet) #read data into dataframe
#check data
    #TODO:values increasing/decreasing with temperature / pressure
    #TODO:verify covers temperature and pressure ranges
    #TODO:verify each phase exists on all isobars
    #TODO:locate dew & bubble points & prevent filtering them out
#filter data 
    #TODO:verify covers pressure range
    #TODO:verify each phase exists on all isobars
    #TODO:identify dew & bubble points on remaining isobars 
    #TODO:prevent filtering dew & bubble points +/- 1 temperature

press=df["PRESS"].unique().tolist() #get unique pressures from df
temp=df["TEMP"].unique().tolist()   #get unique temperatures from df
print(f'\nthere are {len(press)} isobars\n')
if len(press)>7:    #reduce list of pressures to 7 for FRNC-5
    print('Maximum 7 isobars allowed\n')
    print('Delete from the following list:\n')
    for p in range(len(press)): #convert to strings for inputMenu
        press[p]=str(press[p])
    while len(press)>7:
        response=pyip.inputMenu(press, numbered=True)
        press.remove(response)
    for p in range(len(press)): #convert back to numbers
        press[p]=float(press[p])
print('The remaining isobars are:\n')
for p in range(len(press)):
    print(f'{p+1}. {press[p]}')

print(f'\nThere are {len(temp)} isotherms\n')
if len(temp)>20:    #reduce list of temperatures to 20 for FRNC-5
    print('Maximum 20 isotherms allowed\n')
    print('Delete from the following list:\n')
    for t in range(len(temp)): #convert to strings for inputMenu
        temp[t]=str(temp[t])
    while len(temp)>20:
        response=pyip.inputMenu(temp, numbered=True)
        temp.remove(response)
    for t in range(len(temp)): #convert back to numbers
        temp[t]=float(temp[t])
print('The remaining isotherms are:\n')
for t in range(len(temp)):
    print(f'{t+1}. {temp[t]}')

#filter df using press & temp
df2=df.loc[(df['PRESS'].isin(press)) & (df['TEMP'].isin(temp))]
#output data
folder=os.path.dirname(f) #get folder
#open a text file with automatic filename
output=open(folder + '\\' + str(num) + '-' + str(stream) + '.txt', 'w')
output.write(f'STREAM,{num},{stream}') #write stream data
#create dict of labels
value={'REF GRID':'TEMP','WEIGHT FR':'WEIGHT FR','LIQ ENTH':'LIQ ENTH',
'VAP ENTH':'VAP ENTH','LIQ VIS':'LIQ VIS','VAP VIS':'VAP VIS',
'LIQ DENS':'LIQ DENS','VAP DENS':'VAP DENS','LIQ TH CON':'LIQ TH CON',
'VAP TH CON':'VAP TH CON','LIQ SU TEN':'LIQ SU TEN','LIQ HE CAP':'LIQ HE CAP',
'VAP HE CAP':'VAP HE CAP'}
label=['REF GRID','WEIGHT FR','LIQ ENTH','VAP ENTH','LIQ VIS','VAP VIS',
'LIQ DENS','VAP DENS','LIQ TH CON','VAP TH CON','LIQ SU TEN','LIQ HE CAP',
'VAP HE CAP']
#TODO: deal with missing labels for single phase fluids
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
