import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from FinMind.data import DataLoader
import os

# 1. 頁面設定
st.set_page_config(page_title="台股監控系統", layout="wide")

# 2. 資料抓取函式
def get_stock_data(stock_id):
    dl = DataLoader()
    dl.login_by_token(api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoianlpc2hlaWYiLCJlbWFpbCI6Imp5aXNoZWlmQGdtYWlsLmNvbSIsInRva2VuX3ZlcnNpb24iOjB9.ccTI4YgmuGVNJ-CDjMKxFJymGg8BBU00k6LWyuo0fSo") # 若有 Token 請在此輸入
    
    file_name = f"stock_{stock_id}.csv"
    
    # 若檔案存在，讀取並檢查是否需要增量更新
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        # 若無檔案，從 API 下載
        try:
            df = dl.taiwan_stock_daily(stock_id=stock_id, start_date='2023-01-01')
            if not df.empty:
                df.to_csv(file_name, index=False)
                return df
        except Exception as e:
            st.error(f"下載失敗: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# 3. 側邊欄介面
st.sidebar.title("設定")
target_stock = st.sidebar.text_input("輸入股票代碼", value="2330")

# 4. 主程式邏輯
st.title(f"📊 {target_stock} 股價分析")

if target_stock:
    with st.spinner('載入數據中...'):
        df = get_stock_data(target_stock)
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 計算均線
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        
        # 繪圖
        fig = go.Figure(data=[
            go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='K線'),
            go.Scatter(x=df['date'], y=df['MA5'], line=dict(color='orange', width=1.5), name='5MA'),
            go.Scatter(x=df['date'], y=df['MA20'], line=dict(color='blue', width=1.5), name='20MA')
        ])
        fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # 數據預覽
        st.subheader("最新資料")
        st.dataframe(df.tail(10).sort_values('date', ascending=False))
    else:
        st.warning("查無資料，請確認代碼是否正確。")# --- 2. 側邊欄介面 ---
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
