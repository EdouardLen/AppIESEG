import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timezone
from matplotlib import style
import numpy as np
import matplotlib.pyplot as plt

# Fetch S&P 500 tickers from Wikipedia
@st.cache_data
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    table = pd.read_html(url)
    sp500 = table[0]  # First table contains the tickers
    return sp500['Symbol'].tolist()

# Function to convert timestamp to date format
def convert_timestamp_to_date(timestamp):
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d')
    except:
        return "N/A"

# Set up the tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Chart", "Financials", "Monte Carlo Analysis", "Statistics"])

# Sidebar for user inputs
st.sidebar.header("Stock Selection")
sp500_tickers = get_sp500_tickers()
selected_stock = st.sidebar.selectbox("Select a stock", sp500_tickers, key="stock_selector")

# "Update" button to refresh data
if st.sidebar.button("Update"):
    stock = yf.Ticker(selected_stock)
    stock_data = stock.history(period="max")
    stock_info = stock.info

    if stock_data.empty:
        st.write(f"No data available for {selected_stock}")
    else:
        st.write("Data updated for all tabs.")

# Tab 1: Summary
with tab1:
    stock = yf.Ticker(selected_stock)
    stock_data = stock.history(period="max")
    stock_info = stock.info

    st.title(f"{selected_stock} Stock Summary")
    if stock_data.empty:
        st.write(f"No data available for {selected_stock}")
    else:
        fig = go.Figure()
    
    # Color-coded volume bars
        colors_list = ['green' if stock_data['Close'][i] > stock_data['Close'][i-1] else 'red'
                    for i in range(1, len(stock_data))]
        colors_list.insert(0, 'green')  # First entry defaults to green

        fig.add_trace(go.Scatter(
            x=stock_data.index, y=stock_data['Close'],
            mode='lines', name='Price',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(88, 163, 255, 0.3)',
            customdata=stock_data[['Open', 'High', 'Low', 'Volume']].values,
            hovertemplate=(
                '<b>Date:</b> %{x}<br>'
                '<b>Close:</b> %{y:.2f}<br>'
                '<b>Open:</b> %{customdata[0]:.2f}<br>'
                '<b>High:</b> %{customdata[1]:.2f}<br>'
                '<b>Low:</b> %{customdata[2]:.2f}<br>'
                '<b>Volume:</b> %{customdata[3]:,.0f}<br>'
            ),
            showlegend=False
        ))

        # Volume bars
        fig.add_trace(go.Bar(
            x=stock_data.index, y=stock_data['Volume'],
            name='Volume',
            marker_color=colors_list,
            yaxis='y2',
            showlegend=False
        ))

        # Update layout with range selector buttons
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1Y", step="year", stepmode="backward"),
                        dict(count=3, label="3Y", step="year", stepmode="backward"),
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(step="all", label="Max")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis=dict(title='Close Price (USD)'),
            yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
            title={
                'text': f'{stock_info["shortName"]} Stock Price with Volume',
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            template='plotly_white',
            height=600,
            width=1100
        )

        st.plotly_chart(fig)

        # Display additional stock information in a table format below the chart
        st.subheader("Key Financial Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Previous Close**: {stock_info.get('previousClose', 'N/A')}")
            st.write(f"**Open**: {stock_info.get('open', 'N/A')}")
            st.write(f"**Bid**: {stock_info.get('bid', 'N/A')}")
            st.write(f"**Ask**: {stock_info.get('ask', 'N/A')}")
            st.write(f"**Day's Range**: {stock_info.get('dayLow', 'N/A')} - {stock_info.get('dayHigh', 'N/A')}")
            st.write(f"**52 Week Range**: {stock_info.get('fiftyTwoWeekLow', 'N/A')} - {stock_info.get('fiftyTwoWeekHigh', 'N/A')}")
            st.write(f"**Volume**: {stock_info.get('volume', 'N/A'):,}")
            st.write(f"**Avg. Volume**: {stock_info.get('averageVolume', 'N/A'):,}")


        with col2:
            market_cap = f"{stock_info.get('marketCap', 'N/A'):,}"  # Add commas for readability
            st.write(f"**Market Cap**: ${market_cap}")
            st.write(f"**Beta (5Y Monthly)**: {stock_info.get('beta', 'N/A')}")
            st.write(f"**PE Ratio (TTM)**: {stock_info.get('trailingPE', 'N/A')}")
            st.write(f"**EPS (TTM)**: {stock_info.get('trailingEps', 'N/A')}")
            st.write(f"**Earnings Date**: {stock_info.get('earningsDate', 'N/A')}")
            st.write(f"**Forward Dividend & Yield**: {stock_info.get('dividendYield', 'N/A')}")
            st.write(f"**Ex-Dividend Date**: {convert_timestamp_to_date(stock_info.get('exDividendDate', 'N/A'))}")
            st.write(f"**1y Target Est**: {stock_info.get('targetMeanPrice', 'N/A')}")

        # Display company profile and major holders
            # Display company profile and major holders
        st.subheader(f"{stock_info['shortName']} Company Profile")
        st.write(f"**Sector**: {stock_info.get('sector', 'N/A')}")
        st.write(f"**Industry**: {stock_info.get('industry', 'N/A')}")
        st.write(f"**Description**: {stock_info.get('longBusinessSummary', 'N/A')}")


        # Major Holders Section
        st.subheader(f"{stock_info['shortName']} Major Holders")

        # Display major holders percentages
        st.write(f"**% of Shares Held by All Insider**: {stock_info.get('heldPercentInsiders', 0) * 100:.2f}%")
        st.write(f"**% of Shares Held by Institutions**: {stock_info.get('heldPercentInstitutions', 0) * 100:.2f}%")

        # Display top institutional shareholders
        st.subheader("Top Institutional Shareholders")

        # Process and display institutional holders data
        institutional_holders_df = stock.institutional_holders[['Holder', 'Shares', 'Date Reported']]
        institutional_holders_df['Date Reported'] = pd.to_datetime(institutional_holders_df['Date Reported'], errors='coerce')

        # Get the latest date in the 'Date Reported' column
        latest_date = institutional_holders_df['Date Reported'].max().strftime('%Y-%m-%d')
        st.write(f"**Latest Date Reported**: {latest_date}")
        st.write("**Note:** Institutional holdings data may not reflect the most recent filings available on Yahoo Finance's website.")


        # Display the table with institutional holders, excluding rows with missing dates
        st.write(institutional_holders_df.dropna(subset=['Date Reported']))


