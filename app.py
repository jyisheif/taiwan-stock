import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from FinMind.data import DataLoader
import os
from datetime import datetime

# --- 1. 初始化與設定 ---
st.set_page_config(page_title="台股自動化監控系統", layout="wide")
API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoianlpc2hlaWYiLCJlbWFpbCI6Imp5aXNoZWlmQGdtYWlsLmNvbSIsInRva2VuX3ZlcnNpb24iOjB9.ccTI4YgmuGVNJ-CDjMKxFJymGg8BBU00k6LWyuo0fSo" # 建議填入你的 Token 提高額度

def get_stock_data(stock_id):
    """抓取並更新資料的邏輯"""
    file_name = f"stock_{stock_id}.csv"
    dl = DataLoader()
    dl.login_by_token(api_token=API_TOKEN) # 若有 Token 請取消註解
    
    # 判斷起始日期
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
        last_date = pd.to_datetime(df_old['date'].max())
        start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        st.info(f"偵測到 {target_stock} 沒有本地資料，正在從 FinMind 伺服器下載...")
        df_old = get_stock_data(target_stock) # 呼叫你定義的抓取函式
    
    # 執行抓取
    df_new = dl.taiwan_stock_daily(stock_id=stock_id, start_date=start_date)
    
    if not df_new.empty:
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['date'])
        df_combined.to_csv(file_name, index=False)
        return df_combined
    return df_old

# --- 2. 側邊欄介面 ---
st.sidebar.title("控制面板")
target_stock = st.sidebar.text_input("輸入台股代碼", value="2330")
update_btn = st.sidebar.button("手動強制更新資料")

# --- 3. 主要邏輯 ---
st.title(f"📊 台股即時監控：{target_stock}")

with st.spinner(f'正在檢查 {target_stock} 的最新數據...'):
    df = get_stock_data(target_stock)

if not df.empty:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # 計算均線 (MA)
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()

    # --- 4. 數據指標卡片 ---
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    change = last_row['close'] - prev_row['close']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("當前股價", f"{last_row['close']}", f"{change:.2f}")
    col2.metric("最高價", f"{last_row['high']}")
    col3.metric("最低價", f"{last_row['low']}")
    col4.metric("成交量", f"{int(last_row['Trading_Volume']):,}")

    # --- 5. 繪製 K 線圖 ---
    fig = go.Figure(data=[
        go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='K線'),
        go.Scatter(x=df['date'], y=df['MA5'], line=dict(color='orange', width=1), name='5MA'),
        go.Scatter(x=df['date'], y=df['MA20'], line=dict(color='blue', width=1), name='20MA')
    ])
    fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- 6. 數據明細 ---
    with st.expander("查看完整歷史數據"):
        st.write(df.sort_values('date', ascending=False))
else:
    st.error("找不到該股票代碼的資料，請確認輸入是否正確。")
