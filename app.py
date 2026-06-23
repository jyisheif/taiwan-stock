import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")
st.title("📈 個人台股監控儀表板")

# 自動搜尋目錄下的 CSV
files = [f for f in os.listdir('.') if f.startswith('stock_') and f.endswith('.csv')]
stock_file = st.sidebar.selectbox("選擇股票檔案", files)

if stock_file:
    df = pd.read_csv(stock_file)
    df['date'] = pd.to_datetime(df['date'])
    
    # 顯示最後更新資料
    st.subheader(f"目前檢視: {stock_file}")
    
    # 互動式 K 線圖
    fig = go.Figure(data=[go.Candlestick(
        x=df['date'],
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # 顯示原始數據
    with st.expander("檢視原始數據"):
        st.dataframe(df.sort_values('date', ascending=False))
