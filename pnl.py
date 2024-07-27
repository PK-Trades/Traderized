import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Constants
TICK_VALUES = {
    "NQ": 5,
    "ES": 12.5,
    "YM": 5,
    "GC": 10
}

# Initialize session state variables
if 'trades' not in st.session_state:
    st.session_state.trades = []

# Title
st.title("Trading Backtest PnL Calculator")

# Input fields
col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Symbol", options=list(TICK_VALUES.keys()))
    ticks = st.number_input("Ticks", step=1, help="Enter ticks (positive for profit, negative for loss)")
with col2:
    contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)
    commission = st.number_input("Commission per Contract ($)", min_value=0.0, value=0.0, step=0.01)

# Add Trade button
if st.button("Add Trade"):
    if ticks != 0:
        tick_value = ticks * TICK_VALUES[symbol] * contracts
        commission_cost = commission * contracts
        pnl = tick_value - commission_cost
        cumulative_pnl = (st.session_state.trades[-1]['Cumulative PnL'] if st.session_state.trades else 0) + pnl
        
        st.session_state.trades.append({
            "Symbol": symbol,
            "Ticks": ticks,
            "Contracts": contracts,
            "Commission": commission_cost,
            "PnL": pnl,
            "Cumulative PnL": cumulative_pnl
        })
        st.success("Trade added successfully!")
    else:
        st.error("Please enter a non-zero tick value.")

# Display trades
if st.session_state.trades:
    st.subheader("Trades")
    trades_df = pd.DataFrame(st.session_state.trades)
    st.dataframe(trades_df)

    # Calculate statistics
    total_pnl = trades_df['PnL'].sum()
    winning_trades = trades_df[trades_df['PnL'] > 0]
    losing_trades = trades_df[trades_df['PnL'] < 0]
    break_even_trades = trades_df[trades_df['PnL'] == 0]
    
    # Calculate max consecutive wins and losses
    trade_results = (trades_df['PnL'] > 0).astype(int).replace(0, -1)
    trade_streaks = trade_results.groupby((trade_results != trade_results.shift()).cumsum()).cumsum()
    max_consecutive_wins = trade_streaks.max()
    max_consecutive_losses = -trade_streaks.min()

    # Calculate Profit Factor and Trade Expectancy
    total_gross_profit = winning_trades['PnL'].sum()
    total_gross_loss = abs(losing_trades['PnL'].sum())
    profit_factor = total_gross_profit / total_gross_loss if total_gross_loss != 0 else float('inf')
    trade_expectancy = (winning_trades['PnL'].mean() * (len(winning_trades) / len(trades_df))) + \
                       (losing_trades['PnL'].mean() * (len(losing_trades) / len(trades_df)))

    st.subheader("Statistics Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total P&L", f"${total_pnl:.2f}")
        st.metric("Average Winning Trade", f"${winning_trades['PnL'].mean():.2f}" if not winning_trades.empty else "N/A")
        st.metric("Average Losing Trade", f"${losing_trades['PnL'].mean():.2f}" if not losing_trades.empty else "N/A")
        st.metric("Total Number of Trades", len(trades_df))
        st.metric("Number of Winning Trades", len(winning_trades))
        st.metric("Number of Losing Trades", len(losing_trades))
    with col2:
        st.metric("Number of Break Even Trades", len(break_even_trades))
        st.metric("Max Consecutive Wins", max_consecutive_wins)
        st.metric("Max Consecutive Losses", max_consecutive_losses)
        st.metric("Total Commissions", f"${trades_df['Commission'].sum():.2f}")
        st.metric("Largest Profit", f"${trades_df['PnL'].max():.2f}")
        st.metric("Largest Loss", f"${trades_df['PnL'].min():.2f}")
    with col3:
        st.metric("Average Trade P&L", f"${trades_df['PnL'].mean():.2f}")
        st.metric("Profit Factor", f"{profit_factor:.2f}")
        st.metric("Trade Expectancy", f"${trade_expectancy:.2f}")
        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.2f}%")

    # PnL Graph
    st.subheader("PnL Graph")
    try:
        fig = go.Figure(data=[go.Scatter(
            x=list(range(1, len(trades_df) + 1)),
            y=trades_df['Cumulative PnL'].tolist()
        )])
        fig.update_layout(title='Cumulative PnL Over Time', xaxis_title='Trade Number', yaxis_title='Cumulative PnL ($)')
        fig.add_hline(y=0, line_dash='dash', line_color='red')
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"An error occurred while creating the PnL graph: {str(e)}")
        st.info("Please check your data and try again.")

# Reset button
if st.button("Reset All Trades"):
    st.session_state.trades = []
    st.success("All trades have been reset.")
