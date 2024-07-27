import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Define the symbols and their corresponding tick values
symbols = {
    'NQ': 5,
    'ES': 12.5,
    'YM': 5,
    'GC': 10
}

# Initialize the trade history and PnL list
trade_history = []
pnl_values = []

# Create a Streamlit app
st.title('Trading Backtest PnL Calculator')

# Symbol selection
symbol = st.selectbox('Select Symbol', list(symbols.keys()))

# Trade input
ticks_profit = st.number_input('Ticks Profit', min_value=0)
ticks_drawdown = st.number_input('Ticks Drawdown', min_value=0)

# Calculate PnL and update the list
if st.button('Calculate PnL'):
    tick_value = symbols[symbol]
    pnl = (ticks_profit - ticks_drawdown) * tick_value
    pnl_values.append(pnl)
    trade_history.append({
        'symbol': symbol,
        'ticks_profit': ticks_profit,
        'ticks_drawdown': ticks_drawdown,
        'pnl': pnl
    })

# Display trade history
st.write('Trade History:')
for trade in trade_history:
    st.write(f"{trade['symbol']}: {trade['ticks_profit']} ticks profit, {trade['ticks_drawdown']} ticks drawdown, PnL: ${trade['pnl']:.2f}")

# Calculate total PnL
total_pnl = sum(trade['pnl'] for trade in trade_history)
st.write(f'Total PnL: ${total_pnl:.2f}')

# Create a Plotly figure
fig = go.Figure(data=[go.Scatter(y=pnl_values)])

# Display the PnL graph
st.plotly_chart(fig, use_container_width=True)
