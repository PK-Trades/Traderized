import streamlit as st
import pandas as pd

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
    losing_trades = trades_df[trades_df['PnL'] <= 0]
   
    st.subheader("Statistics Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total PnL", f"${total_pnl:.2f}")
        win_rate = len(winning_trades) / len(trades_df) * 100 if trades_df.shape[0] > 0 else 0
        st.metric("Win Rate", f"{min(win_rate, 100):.2f}%")
        st.metric("Average Winning Trade", f"${winning_trades['PnL'].mean():.2f}" if not winning_trades.empty else "N/A")
        st.metric("Average Losing Trade", f"${losing_trades['PnL'].mean():.2f}" if not losing_trades.empty else "N/A")
    with col2:
        st.metric("Largest Winning Trade", f"${trades_df['PnL'].max():.2f}")
        st.metric("Largest Losing Trade", f"${trades_df['PnL'].min():.2f}")
        st.metric("Total Commission", f"${trades_df['Commission'].sum():.2f}")

# Reset button
if st.button("Reset All Trades"):
    st.session_state.trades = []
    st.success("All trades have been reset.")
