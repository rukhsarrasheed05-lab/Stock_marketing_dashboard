import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf  # For live data if needed

# Set page config
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Function to load and prepare data
@st.cache_data
def load_stock_data():
    # Load datasets (replace with actual Kaggle dataset paths)
    try:
        # For demonstration, we'll use sample data. In real implementation, 
        # download from Kaggle and load CSV files
        
        # Dataset 1: Apple (AAPL) - assume downloaded from Kaggle
        aapl_data = pd.read_csv('AAPL.csv')
        aapl_data['Source'] = 'Kaggle_AAPL'
        
        # Dataset 2: Google (GOOGL) - assume downloaded from Kaggle  
        googl_data = pd.read_csv('NFLX.csv')
        googl_data['Source'] = 'Kaggle_NFLX'
        
       
        
        # Standardize column names (assuming Kaggle datasets have Date, Open, High, Low, Close, Volume)
        for df in [aapl_data, googl_data, msft_data]:
            df.columns = df.columns.str.strip()
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
        
        # Merge datasets
        combined_data = pd.concat([aapl_data, googl_data, msft_data], axis=0)
        
        return combined_data, aapl_data, googl_data, msft_data
        
    except FileNotFoundError:
        st.error("Stock data files not found. Please ensure CSV files are in the 'data' directory.")
        return None, None, None, None

# Load data
combined_data, aapl_data, googl_data, msft_data = load_stock_data()