# Second Tab : Chart Tab
with tab2:
    st.title(f"{selected_stock} Detailed Chart")

    chart_type = st.selectbox("Select Chart Type", ["Line", "Candlestick"], key="chart_type")
    time_interval = st.selectbox("Select Time Interval", ["1d", "1wk", "1mo"], key="time_interval")
    time_range = st.selectbox("Select Time Range", ["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "Max"], key="time_range")

    # Mapping the time range to Yahoo Finance period format
    period_mapping = {
        "1M": "1mo", "3M": "3mo", "6M": "6mo", "YTD": "ytd", 
        "1Y": "1y", "3Y": "3y", "5Y": "5y", "Max": "max"
    }
    period = period_mapping[time_range]

    # Fetch stock data based on selected range and interval
    stock = yf.Ticker(selected_stock)
    stock_data = stock.history(period=period, interval=time_interval)
    stock_info = stock.info

    if not stock_data.empty:
        fig = go.Figure()

        # Select between line and candlestick
        if chart_type == "Line":
            fig.add_trace(go.Scatter(
                x=stock_data.index, y=stock_data['Close'],
                mode='lines', name='Close Price',
                line=dict(color='blue')
            ))
        else:
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'], high=stock_data['High'],
                low=stock_data['Low'], close=stock_data['Close'],
                name="Candlestick"
            ))

        # Add 50-day SMA
        stock_data['SMA50'] = stock_data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=stock_data.index, y=stock_data['SMA50'],
            mode='lines', name='50-Day SMA',
            line=dict(color='orange', dash='dash')
        ))

        # Add volume bars at the bottom
        fig.add_trace(go.Bar(
            x=stock_data.index, y=stock_data['Volume'],
            name='Volume', marker_color='rgba(58, 71, 80, 0.6)',
            yaxis='y2'
        ))

        fig.update_layout(
            title=f"{selected_stock} Price Chart",
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
            template='plotly_white',
            height=600,
            width=1100
        )

        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected stock and parameters.")



