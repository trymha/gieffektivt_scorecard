import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
pd.set_option("display.precision", 0)

df = pd.read_csv('donations-effekt.csv', delimiter=";", parse_dates=['timestamp_confirmed'])
df = df.sort_values(by='timestamp_confirmed')
df.index = pd.to_datetime(df['timestamp_confirmed'])

MDs = pd.DataFrame() #monthly donations
MDs['sum_confirmed'] = df['sum_confirmed'].resample('M').sum() #Resample by day
MDs['date_name'] = [ts.month_name()[:3] + ' ' + str(ts.year) for ts in MDs.index]
MDs['timestamp'] = MDs.index
MDs.index = [i for i in range(0,len(MDs))]
#df['timestamp_confirmed'] = pd.to_datetime(df['timestamp_confirmed'])

cumulative_donations = np.cumsum( df['sum_confirmed'].to_numpy() )
donations = df['sum_confirmed']
timestamps = pd.to_datetime(df['timestamp_confirmed'])

hvr_tmpl = '<b>Donasjonsmenge:</b> %{x} NOK<br><b>Prosent:</b> %{y:.2f}%<extra></extra>'

def get_df_subset_by_month(month_index_range):
    all_dates = MDs.iloc[month_index_range[0]:month_index_range[1]]
    date_1 = all_dates['timestamp'].iloc[0]
    date_2 = all_dates['timestamp'].iloc[-1]
    df_subset = df.loc[(df.index>date_1)&(df.index<date_2)]
    return df_subset

def get_histogram(month_index_range, n_bins=100):
    df_subset = get_df_subset_by_month(month_index_range)
    donations = df_subset['sum_confirmed'].to_numpy()
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(x=donations, nbinsx=n_bins, marker_color='black', histnorm='percent', hovertemplate=hvr_tmpl)
    )
    fig.update_layout(
        xaxis = dict(title=dict(text='Donasjonsmenge [NOK]'), fixedrange=True),
        yaxis = dict(type='log', title=dict(text='Prosent av donasjoner [%]'), fixedrange=True),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
