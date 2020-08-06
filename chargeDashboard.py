import dash
import dash_table
from dash.dependencies import Input as ddInput
from dash.dependencies import Output as ddOutput
from dash.dependencies import State as ddState
import dash_core_components as dcc
import dash_html_components as html
import datetime
import os
import pandas as pd
from lib_File_Reader import File_Reader

def generateMarks(input):
    ret = {}
    if isinstance(input, list):
        for x in input:
            ret[x] = {'label': str(x)}
    elif isinstance(input, dict):
        for key, value in input.items():
            ret[key] = {'label': str(value)}
    return ret

def dateRange(startDate, endDate):
    delta = endDate - startDate
    ranger = []
    for i in range(delta.days + 2):
        ranger.append(startDate + datetime.timedelta(days=i))
    return ranger

def generateDropdownList(input = None, all=False,none=False):
	ret=[]
	if(input is None or (input is not None and len(input)<=0)):
		ret.append({'label': 'Empty', 'value': ''})
		return ret
	if(none):
		ret.append({'label': 'None', 'value': ''})
	elif(all):
		ret.append({'label': 'All', 'value': ''})
	if(isinstance(input, list)):
		for v in input:
			ret.append({'label': v, 'value': v})
	elif(isinstance(input, dict)):
		for key, value in dictt.items():
			ret.apend({'label': key, 'value': value})
	return ret

def timeToInt(s, seperator):
    x = s.split(seperator)
    if(len(x)==1):
        return int(s)
    elif(len(x)==2):
        return int(x[0])*60+int(x[1])
    elif(len(x)==3):
        return int(x[0])*3600+int(x[1])*60+int(x[2])
    return 0
def calculateRunningDecrease(l):
    s=0
    for i in range(len(l)-1):
        prev = l[i]
        nex = l[i+1]
        if(prev>nex):
            diff = prev-nex
            s = s + diff
    return s

defaultDirectory = os.path.join(os.path.dirname(os.path.abspath(__file__)),'files')
fileDirectory = defaultDirectory
#fileDirectory = os.path.join(os.getcwd(),'files')
subDirectories = [ f.path for f in os.scandir(fileDirectory) if f.is_dir() ]
timeZone = datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo
fileReader = None
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Open+Sans&display=swap'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, assets_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'))


app.title = 'Charge Dashboard'
app.layout = html.Div(
    children=[
        html.Div(
            id='top',
            className = 'selectorDiv',
            children = [
                html.A(href='https://play.google.com/store/apps/details?id=com.waterdaaan.chargemonitor', children=html.Button("Download app", id='downloadLink',style = {'float':'left'})),
				dcc.Input(id="ddInputFileDirectory", type="text", placeholder=defaultDirectory,style={'width':'400px'}, debounce=True),
				html.Button("Refresh", id='refreshButton',style = {'float':'left'}, n_clicks=0),
                dcc.Dropdown(id='ddInputFilesDirectoryDropdown',style = {'float':'left','width':'200px'}),
                html.Button("Update", id='updateButton',style = {'float':'left'}, n_clicks=0),
            ]
        ),
        html.Div(
            id='mainTextDisplay',
            className = 'selectorDiv',
            children = [
                html.Div("", className ='textDiv', id='totalPercentUsedOutput'),
                html.Div("", className ='textDiv', id='totalPercentUsedPerDayOutput'),
            ]
        ),
        #html.H1("", id='efficiencyOutput'),
		html.Div(
            id='timeTextDisplay',
            className = 'selectorDiv',
            children = [
                html.Div("Timezone: " + str(timeZone), className = 'textDiv', style = {'display':'none'}, id='timeZoneOutput'),
                html.Div("", className = 'textDiv', id='timestampRangeSliderFeedBackOutput'),
            ]
        ),
        dcc.RangeSlider(id='ddInputTimestampRangeSlider'),
        dcc.Graph(id='ddOutputMainGraph',style={'height':'80vh'},),
        dcc.Slider(id='ddInputAverageDaysSlider',min=1,max=7,step=1,value=3,
			marks=generateMarks([1,2,3,4,5,6,7]),
		),
        dcc.Graph(id='ddOutputDayAverageGraph',style={'height':'80vh'},),
    ]
)

