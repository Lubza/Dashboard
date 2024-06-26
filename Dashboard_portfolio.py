from pandas_datareader import data as pdr
from datetime import datetime
import numpy as np # linear algebra
#import matplotlib.pyplot as plt
import yfinance as yf
#Data viz
import plotly.graph_objs as go
yf.pdr_override()

import pandas as pd
import plotly.express as px
import streamlit as st

#emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

st.set_page_config(page_title="Portfolio overview",
                    page_icon=":bar_chart:",
                    layout="wide"
)

#adress = r'C:\Users\Lubos\Dropbox\My PC (Lubos-PC1)\Desktop\python\data\Portfolio_dataset_1122.csv'
#adress = r'https://raw.githubusercontent.com/Lubza/My-overview-app/master/Portfolio_dataset_1122.csv'
adress = r'data/Portfolio_dataset_0424.csv'

df = pd.read_csv(adress, engine='python')

#df = get_data()

### 1. Activity log ###

adress_log = r'Activity logs/Activity log 02292024.csv'

log = pd.read_csv(adress_log, engine='python')

    # DataFrame
data = log['Date']
log_date = pd.DataFrame(data)

    # Define function to convert date format
def convert_date(date_str):
        original_date = pd.to_datetime(date_str, format='%m/%d/%Y')
        return original_date.strftime('%Y-%m-%d')

    # Apply function to DataFrame column
log['Date_converted'] = log_date['Date'].apply(convert_date)
log['Amount'] = log['Price'] * log['Qty']

### 1.1 Pozicie ###
#### 1.1.1. all pozicie
pozicie = pd.pivot_table(log,
                         values=['Qty', 'Amount'],
                         index=['Ticker'],
                         #columns=['Date'],
                         aggfunc="sum").fillna(0)
pozicie = pozicie.reset_index(drop=False)
log = log.reset_index(drop=False)

#### 1.1.2 select pozicie
Tickers = ['VOD'] # input for ticker
bot = ['BOT'] # bought
sld = ['SLD'] # sold
   
# selecting rows based on condition 
#Select_pozicie = pozicie[pozicie['Ticker'].isin(Tickers)]

Select_ticker = log[log['Ticker'].isin(Tickers)]

Select_ticker_bot = Select_ticker[Select_ticker['Action'].isin(bot)]
Select_ticker_sld = Select_ticker[Select_ticker['Action'].isin(sld)]

init_costbase_pozicie = Select_ticker_bot.drop(['index'], axis=1) # calculate initial cost_base of selected position 
init_costbase_pozicie_sum = init_costbase_pozicie['Amount'].sum()

sold_pozicie = Select_ticker_sld.drop(['index'], axis=1) # calculate sold position in $
sold_pozicie_sum = sold_pozicie['Amount'].sum()

sum_select_ticker = Select_ticker['Amount'].sum() # calculate sum sold and bought selected position

if sum_select_ticker > 0:                         # ak je suma predanych a nakupenych kladna tak toto je nova cost base a ak je zaporna tak je to realized
   current_costbase_ticker = sum_select_ticker
else:
   realized_ticker = sum_select_ticker * -1

#### 1.1.3 all closed positions 
Closed_positions_df = pozicie[pozicie['Qty'] == 0]
closed_positions_sum = Closed_positions_df['Amount'].sum()

#### 1.1.4 all live positions
zive_pozicie_df = pozicie[pozicie['Qty'] != 0]

#### 1.1.5. all option positions
mask = (pozicie['Ticker'].str.len() > 6) & (pozicie['Ticker'] != 'NET.UN VENTURE')
pozicie_opcie_df = pozicie.loc[mask]

##### 1.1.5.1. Live option positions
live_positions_options_df = pozicie_opcie_df[pozicie_opcie_df['Qty'] != 0]

##### 1.1.5.2. closed option positions
closed_positions_options_df = pozicie_opcie_df[pozicie_opcie_df['Qty'] == 0]

#### 1.1.6. all stock positions
mask = (pozicie['Ticker'].str.len() < 7) & (pozicie['Ticker'] != 'NET.UN VENTURE')
pozicie_akcie_df = pozicie.loc[mask]



#---- SIDEBAR -----
st.sidebar.title('Navigation') # novy riadok pre multipage testing
st.sidebar.header("Please Filter Here:")

PSize = st.sidebar.multiselect(
    "Select the position size:",
    options=df["Position_Size"].unique(),
    default=df["Position_Size"].unique()
)


sector = st.sidebar.multiselect(
    "Select the Sector:",
    options=df["Sector"].unique(),
    default=df["Sector"].unique()
)

