import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache
def get_data(filename):
    df = pd.read_csv(filename)

    return df

#emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

st.set_page_config(page_title="Portfolio overview",
                    page_icon=":bar_chart:",
                    layout="wide"
)

#adress = r'C:\Users\Lubos\Dropbox\My PC (Lubos-PC1)\Desktop\python\data\Portfolio_dataset_1122.csv'
#adress = r'https://raw.githubusercontent.com/Lubza/My-overview-app/master/Portfolio_dataset_1122.csv'
#adress = r'data/Portfolio_dataset_1122.csv'

#df = pd.read_csv(adress, engine='python')

df = get_data(r'data\Portfolio_dataset_0423.csv')


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
    "Position_Size == @PSize & Sector == @sector & Industry == @industry"
)


#-----MAINPAGE-----
st.title(":bar_chart: Portfolio Overview as of April 2023")
st.markdown('##')

#TOP KPI's
Total_net_liq = round(df_selection['% of Net Liq'].sum(), 2)
Total_MV = round(df_selection['Market Value'].sum(), 1)
Account_balance = round(((100/Total_net_liq)*Total_MV), 2)

#Dividend calculation
Divi = df['Dividends']
Shares = df['Position']
Total_div_year = round((Divi * Shares).sum(),2)
div_yield = round(((Total_div_year/Total_MV) * 100),2)

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

#st.dataframe(df_selection)
#st.dataframe(df)

col1, col2 = st.columns(2)

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

st.plotly_chart(fig_industry)

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

st.plotly_chart(fig_industry_unrlzd)