@app.callback(
    [
		ddOutput('ddInputFilesDirectoryDropdown', 'options'),
    ],
    [
		ddInput('ddInputFileDirectory', 'value'),
		ddInput('refreshButton', 'n_clicks'),
    ]
)
def loadFileList(dir, btn):
    global defaultDirectory
    global fileDirectory
    if(dir is None or dir==''):
        dir = defaultDirectory
    
    fileDirectory = dir
    try:
        fileList = [ os.path.basename(os.path.normpath(f.path)) for f in os.scandir(fileDirectory) if f.is_dir() ]
    except FileNotFoundError:
        fileDirectory = defaultDirectory
        fileList = [ os.path.basename(os.path.normpath(f.path)) for f in os.scandir(fileDirectory) if f.is_dir() ]
    dashFileList = generateDropdownList(fileList)
    return [dashFileList]

	
############### efficiency (doesnt work)
# @app.callback(
    # [
		# ddOutput('efficiencyOutput', 'children'),
    # ],
    # [
		# ddInput('ddInputFilesDirectoryDropdown','value'),
    # ]
# )
# def calculateEfficiency(folder):
    # if(folder == '' or folder is None):
        # return ['']
    # columns = ['time','capacity','current','voltage','temp']
    # x = File_Reader(fileDirectory,folder)
    # fileNames = File_Reader.getFileNames(os.path.join(fileDirectory, folder))
    # masterDf = pd.DataFrame(columns = columns)
    # for fileName in fileNames:
        # fileName = os.path.splitext(fileName)[0]
        # df = x.getDf(fileName)
        # startTime = datetime.datetime.strptime(fileName,'%b %d %Y %H-%M-%S')
        # df['Time'] = [timeToInt(x,':') for x in df['Time']]
        # df['Time'] = [startTime + datetime.timedelta(seconds = x) for x in df['Time']]
        # df['Time'] = [x.replace(tzinfo=timeZone) for x in df['Time']]
        # df.columns = columns
        # timeList = df['time'].values.tolist()
        # currentList = df['current'].values.tolist()
        # s=0
        # t=0
        # for i in range(len(df)-1):
            # diff = (timeList[i+1]-timeList[i])/1000000000/3600
            # charge = currentList[i+1]*diff
            # s=s+charge
            # t=t+diff
        # delta = (df.iloc[len(df)-1]['capacity']-df.iloc[0]['capacity'])*4300/100
        # print(fileName + '  ' + str((s)/1) + '    ' + str(delta/1))
    # return ['']

@app.callback(
    [
		ddOutput('ddInputTimestampRangeSlider', 'min'),
		ddOutput('ddInputTimestampRangeSlider', 'max'),
		ddOutput('ddInputTimestampRangeSlider', 'step'),
		ddOutput('ddInputTimestampRangeSlider', 'value'),
		ddOutput('ddInputTimestampRangeSlider', 'marks'),
    ],
    [
		ddInput('ddInputFilesDirectoryDropdown','value'),
		ddInput('updateButton', 'n_clicks'),
    ]
)
def loadFile(folder, btn):

    global fileReader
    if(fileReader == '' or folder == '' or folder is None):
        fileReader = None
        return [0,1,1,[0,1],{}]
    global timeZone
    columns = ['time','capacity','current','voltage','temp']
    fileReader = File_Reader(fileDirectory,folder)
    fileNames = File_Reader.getFileNames(os.path.join(fileDirectory, folder))
    masterDf = pd.DataFrame(columns = columns)
    
    for fileName in fileNames:
        fileName = os.path.splitext(fileName)[0]
        df = fileReader.getDf(fileName)
        startTime = datetime.datetime.strptime(fileName,'%b %d %Y %H-%M-%S')
        df['Time'] = [timeToInt(x,':') for x in df['Time']]
        df['Time'] = [startTime + datetime.timedelta(seconds = x) for x in df['Time']]
        df['Time'] = [x.replace(tzinfo=timeZone) for x in df['Time']]
        df.columns = columns
        masterDf = masterDf.append(df)
    masterDf = masterDf.sort_values(by=['time'])
    fileReader.setProperty('masterDf', masterDf)
    minTimestamp = min(masterDf['time']).timestamp()
    maxTimestamp = max(masterDf['time']).timestamp()
    dates = dateRange(min(masterDf['time']), max(masterDf['time']))
    dates = [x.replace(hour=0,minute=0,second=0,microsecond=0) for x in dates]
    fileReader.setProperty('dates', dates)
    dates = {int(x.timestamp()):x.strftime("%d/%m") for x in dates}
    datesDict = generateMarks(dates)
    return [minTimestamp, maxTimestamp, 1, [minTimestamp, maxTimestamp], datesDict]