# Third Tab: Financials 
with tab3:
    st.header("Financials")
    
    # Dropdowns for financial report selection and period
    report_type = st.selectbox("Select Financial Report", ["Income Statement", "Balance Sheet", "Cash Flow"])
    period = st.radio("Select Period", ["Annual", "Quarterly"])
    
    # Function to get financials data from Yahoo Finance
    def get_financial_data(ticker, report, period):
        stock = yf.Ticker(ticker)
        
        if report == "Income Statement":
            if period == "Annual":
                return stock.financials  # Annual income statement
            else:
                return stock.quarterly_financials  # Quarterly income statement
        elif report == "Balance Sheet":
            if period == "Annual":
                return stock.balance_sheet  # Annual balance sheet
            else:
                return stock.quarterly_balance_sheet  # Quarterly balance sheet
        elif report == "Cash Flow":
            if period == "Annual":
                return stock.cashflow  # Annual cash flow
            else:
                return stock.quarterly_cashflow  # Quarterly cash flow

    # Display financial data
    if selected_stock:
        financial_data = get_financial_data(selected_stock, report_type, period)
        if financial_data is not None and not financial_data.empty:
            st.write(financial_data)
        else:
            st.write("No financial data available for this period and report type.")



# Fourth Tab - Monte Carlo Analysis
with tab4:
        st.title(f"Monte Carlo Simulation for: {selected_stock}")

        # User inputs for Monte Carlo simulation
        num_simulations = st.selectbox("Select number of simulations", [200, 500, 1000], index=2)
        num_days = st.selectbox("Select time horizon (days)", [30, 60, 90], index=0)

        # Fetch historical stock data
        stock = yf.Ticker(selected_stock).history(period="5y")['Close']
        last_price = stock[-1]
        daily_return = stock.pct_change().dropna()
        daily_vol = daily_return.std()

        # Monte Carlo simulation
        simulation_df = pd.DataFrame()
        for x in range(num_simulations):
            price_series = [last_price * (1 + np.random.normal(0, daily_vol))]
            for _ in range(num_days - 1):
                price = price_series[-1] * (1 + np.random.normal(0, daily_vol))
                price_series.append(price)
            simulation_df[x] = price_series

        # Plot the Monte Carlo simulation paths
        fig, ax = plt.subplots()
        ax.plot(simulation_df, linewidth=0.5)
        ax.axhline(y=last_price, color='red', linestyle='--', label="Current Price")
        ax.set_title(f"Monte Carlo Simulation: {selected_stock}")
        ax.set_xlabel("Day")
        ax.set_ylabel("Price")
        ax.legend()

        # Display plot in Streamlit
        st.pyplot(fig)

        # Calculate Value at Risk (VaR) at 95% confidence interval
        ending_prices = simulation_df.iloc[-1, :]
        future_price_95ci = np.percentile(ending_prices, 5)
        VaR = ending_prices.iloc[-1] - future_price_95ci
        st.write(f"Value at Risk (VaR) at 95% confidence interval: ${VaR:.2f}")

#tab 5: Statistics

with tab5:
    st.title("Statistics")

    # Retrieve the stock information from Yahoo Finance
    stock = yf.Ticker(selected_stock)
    stock_info = stock.info

    # Display Valuation Measures
    st.subheader("Valuation Measures")
    valuation_measures = {
        "Market Cap": stock_info.get('marketCap', 'N/A'),
        "Enterprise Value": stock_info.get('enterpriseValue', 'N/A'),
        "Trailing P/E": stock_info.get('trailingPE', 'N/A'),
        "Forward P/E": stock_info.get('forwardPE', 'N/A'),
        "PEG Ratio (5yr expected)": stock_info.get('pegRatio', 'N/A'),
        "Price/Sales": stock_info.get('priceToSalesTrailing12Months', 'N/A'),
        "Price/Book": stock_info.get('priceToBook', 'N/A'),
        "Enterprise Value/Revenue": stock_info.get('enterpriseToRevenue', 'N/A'),
        "Enterprise Value/EBITDA": stock_info.get('enterpriseToEbitda', 'N/A')
    }
    valuation_df = pd.DataFrame(valuation_measures, index=["Current"]).T
    st.table(valuation_df)

    # Financial Highlights
    st.subheader("Financial Highlights")

    # Helper function to format values with comma separator and unit
    def format_value(value, unit=""):
        if isinstance(value, (int, float)):
            return f"{value:,.2f} {unit}".strip()
        return value


