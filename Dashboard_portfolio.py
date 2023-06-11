from pandas_datareader import data as pdr
from datetime import datetime
import yfinance as yf
#Data viz
import plotly.graph_objs as go
yf.pdr_override()

import pandas as pd
import plotly.express as px
import streamlit as st

#@st.cache
#def get_data():
    #df = pd.read_csv(r'data\Portfolio_dataset_0423.csv)

    #return df

#emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

st.set_page_config(page_title="Portfolio overview",
                    page_icon=":bar_chart:",
                    layout="wide"
)

#adress = r'C:\Users\Lubos\Dropbox\My PC (Lubos-PC1)\Desktop\python\data\Portfolio_dataset_1122.csv'
#adress = r'https://raw.githubusercontent.com/Lubza/My-overview-app/master/Portfolio_dataset_1122.csv'
adress = r'data/Portfolio_dataset_0523.csv'

df = pd.read_csv(adress, engine='python')

#df = get_data()

adress_log = r'Activity logs/Activity log 05312023.csv'

df_log = pd.read_csv(adress_log, engine='python')

#del df_log['Unnamed: 7']
#del df_log['Unnamed: 8']

df_log['Price adj'] = df_log["Price"].str.replace("$","")
df_log['Price adj'] = df_log['Price adj'].astype(float)
df_log['Amount'] = df_log['Price adj'] * df_log['Qty']

df_log['Date adj'] = pd.to_datetime(df_log['Date'])

df_log['Year'] = df_log['Date adj'].dt.year 
df_log['Month'] = df_log['Date adj'].dt.month

del df_log['Date adj']


#---- SIDEBAR -----
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
st.title(":bar_chart: Portfolio Overview as of May 2023")
st.markdown('##')

#TOP KPI's
Total_net_liq = round(df_selection['% of Net Liq'].sum(), 2)
Total_MV = round(df_selection['Market Value'].sum(), 1)
Account_balance = round(((100/Total_net_liq)*Total_MV), 2)
Total_unrlzd = round(df_selection['Unrealized P&L'].sum(), 2)

#Dividend calculation
Divi = df['Dividends']
Shares = df['Position']
Total_div_year = round((Divi * Shares).sum(),2)
div_yield = round(((Total_div_year/Total_MV) * 100),2)

#Calculating year-to-date price return of SPY
SPY_YE_2022 = pdr.DataReader('SPY','2022-12-30','2022-12-31')['Adj Close']
SPY_YE_2022 = SPY_YE_2022.sum()

SPY_mtd_2023 = pdr.DataReader('SPY','2023-05-31','2023-06-01')['Adj Close']
SPY_mtd_2023 = SPY_mtd_2023.sum()

SPY_YTD_return = round((((SPY_mtd_2023 - SPY_YE_2022) / SPY_YE_2022 ) * 100),2)

#Calculating year-to-date price return of VNQ
VNQ_YE_2022 = pdr.DataReader('VNQ','2022-12-30','2022-12-31')['Adj Close']
VNQ_YE_2022 = VNQ_YE_2022.sum()

VNQ_mtd_2023 = pdr.DataReader('VNQ','2023-05-31','2023-06-01')['Adj Close']
VNQ_mtd_2023 = VNQ_mtd_2023.sum()

VNQ_YTD_return = round((((VNQ_mtd_2023 - VNQ_YE_2022) / VNQ_YE_2022 ) * 100),2)

#since inception performance
since_inception_performance = round((( df['Unrealized P&L'].sum() / df['Cost Basis'].sum() )*100),2)



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
    st.subheader("since_inception_performance:")
    st.subheader(f"{since_inception_performance:,} % ")
with right_column:
    st.subheader("Unrealized:")
    st.subheader(f"{Total_unrlzd:,} USD")

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

st.markdown("---")
st.title(":bar_chart: Activity log")

#col4= st.columns(1)

st.dataframe(df_log)