if combined_data is not None:
    # Main header
    st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for controls
    st.sidebar.title("Dashboard Controls")
    
    # Stock selection
    available_stocks = ['AAPL', 'GOOGL']
    selected_stocks = st.sidebar.multiselect(
        "Select Stocks to Compare",
        available_stocks,
        default=['AAPL', 'GOOGL']
    )
    
    # Date range selection
    if not combined_data.empty:
        min_date = combined_data.index.min().date()
        max_date = combined_data.index.max().date()
        
        start_date = st.sidebar.date_input(
            "Start Date",
            min_date,
            min_value=min_date,
            max_value=max_date
        )
        end_date = st.sidebar.date_input(
            "End Date", 
            max_date,
            min_value=min_date,
            max_value=max_date
        )
        
        # Ensure end_date is after start_date
        if start_date >= end_date:
            st.sidebar.error("End date must be after start date")
            end_date = start_date + timedelta(days=1)
    
    # Analysis type
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Price Trends", "Volume Analysis", "Returns Comparison", "Correlation Matrix"]
    )
    
    # Filter data based on selections
    if selected_stocks and not combined_data.empty:
        filtered_data = combined_data[combined_data.index.date >= start_date]
        filtered_data = filtered_data[filtered_data.index.date <= end_date]
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Detailed Analysis", "🔍 Stock Comparison", "ℹ️ About"])
        
        with tab1:
            st.header("Market Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            for i, stock in enumerate(selected_stocks[:4]):  # Limit to 4 stocks for display
                stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                if not stock_data.empty:
                    latest_price = stock_data['Close'].iloc[-1]
                    price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]
                    price_change_pct = (price_change / stock_data['Close'].iloc[0]) * 100
                    
                    with [col1, col2, col3, col4][i]:
                        st.metric(
                            label=f"{stock} Price",
                            value=f"${latest_price:.2f}",
                            delta=f"{price_change_pct:.2f}%"
                        )
            
            # Overview chart
            st.subheader("Stock Price Trends")
            fig_overview = go.Figure()
            
            for stock in selected_stocks:
                stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                if not stock_data.empty:
                    fig_overview.add_trace(go.Scatter(
                        x=stock_data.index,
                        y=stock_data['Close'],
                        mode='lines',
                        name=stock,
                        line=dict(width=2)
                    ))
            
            fig_overview.update_layout(
                title="Stock Price Comparison",
                xaxis_title="Date",
                yaxis_title="Closing Price ($)",
                height=500
            )
            st.plotly_chart(fig_overview, use_container_width=True)
        
        with tab2:
            st.header("Detailed Analysis")
            
            if analysis_type == "Price Trends":
                st.subheader("Price Trends Analysis")
                
                for stock in selected_stocks:
                    stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                    if not stock_data.empty:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Candlestick chart
                            fig_candle = go.Figure(data=[go.Candlestick(
                                x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close']
                            )])
                            fig_candle.update_layout(
                                title=f"{stock} Candlestick Chart",
                                height=400
                            )
                            st.plotly_chart(fig_candle, use_container_width=True)
                        
                        with col2:
                            # Volume chart
                            fig_volume = px.bar(
                                stock_data,
                                x=stock_data.index,
                                y='Volume',
                                title=f"{stock} Trading Volume"
                            )
                            fig_volume.update_layout(height=400)
                            st.plotly_chart(fig_volume, use_container_width=True)
            
            elif analysis_type == "Volume Analysis":
                st.subheader("Volume Analysis")
                
                fig_volume_comp = go.Figure()
                for stock in selected_stocks:
                    stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                    if not stock_data.empty:
                        fig_volume_comp.add_trace(go.Bar(
                            x=stock_data.index,
                            y=stock_data['Volume'],
                            name=stock
                        ))
                
                fig_volume_comp.update_layout(
                    title="Trading Volume Comparison",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    barmode='group',
                    height=500
                )
                st.plotly_chart(fig_volume_comp, use_container_width=True)
            
            elif analysis_type == "Returns Comparison":
                st.subheader("Returns Analysis")
                
                returns_data = pd.DataFrame()
                for stock in selected_stocks:
                    stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                    if not stock_data.empty:
                        returns_data[stock] = stock_data['Close'].pct_change()
                
                if not returns_data.empty:
                    fig_returns = px.line(
                        returns_data,
                        title="Daily Returns Comparison",
                        labels={'value': 'Daily Return', 'variable': 'Stock'}
                    )
                    fig_returns.update_layout(height=500)
                    st.plotly_chart(fig_returns, use_container_width=True)
                    
                    # Cumulative returns
                    cum_returns = (1 + returns_data).cumprod() - 1
                    fig_cum_returns = px.line(
                        cum_returns,
                        title="Cumulative Returns",
                        labels={'value': 'Cumulative Return', 'variable': 'Stock'}
                    )
                    fig_cum_returns.update_layout(height=500)
                    st.plotly_chart(fig_cum_returns, use_container_width=True)
            
            elif analysis_type == "Correlation Matrix":
                st.subheader("Stock Correlation Analysis")
                
                corr_data = pd.DataFrame()
                for stock in selected_stocks:
                    stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                    if not stock_data.empty:
                        corr_data[stock] = stock_data['Close']
                
                if not corr_data.empty:
                    correlation_matrix = corr_data.corr()
                    
                    fig_corr = px.imshow(
                        correlation_matrix,
                        text_auto=True,
                        aspect="auto",
                        color_continuous_scale='RdBu_r',
                        title="Stock Price Correlation Matrix"
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
        
        with tab3:
            st.header("Stock Comparison")
            
            # Statistical comparison
            st.subheader("Statistical Summary")
            
            stats_data = []
            for stock in selected_stocks:
                stock_data = filtered_data[filtered_data['Source'].str.contains(stock)]
                if not stock_data.empty:
                    stats = {
                        'Stock': stock,
                        'Mean Price': stock_data['Close'].mean(),
                        'Std Dev': stock_data['Close'].std(),
                        'Min Price': stock_data['Close'].min(),
                        'Max Price': stock_data['Close'].max(),
                        'Total Volume': stock_data['Volume'].sum()
                    }
                    stats_data.append(stats)
            
            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df)
                
                # Performance comparison chart
                fig_perf = px.bar(
                    stats_df,
                    x='Stock',
                    y='Mean Price',
                    title="Average Closing Price Comparison",
                    color='Stock'
                )
                st.plotly_chart(fig_perf, use_container_width=True)
        
        with tab4:
            st.header("About This Dashboard")
            
            st.markdown("""
            ## Stock Market Dashboard
            
            This dashboard provides comprehensive analysis of stock market data with the following features:
            
            ### Features:
            - **Multi-Stock Comparison**: Compare multiple stocks simultaneously
            - **Interactive Charts**: Candlestick, line, bar, and correlation charts
            - **Time Series Analysis**: Analyze trends over custom date ranges
            - **Volume Analysis**: Study trading volume patterns
            - **Returns Analysis**: Calculate and visualize daily and cumulative returns
            - **Statistical Summary**: Key statistics for selected stocks
            
            ### Data Sources:
            - Apple (AAPL) stock data from Kaggle
            - Google (GOOGL) stock data from Kaggle  
            - Microsoft (MSFT) stock data from Kaggle
            
            ### Technologies Used:
            - Streamlit for the web interface
            - Plotly for interactive visualizations
            - Pandas for data manipulation
            - Python for backend logic
            
            ### How to Use:
            1. Select stocks from the sidebar
            2. Choose date range for analysis
            3. Select analysis type
            4. Explore different tabs for various insights
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit | Data sourced from Kaggle")

else:
    st.error("Unable to load stock data. Please check your data files.")