import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
pd.set_option("display.precision", 0)

def fixLeapYear(dates,donations):
    isNotLeapYearDate = ~(dates=='02-29')
    return dates[isNotLeapYearDate],donations[isNotLeapYearDate]

hvr_tmpl = '<b>Donasjonsmenge:</b> %{x} NOK<br><b>Prosent:</b> %{y:.2f}%<extra></extra>'

df = pd.read_csv('donations-effekt.csv', delimiter=";", parse_dates=['timestamp_confirmed'])
df = df.sort_values(by='timestamp_confirmed')
df.index = pd.to_datetime(df['timestamp_confirmed'])
#df['recurring'] = [dNum[np.where(unique_Donor_ID==donor_ID)[0][0]]>1 for donor_ID in full_df['Donor_ID']]['Num_dons_ID'] =

# Filter out recurring donations
ID_num_count = df['Donor_ID'].value_counts()
recurring_IDs = [ind for ind,val in zip(ID_num_count.index, ID_num_count.values) if val>1]
df_reccuring = df.loc[df['Donor_ID'].isin(recurring_IDs)]

#Get monthly donations for all, and recurring donations
MDs = pd.DataFrame() #monthly donations
MDs['sum_confirmed'] = df['sum_confirmed'].resample('M').sum() #Resample by day
MDs['date_name'] = [ts.month_name()[:3] + ' ' + str(ts.year) for ts in MDs.index]
MDs['timestamp'] = MDs.index
MDs.index = [i for i in range(0,len(MDs))]

MDs_reccuring = pd.DataFrame() #monthly donations
MDs_reccuring['sum_confirmed'] = df_reccuring['sum_confirmed'].resample('M').sum() #Resample by day
MDs_reccuring['date_name'] = [ts.month_name()[:3] + ' ' + str(ts.year) for ts in MDs_reccuring.index]
MDs_reccuring['timestamp'] = MDs_reccuring.index
MDs_reccuring.index = [i for i in range(0,len(MDs_reccuring))]

# Get yearly donations and sort by year
DDs = pd.DataFrame() #daily donations
DDs['value'] = df['sum_confirmed'].resample('D').sum() #Resample by day
DDs['y-m-d'] = pd.to_datetime(DDs.index)
DDs['y']= DDs['y-m-d'].dt.strftime('%Y')
DDs['m-d'] = DDs['y-m-d'].dt.strftime('%m') + "-" + DDs['y-m-d'].dt.strftime('%d')

year_strings = [str(yr) for yr in range(2019,2023)]
dates_by_year     = [ DDs.loc[DDs['y']==year_str,'m-d'].to_numpy() for year_str in year_strings]
donations_by_year = [ DDs.loc[DDs['y']==year_str,'value'].to_numpy() for year_str in year_strings]
dates_by_year,donations_by_year = zip(*[ fixLeapYear(dts,dons) for dts,dons in zip(dates_by_year,donations_by_year) ])

yMax = max([sum(dons) for dons in donations_by_year])

def get_df_subset_by_month(month_index_range, month_df, full_df):
    all_dates = month_df.iloc[month_index_range[0]:month_index_range[1]]
    date_1 = all_dates['timestamp'].iloc[0]
    date_2 = all_dates['timestamp'].iloc[-1]
    df_subset = full_df.loc[(full_df.index>date_1)&(full_df.index<date_2)]
    return df_subset