# Function to format date values
    def format_date(timestamp):
        if pd.isna(timestamp) or timestamp == 'N/A':
            return "N/A"
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except Exception:
            return "Invalid Date"

    # Fiscal Year Section
    st.write("**Fiscal Year**")
    st.write(f"Fiscal Year Ends: {format_date(stock_info.get("lastFiscalYearEnd", 'N/A'))}")
    st.write(f"Most Recent Quarter: {format_date(stock_info.get('mostRecentQuarter', 'N/A'))}")

    # Profitability
    st.write("**Profitability**")
    st.write(f"Profit Margin: {format_value(stock_info.get('profitMargins', 'N/A') * 100, '%')}")
    st.write(f"Operating Margin: {format_value(stock_info.get('operatingMargins', 'N/A') * 100, '%')}")

    # Management Effectiveness
    st.write("**Management Effectiveness**")
    st.write(f"Return on Assets: {format_value(stock_info.get('returnOnAssets', 'N/A') * 100, '%')}")
    st.write(f"Return on Equity: {format_value(stock_info.get('returnOnEquity', 'N/A') * 100, '%')}")

    # Income Statement
    st.write("**Income Statement**")
    st.write(f"Revenue (ttm): {format_value(stock_info.get('totalRevenue', 'N/A'), '$')}")
    st.write(f"Revenue Per Share (ttm): {format_value(stock_info.get('revenuePerShare', 'N/A'), '$')}")
    st.write(f"Quarterly Revenue Growth (yoy): {format_value(stock_info.get('revenueGrowth', 'N/A') * 100, '%')}")
    st.write(f"Gross Profit (ttm): {format_value(stock_info.get('grossProfits', 'N/A'), '$')}")
    st.write(f"EBITDA: {format_value(stock_info.get('ebitda', 'N/A'), '$')}")
    st.write(f"Net Income Avi to Common (ttm): {format_value(stock_info.get('netIncomeToCommon', 'N/A'), '$')}")
    st.write(f"Diluted EPS (ttm): {format_value(stock_info.get('trailingEps', 'N/A'), '$')}")
    st.write(f"Quarterly Earnings Growth (yoy): {format_value(stock_info.get('earningsGrowth'* 100, '--') , '%')}")


    # Balance Sheet
    st.write("**Balance Sheet**")
    st.write(f"Total Cash (mrq): {format_value(stock_info.get('totalCash', 'N/A'), '$')}")
    st.write(f"Total Cash Per Share (mrq): {format_value(stock_info.get('totalCashPerShare', 'N/A'), '$')}")
    st.write(f"Total Debt (mrq): {format_value(stock_info.get('totalDebt', 'N/A'), '$')}")
    st.write(f"Total Debt/Equity (mrq): {format_value(stock_info.get('debtToEquity', 'N/A') * 100, '%')}")
    st.write(f"Current Ratio (mrq): {format_value(stock_info.get('currentRatio', 'N/A'))}")
    st.write(f"Book Value Per Share (mrq): {format_value(stock_info.get('bookValue', 'N/A'), '$')}")

    # Cash Flow Statement
    st.write("**Cash Flow Statement**")
    st.write(f"Operating Cash Flow (ttm): {format_value(stock_info.get('operatingCashflow', 'N/A'), '$')}")
    st.write(f"Levered Free Cash Flow (ttm): {format_value(stock_info.get('freeCashflow', 'N/A'), '$')}")

    # Abbreviation Guide
    st.write("**Abbreviation Guide**")
    st.write("mrq = Most Recent Quarter")
    st.write("ttm = Trailing Twelve Months")
    st.write("yoy = Year Over Year")
    st.write("lfy = Last Fiscal Year")
    st.write("fye = Fiscal Year Ending")

    