industry = st.sidebar.multiselect(
    "Select the Industry:",
    options=df["Industry"].unique(),
    default=df["Industry"].unique()
)

REIT_sector = st.sidebar.multiselect(
    "Select the REIT Sector:",
    options=df["REIT sector"].unique(),
    default=df["REIT sector"].unique()
)

ccy = st.sidebar.multiselect(
    "Select the currency:",
    options=df["CCY"].unique(),
    default=df["CCY"].unique()
)

df_selection = df.query(
    "Position_Size == @PSize & Sector == @sector & Industry == @industry & CCY == @ccy"
)


#-----MAINPAGE-----
st.title(":bar_chart: Portfolio Overview as of April 2024")
st.markdown('##')

#TOP KPI's
Total_net_liq = round(df_selection['% of Net Liq'].sum(), 2)
Total_MV = round(df_selection['Market Value'].sum(), 1)
Account_balance = round(((100/Total_net_liq)*Total_MV), 2)
Total_unrlzd = round(df_selection['Unrealized P&L'].sum(), 2)

#YTD portfolio performance
Portfolio_YE23 =  74849.6
deposits = 0
YTD_performance = round((((Account_balance - deposits - Portfolio_YE23) / Portfolio_YE23) * 100),2)

#Dividend calculation
Divi = df['Dividends']
Shares = df['Position']
Total_div_year = round((Divi * Shares).sum(),2)
div_yield = round(((Total_div_year/Total_MV) * 100),2)

#Calculating year-to-date price return of SPY
SPY_YE_2023 = pdr.DataReader('SPY','2023-12-29','2023-12-30')['Adj Close']
SPY_YE_2023 = SPY_YE_2023.sum()

SPY_mtd_2024 = pdr.DataReader('SPY','2024-02-29','2024-03-01')['Adj Close']
SPY_mtd_2024 = SPY_mtd_2024.sum()

SPY_YTD_return = round((((SPY_mtd_2024 - SPY_YE_2023) / SPY_YE_2023 ) * 100),2)

#Calculating year-to-date price return of VNQ
VNQ_YE_2023 = pdr.DataReader('VNQ','2023-12-29','2023-12-30')['Adj Close']
VNQ_YE_2023 = VNQ_YE_2023.sum()

VNQ_mtd_2024 = pdr.DataReader('VNQ','2024-03-28','2024-04-01')['Adj Close']
VNQ_mtd_2024 = VNQ_mtd_2024.sum()

VNQ_YTD_return = round((((VNQ_mtd_2024 - VNQ_YE_2023) / VNQ_YE_2023 ) * 100),2)

#since inception performance
#since_inception_performance = round((( df['Unrealized P&L'].sum() / df['Cost Basis'].sum() )*100),2)

### new feature - trades





left_column, middle_column1, middle_column2, right_column = st.columns(4)
with left_column:
    st.subheader("Exposure:")
    st.subheader(f"{Total_net_liq:,} %")
with middle_column1:
    st.subheader("Portfolio Market Value:")
    st.subheader(f"{Total_MV:,} USD")
with middle_column2:
    st.subheader("Balance:")
    st.subheader(f"{Account_balance:,} USD ")
with right_column:
    st.subheader("Dividend yield:")
    st.subheader(f"{div_yield:,} %      or      {Total_div_year:,} USD")
    

st.markdown("---")

left_column, middle_column1, middle_column2, right_column = st.columns(4)
with left_column:
    st.subheader("SPY YTD:")
    st.subheader(f"{SPY_YTD_return:,} %")
with middle_column1:
    st.subheader("VNQ YTD:")
    st.subheader(f"{VNQ_YTD_return:,} %")
with middle_column2:
    st.subheader("Unrealized PnL:")
    st.subheader(f"{Total_unrlzd:,} USD ")
with right_column:
    st.subheader("YTD:")    
    st.subheader(f"{YTD_performance:,} %")

st.markdown("---")

#st.dataframe(df_selection)
#st.dataframe(df)

col1, col2, col3 = st.columns(3)

# Expected Dividend by month

Expected_dividend_by_month = (

df_selection.groupby(by=["Month"]).sum()[["Next_div_receiveable"]].sort_values(by="Next_div_receiveable")

)

fig_div = px.bar(
        Expected_dividend_by_month,
        y = "Next_div_receiveable",
        x = Expected_dividend_by_month.index,
        orientation="v",
        title="<b>Expected Dividend by month</b>",
        color_discrete_sequence=["#0083B8"] * len(Expected_dividend_by_month),
        template="plotly_white"
)