def get_histogram(month_index_range, exclude_otd, n_bins=50):
    month_df = MDs_reccuring if exclude_otd else MDs
    full_df = df_reccuring if exclude_otd else df
    df_subset = get_df_subset_by_month(month_index_range, month_df=month_df, full_df=full_df)
    donations = df_subset['sum_confirmed'].to_numpy()
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=donations, nbinsx=n_bins, marker_color='black', histnorm='percent', hovertemplate=hvr_tmpl)
    )
    #horline_values = [10**n for n in range(-1,3)]
    major_ticks = np.logspace(-3,3,7)
    all_ticks = np.outer(major_ticks,np.arange(1,10,1)).flatten()
    horline_values_major = [0.01, 0.1, 1.0, 10.0, 100.0]
    [fig.add_hline(y=hlv, line_color='#fafafa', line_width=0.5) for hlv in horline_values_major]
    fig.update_layout(
        xaxis = dict(title=dict(text='Donasjonsmenge [NOK]'), fixedrange=True),
        yaxis = dict(
            type='log',
            title=dict(text='Prosent av donasjoner [%]'),
            fixedrange=True, #Disabling zoom
            #gridcolor='black',
            ticks = 'outside',
            tickvals = all_ticks,
            ticktext = [val if val in major_ticks else '' for val in all_ticks],
            range = [-3,2],
            showgrid=False
            #minor = dict(ticks='outside', dtick=0, tick0=-2, showgrid=True)
            ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        bargap=0.05
    )
    return fig

def get_barplot(month_index_range):
    flip_single = True #Flip single donations
    df_subset = get_df_subset_by_month(month_index_range)
    df_recurring, df_single = pd.DataFrame(), pd.DataFrame()
    df_recurring['recurring'] = MDs['sum_confirmed'].apply(lambda x: x/1000)
    df_recurring.index = MDs['timestamp']
    if flip_single:
        df_single['single'] = MDs.loc[MDs.index.get_level_values(0)==False]['sum_confirmed'].apply(lambda x: -x/1000)
    else:
        df_single['single'] = MDs.loc[MDs.index.get_level_values(0)==False]['sum_confirmed'].apply(lambda x: -x/1000)
    #df_recurring.index = df_recurring.index.droplevel(0)
    #df_single.index = df_single.index.droplevel(0)

    step = 400
    #y_max = int(math.ceil((max(df_single['single'].max(),df_recurring['recurring'].max())*1.05)/step)*step) #round max value to nearest hundred
    bar_w= 26 if flip_single else 14
    bar_w_dt = timedelta(days=bar_w)
    fig = go.Figure()
    if flip_single:
        fig.add_trace(
            go.Bar(x=df_recurring.index-bar_w_dt/2, y=df_recurring['recurring'], marker_color='black')#, width=bar_w)#, color='k',label='Recurring')
        )
        # fig.add_trace(
        #     go.Bar(x=df_single.index-bar_w_dt/2, y=df_single['single'], marker_color='grey')
        # )
        #ax.bar(x=df_single.index-bar_w_dt/2, height=df_single['single'], width=bar_w, color='grey',label='Single')
    # else:
    #     ax.bar(x=df_recurring.index-bar_w_dt/2,height=df_recurring['recurring'], width=bar_w, color='k',label='Recurring')#Shift left by half
    #     ax.bar(x=df_single.index-bar_w_dt*3/2,height=df_single['single'], width=bar_w, color='grey',label='Single')#Shift left by 3/2
    # ax.bar(x=df_recurring.index,height=df_recurring['recurring'], width=bar_w, color='k',label='Recurring')
    # ax.bar(x=df_single.index,height=df_single['single'], width=bar_w, color='grey',label='Single')
    # ax.set_ylim(bottom=-y_max, top=y_max)
    # ax.set_yticks([x for x in range(-y_max,y_max+step,step)])
    # ax.xaxis.set_major_formatter( mdates.DateFormatter('%b-%y') )
    # ax.yaxis.set_major_formatter(FormatStrFormatter('% .0f'))
    # [plt.axhline(y,color='white',linewidth=0.5) for y in ax.get_yticks()]
    # #plt.axhline(0,color='grey',linewidth=0.5)
    # plt.ylabel('Donations [kNok]')
    # ax.yaxis.tick_right()
    # ax.yaxis.set_label_position("right")
    # ax.set_yticklabels([f'{abs(x)}' for x in ax.get_yticks()])
    # #ax.yaxis.get_major_ticks()
    # for key, spine in ax.spines.items():
    #     spine.set_visible(False)
    # plt.tight_layout(True)
    #[fig.add_hline(y=y_tick) for y_tick in 
    fig.update_layout(
        dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(
                showgrid=True,
                gridcolor='White'
                )
        )
    )
    #fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink')
    return fig

yearly_dons_hovertemplate = '<b>Dato:</b> %{x}<br><b>Verdi:</b> %{y:,.0f} kr'
def get_yearly_donations_plot():
    fig = go.Figure()
    for dates, dons, year_str in zip(dates_by_year, donations_by_year, year_strings):
        dates = ['1970-'+d for d in dates]
        color = 'black' if year_str=='2022' else 'grey'
        dons_cumsum = np.cumsum(dons)
        fig.add_trace(
            go.Scatter(x=dates, y=dons_cumsum, marker_color=color, name=year_str, xhoverformat="%d %b", hovertemplate=yearly_dons_hovertemplate)
        )
        fig.add_trace(
            go.Scatter(x=[dates[-1]], y=[dons_cumsum[-1]], name=year_str, marker_color=color, mode='markers', xhoverformat="%d %b", hovertemplate=yearly_dons_hovertemplate)
        )
        fig.add_annotation(
            x=dates[-1], y=dons_cumsum[-1]+0.03*yMax, text=year_str, showarrow=False, font=dict(color=color)
        )
    fig.update_layout(
        xaxis = dict(
            tickformat = '%b',
            dtick="M1", 
            ticklabelmode="period", 
            ticks='outside', 
            #tickvals=[f'1970-{mon}-01' for mon in range(1,13)],
            #tickvals = pd.date_range('1970-01', '1970-12', freq='MS'),
            showgrid=False,
            fixedrange=True, #Disabling zoom
        ),
        yaxis = dict(gridcolor='lightgrey', fixedrange=True), #Disabling zoom),
        hoverlabel=dict(bgcolor="#fafafa"),
        showlegend = False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
    )
        #plt.plot(dates[-1], dons_cumsum[-1], color=color_, marker='.', markersize=10)
        #txtBox = plt.text(dates[-1], dons_cumsum[-1] + 0.02*yMax, year_str, va='bottom',ha='center')
    return fig
    
def histogram_timing():
    fig = get_histogram([0,5])

# TIMING CODE #
time_code = False
sort_type = 'cumtime'
if time_code:
    import cProfile
    import pstats
    from pstats import SortKey
    # profiler = cProfile.Profile()
    # profiler.runcall(histogram_timing)
    # profiler.print_stats()
    cProfile.run('histogram_timing()','output.dat')
    with open('output.txt','w') as f:
        p=pstats.Stats('output.dat', stream=f)
        p.sort_stats(sort_type).print_stats()

