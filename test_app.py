from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
#from organization_plots import *
from histogram_plot import *

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#month_marks = {i: ts.month_name()[:3] + ' ' + str(ts.year) for i,ts in enumerate(timestamps)}
showlabel_months = ['January','April','July','October']
month_marks = {i: {
    'label':ts.month_name()[:3] + '\n' +  str(ts.year),
    'style': {'white-space':'nowrap','writing-mode': 'vertical-rl'}} for i,ts in enumerate(MDs['timestamp'])}
    #'style': {'white-space':'nowrap'}} for i,ts in enumerate(MDs['timestamp'])}
#month_marks = {i: '''a<br>a''' for i,ts in enumerate(MDs['timestamp'])}
time_options = ['Week','Year','Quarter','Month']
time_dd = dcc.Dropdown(id='time-dd',value=time_options[0],options=[{'label':to,'value':to} for to in time_options])

month_slider = dcc.RangeSlider(
        id='month-slider', 
        marks=month_marks, 
        value=[0,len(month_marks)-1], step=None, min=0, max=len(month_marks),
        allowCross= False, pushable=6, #Minimum 6 months range
        #vertical=True, verticalHeight=700,
        #tooltip={"placement": "bottom", "always_visible": True},
        className='slider'),

year_slider = dcc.RangeSlider(
        id='year-slider', 
        #marks=month_marks, 
        value=[2019,2021], step=1, min=2018, max=2022,
        marks=None,
        #vertical=True, verticalHeight=700,
        #tooltip={"placement": "bottom", "always_visible": True},
        )#className='rc-slider'),

histogram_graph = dcc.Graph(id='histogram-graph', style={"width": "100%"})
bar_graph = dcc.Graph(id='bar-graph', style={"width": "100%"})

app.layout = dbc.Container([
    #time_dd,
    #dcc.Slider(id='bins-slider', value=100, min=20, max=500, step=10, className='slider'),
    html.Br(),
    dbc.Row([
       # dbc.Col(histogram_graph, width={"size": 6},style = {'background-color':'cyan'}),
        #dbc.Col(bar_graph, width={"size": 6},style = {'background-color':'cyan'}),
        #dbc.Col([year_slider], style={'width':'30%'}),
        dbc.Col(html.Span('2019', id='from-year'), width='auto'),
        dbc.Col(year_slider, width=9),
        dbc.Col(html.Span('2021', id='to-year'), width='auto'),
        #dbc.Col([dcc.RangeSlider(0, 20, marks=None, value=[5, 15])], style={'width':'30%'})
    ]), #style = {"height": "100%", 'background-color':'yellow'}), 
    dbc.Row(dbc.Col(histogram_graph)),
    # dbc.Row(year_slider), 
    html.Br(),
    ], style={'backgroundColor':'#fafafa'}
)

@app.callback(
    Output('histogram-graph','figure'),
    Input('year-slider','value'),
    prevent_inital_callback=True
)
def update_histogram(year_range):
    index_range = [(year - 2018)*12 for year in year_range]
    return get_histogram(index_range)

@app.callback(
    Output('from-year','children'),
    Output('to-year','children'),
    Input('year-slider','value')
)
def update_year_text(year_range):
    return str(year_range[0]), str(year_range[1])

# @app.callback(
#     Output('bar-graph','figure'),
#     Input('year-slider','value'),
#     prevent_inital_callback=True
# )
# def update_barplot(index_range):
#     return get_barplot(index_range)

if __name__ == '__main__':
    app.run_server(debug=False)