@app.callback(
	[
		ddOutput('timestampRangeSliderFeedBackOutput', 'children'),
	],
	[
		ddInput('ddInputTimestampRangeSlider', 'value'),
	]
)
def timestampRangeSliderFeedBack(val):
    minDate = datetime.datetime.fromtimestamp(val[0])
    maxDate = datetime.datetime.fromtimestamp(val[1])
    ret = minDate.strftime("%d/%m/%Y, %H:%M:%S") + ' to ' + maxDate.strftime("%d/%m/%Y, %H:%M:%S")
    return [ret]
    
@app.callback(
	[
		ddOutput('ddOutputMainGraph', 'figure'),
		ddOutput('totalPercentUsedOutput', 'children'),
		ddOutput('totalPercentUsedPerDayOutput', 'children'),
	],
	[
		ddInput('ddInputTimestampRangeSlider', 'value'),
	]
)
def generator(val):
    
    global fileReader
    if(fileReader is None):
        return [{'data': [],'layout': {}},"",""]
    masterDf = fileReader.getProperty('masterDf')
    global timeZone
    if(masterDf is None):
        return [{'data': [],'layout': {}},"",""]
    
    minDate = datetime.datetime.fromtimestamp(val[0]).replace(tzinfo=timeZone)
    maxDate = datetime.datetime.fromtimestamp(val[1]).replace(tzinfo=timeZone)
    
    subDf = masterDf.loc[(masterDf['time'] > minDate) & (masterDf['time'] <= maxDate)]
    noOfDays = (max(subDf['time']).timestamp()-min(subDf['time']).timestamp())/86400
    
    capacityList = subDf['capacity'].values.tolist()
    #print(capacityList)
    capacityRetString = 'Total used: ' + str(calculateRunningDecrease(capacityList)) + '%'
    capacityPerDayRetString = 'Per day: ' + str(round(calculateRunningDecrease(capacityList)/noOfDays,2)) + '%'
    return [{
        'data': [
            {'x': subDf['time'], 'y': subDf['capacity'], 'type': 'line', 'name': 'Capacity'},
            {'x': subDf['time'], 'y': subDf['voltage'], 'type': 'line', 'name': 'Voltage'},
            {'x': subDf['time'], 'y': subDf['current'], 'type': 'line', 'name': 'Current'},
            {'x': subDf['time'], 'y': subDf['temp'], 'type': 'line', 'name': 'Temperature'},
        ],
        'layout': {
            'title': 'All'
        }
    },
    capacityRetString,
    capacityPerDayRetString
    ]

@app.callback(
	[
		ddOutput('ddOutputDayAverageGraph', 'figure'),
	],
	[
		ddInput('ddInputAverageDaysSlider', 'value'),
		ddInput('totalPercentUsedOutput','children'),
	],
)
def avgGenerator(val, trigger):
    
    global fileReader
    if(fileReader is None or trigger is None or trigger == ''):
        return [{'data': [],'layout': {}}]
    masterDf = fileReader.getProperty('masterDf')
    global timeZone
    if(masterDf is None):
        return [{'data': [],'layout': {}}]
    xList = []
    yList = []
    minDate = min(masterDf['time']).replace(hour=0,minute=0,second=0,microsecond=0).replace(tzinfo=timeZone)
    maxDate = max(masterDf['time']).replace(hour=0,minute=0,second=0,microsecond=0).replace(tzinfo=timeZone)
    curDate = minDate
    while True:
        one = curDate
        two = curDate + datetime.timedelta(days=val)
        if(two>maxDate):
            break
        subDf = masterDf.loc[(masterDf['time'] > one) & (masterDf['time'] <= two)]
        
        capacityList = subDf['capacity'].values.tolist()
        noOfDays = (max(subDf['time']).timestamp()-min(subDf['time']).timestamp())/86400
        avg = round(calculateRunningDecrease(capacityList)/noOfDays,2)
        
        xList.append(curDate)
        yList.append(avg)
        
        curDate = curDate + datetime.timedelta(days=1)
    return [{
        'data': [
            {'x': xList, 'y': yList, 'type': 'line', 'name': 'Capacity'},
        ],
        'layout': {
            'title': str(val) + ' Day Average'
        }
    }]
if __name__ == '__main__':
    app.run_server(debug=True)
    