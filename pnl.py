import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Set page to wide mode
st.set_page_config(layout="wide")

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

if 'show_graphs' not in st.session_state:
    st.session_state.show_graphs = True

if 'show_risk_metrics' not in st.session_state:
    st.session_state.show_risk_metrics = True

if 'show_reset_confirmation' not in st.session_state:
    st.session_state.show_reset_confirmation = False

# Title
st.title("Enhanced Trading Backtest PnL Calculator")

# Input fields
col1, col2, col3, col4 = st.columns(4)
with col1:
    symbol = st.selectbox("Symbol", options=list(TICK_VALUES.keys()))
with col2:
    ticks = st.number_input("Ticks", step=1, help="Enter ticks (positive for profit, negative for loss)")
with col3:
    contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)
with col4:
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

# Toggle buttons
col1, col2 = st.columns(2)
with col1:
    st.session_state.show_graphs = st.checkbox("Show Graphs", value=st.session_state.show_graphs)
with col2:
    st.session_state.show_risk_metrics = st.checkbox("Show Risk Metrics", value=st.session_state.show_risk_metrics)

# Display content if trades exist
if st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades)

    # Multiple Graphs
    if st.session_state.show_graphs:
        st.subheader("Performance Graphs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cumulative PnL
            fig_cumulative = go.Figure()
            fig_cumulative.add_trace(go.Scatter(x=list(range(1, len(trades_df) + 1)), y=trades_df['Cumulative PnL'], name="Cumulative PnL"))
            fig_cumulative.add_hline(y=0, line_dash='dash', line_color='red')
            fig_cumulative.update_layout(title="Cumulative PnL", xaxis_title="Trade Number", yaxis_title="Cumulative PnL ($)")
            st.plotly_chart(fig_cumulative, use_container_width=True)
        
        with col2:
            # Individual Trade PnL
            fig_individual = go.Figure()
            fig_individual.add_trace(go.Bar(x=list(range(1, len(trades_df) + 1)), y=trades_df['PnL'], name="Trade PnL"))
            fig_individual.update_layout(title="Individual Trade PnL", xaxis_title="Trade Number", yaxis_title="PnL ($)")
            st.plotly_chart(fig_individual, use_container_width=True)
        
        # Win/Loss Pie Chart
        win_loss_data = trades_df['PnL'].apply(lambda x: 'Win' if x > 0 else ('Loss' if x < 0 else 'Break Even'))
        win_loss_counts = win_loss_data.value_counts()
        fig_pie = px.pie(values=win_loss_counts.values, names=win_loss_counts.index, title="Win/Loss Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Display trades
    st.subheader("Trades")
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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total P&L", f"${total_pnl:.2f}")
        st.metric("Average Winning Trade", f"${winning_trades['PnL'].mean():.2f}" if not winning_trades.empty else "N/A")
        st.metric("Average Losing Trade", f"${losing_trades['PnL'].mean():.2f}" if not losing_trades.empty else "N/A")
        st.metric("Total Number of Trades", len(trades_df))
    with col2:
        st.metric("Number of Winning Trades", len(winning_trades))
        st.metric("Number of Losing Trades", len(losing_trades))
        st.metric("Number of Break Even Trades", len(break_even_trades))
        st.metric("Max Consecutive Wins", max_consecutive_wins)
    with col3:
        st.metric("Max Consecutive Losses", max_consecutive_losses)
        st.metric("Total Commissions", f"${trades_df['Commission'].sum():.2f}")
        st.metric("Largest Profit", f"${trades_df['PnL'].max():.2f}")
        st.metric("Largest Loss", f"${trades_df['PnL'].min():.2f}")
    with col4:
        st.metric("Average Trade P&L", f"${trades_df['PnL'].mean():.2f}")
        st.metric("Profit Factor", f"{profit_factor:.2f}")
        st.metric("Trade Expectancy", f"${trade_expectancy:.2f}")
        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0
        st.metric("Win Rate", f"{win_rate:.2f}%")

    # Risk Metrics
    if st.session_state.show_risk_metrics:
        st.subheader("Risk Metrics")
        
        # Sharpe Ratio (assuming risk-free rate of 2% annualized)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate (assuming 252 trading days)
        returns = trades_df['PnL'].pct_change()
        sharpe_ratio = (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252) if len(trades_df) > 1 else 0
        
        # Maximum Drawdown
        cumulative = trades_df['Cumulative PnL']
        max_drawdown = (cumulative.cummax() - cumulative).max() / cumulative.cummax().max() if len(cumulative) > 0 else 0
        
        # Risk-Reward Ratio
        risk_reward_ratio = abs(winning_trades['PnL'].mean() / losing_trades['PnL'].mean()) if not losing_trades.empty and not winning_trades.empty else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
        with col2:
            st.metric("Maximum Drawdown", f"{max_drawdown:.2%}")
        with col3:
            st.metric("Risk-Reward Ratio", f"{risk_reward_ratio:.2f}")

# Reset button with confirmation
if st.button("Reset All Trades"):
    st.session_state.show_reset_confirmation = True

if st.session_state.show_reset_confirmation:
    st.warning("Are you sure you want to reset all trades? This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, reset all trades", key="confirm_reset"):
            st.session_state.trades = []
            st.session_state.show_reset_confirmation = False
            st.success("All trades have been reset.")
            st.experimental_rerun()
    with col2:
        if st.button("No, keep my trades", key="cancel_reset"):
            st.session_state.show_reset_confirmation = False
            st.info("Reset cancelled. Your trades are safe.")
            st.experimental_rerun()
