from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
#from organization_plots import *
import histogram_plot as hp


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

month_marks = {i: ts.month_name()[:3] + ' ' + str(ts.year) for i,ts in enumerate(hp.MDs['timestamp'])}
showlabel_months = ['January','April','July','October']

time_options = ['Week','Year','Quarter','Month']
time_dd = dcc.Dropdown(id='time-dd',value=time_options[0],options=[{'label':to,'value':to} for to in time_options])

onetime_donations_switch = dbc.Switch(id='onetime-donations-switch',label='Eksluder enkeltdonasjoner', value=False)
month_slider = dcc.RangeSlider(
        id='month-slider', 
        #marks=month_marks,
        marks=None, 
        value=[0,len(month_marks)-1],
        step=1,
        min=0,
        max=len(month_marks)-1,
        allowCross= False,
        pushable=6, #Minimum 6 months range
        #vertical=True, verticalHeight=700,
        #tooltip={"placement": "bottom", "always_visible": True},
        #style={'padding':'0px 0px 0px 0px'}
        )

year_slider = dcc.RangeSlider(
        id='year-slider', 
        #marks=month_marks, 
        value=[2019,2021], step=1, min=2018, max=2022,
        marks=None,
        #vertical=True, verticalHeight=700,
        #tooltip={"placement": "bottom", "always_visible": True},
        )#className='rc-slider'),

histogram_graph = dcc.Graph(
    id='histogram-graph', 
    style={"width": "100%"}, 
    config={'displayModeBar': False} #Hide options for saving graph, zooming etc
)
bar_graph = dcc.Graph(id='bar-graph', style={"width": "100%"})
yearly_donations_graph = dcc.Graph(
    id='yearly-donations-graph', 
    figure=hp.get_yearly_donations_plot(),
    config={'displayModeBar': False}
)

#app.layout = html.Div([
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(onetime_donations_switch,  width='auto'),
        dbc.Col(html.Span(month_marks[0], id='from-month'), width='auto'),
        dbc.Col(month_slider, width=8, style={'padding':'0px 0px0px'}),
        dbc.Col(html.Span(month_marks[len(month_marks)-1], id='to-month'), width='auto'),
        #dbc.Col([dcc.RangeSlider(0, 20, marks=None, value=[5, 15])], style={'width':'30%'})
    ], align='center'), #style = {"height": "100%", 'background-color':'yellow'}), 
    dbc.Row(dbc.Col(histogram_graph)),
    html.Br(),
    html.Hr(),
    html.Br(),
    dbc.Row(dbc.Col(yearly_donations_graph)),
    ], style={'backgroundColor':'#fafafa'}
)

@app.callback(
    Output('histogram-graph','figure'),
    #Input('year-slider','value'),
    Input('month-slider','value'),
    Input('onetime-donations-switch','value'),
    prevent_inital_callback=True
)
def update_histogram(month_index_range, exclude_otd):
    #index_range = [(year - 2018)*12 for year in year_range]
    return hp.get_histogram(month_index_range, exclude_otd=exclude_otd)

# @app.callback(
#     Output('from-year','children'),
#     Output('to-year','children'),
#     Input('year-slider','value')
# )
# def update_year_text(year_range):
#     return str(year_range[0]), str(year_range[1])

# @app.callback(
#     Output('bar-graph','figure'),
#     Input('year-slider','value'),
#     prevent_inital_callback=True
# )
# def update_barplot(index_range):
#     return get_barplot(index_range)

# # profiler = cp.Profile()
# # profiler.runcall(histogram_timing)
# # profiler.print_stats()
# cProfile.run('histogram_timing()','timing.stats')
# stats = pstats.Stats('timing.stats')
# stats.print_stats()

if __name__ == '__main__':
    app.run_server(debug=True)
    