col1.plotly_chart(fig_div)

# Portfolio by currency

fig_ccy = px.pie(
        df,
        values='Market Value',
        names='CCY',
        title="<b>Portfolio by currency</b>",
)

col2.plotly_chart(fig_ccy)

#Portfolio by Industry

fig_industry = px.pie(
        df,
        values='Market Value',
        names='Industry',
        title='<b>Portfolio by industry</b>'
        
)

col3.plotly_chart(fig_industry)

#PnL By ticker

PnL_by_ticker_pct = (

df_selection.groupby(by=["Financial Instrument"]).sum()[["Unrealized PnL"]].sort_values(by="Unrealized PnL")

)

fig_PnL_by_ticker_pct = px.bar(
        PnL_by_ticker_pct,
        y = 'Unrealized PnL',
        x = PnL_by_ticker_pct.index,
        orientation='v',
        title='<b>Unrealized PnL by ticker %</b>',
        color_discrete_sequence=['#00b7b7'] * len(PnL_by_ticker_pct),
        template='plotly_white'
)

col1.plotly_chart(fig_PnL_by_ticker_pct)

#Unrealized gain/loss by sector

Unrealized_gl_by_sector = (

df_selection.groupby(by=["Industry"]).sum()[["Unrealized P&L"]].sort_values(by="Unrealized P&L")

)

fig_industry_unrlzd = px.bar(
        Unrealized_gl_by_sector,
        y = "Unrealized P&L",
        x = Unrealized_gl_by_sector.index,
        orientation="v",
        title="<b>Unrealized P/L by sector</b>",
        color_discrete_sequence=["#90b800"] * len(Unrealized_gl_by_sector),
        template="plotly_white"
)

col2.plotly_chart(fig_industry_unrlzd)

#PnL By ticker %

PnL_by_ticker = (

df_selection.groupby(by=["Financial Instrument"]).sum()[["Unrealized P&L"]].sort_values(by="Unrealized P&L")

)

fig_PnL_by_ticker = px.bar(
        PnL_by_ticker,
        y = 'Unrealized P&L',
        x = PnL_by_ticker.index,
        orientation='v',
        title='<b>PnL by ticker</b>',
        color_discrete_sequence=['#b76500'] * len(PnL_by_ticker),
        template='plotly_white'
)

col3.plotly_chart(fig_PnL_by_ticker)

#Ticker by size
ticker_by_size = (

df_selection.groupby(by=["Financial Instrument"]).sum()[["% of Net Liq"]].sort_values(by="% of Net Liq")

)

fig_ticker_by_size = px.bar(
        ticker_by_size,
        y = '% of Net Liq',
        x = ticker_by_size.index,
        orientation='v',
        title='<b>Position by size</b>',
        color_discrete_sequence=['#f56cde'] * len(ticker_by_size),
        template='plotly_white'
)

col1.plotly_chart(fig_ticker_by_size)
#

#YTD price return chart
YtD_price_return = (

df_selection.groupby(by=["Financial Instrument"]).sum()[["YtD price return"]].sort_values(by="YtD price return")

)

fig_YtD_price_return = px.bar(
        YtD_price_return,
        y = 'YtD price return',
        x = YtD_price_return.index,
        orientation='v',
        title='<b>Year to date price return</b>',
        color_discrete_sequence=['#2dbaed'] * len(YtD_price_return),
        template='plotly_white'
)

col2.plotly_chart(fig_YtD_price_return)
#

#YTD price return chart
MtD_price_return = (

df_selection.groupby(by=["Financial Instrument"]).sum()[["MtD price return"]].sort_values(by="MtD price return")

)

fig_MtD_price_return = px.bar(
        MtD_price_return,
        y = 'MtD price return',
        x = MtD_price_return.index,
        orientation='v',
        title='<b>Month to date price return</b>',
        color_discrete_sequence=['#ed772d'] * len(MtD_price_return),
        template='plotly_white'
)

col3.plotly_chart(fig_MtD_price_return)
#

st.markdown("---")
st.title(":bar_chart: Activity log")

#col4= st.columns(1)

st.dataframe(log)

st.markdown("---")
st.title(":bar_chart: VNQ share price evolution last 5 years")

#Loading stock data
data = yf.download(tickers='VNQ', period='5y', interval='1d')

#VNQ chart
fig_VNQ = go.Figure()
fig_VNQ.add_trace(go.Scatter(x=data.index, y=data["Close"]))

#Add titles
fig_VNQ.update_layout(yaxis_title='Stock Price (USD per Shares)')

#fig_VNQ.show()

st.plotly_chart(fig_VNQ)