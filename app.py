import streamlit as st
import gspread
import requests
import datetime
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# 1. 接続設定
creds_dict = st.secrets["GOOGLE_SHEETS"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = "101hhNwt1VrR0fn3me63ifsduMqelnVIrY1ozr_Ul74w"
sheet = client.open_by_key(SHEET_ID).sheet1

# 2. 通知関数
def send_discord_notification(message):
    url = st.secrets["DISCORD"]["WEBHOOK_URL"]
    requests.post(url, json={"content": message})
    

st.markdown("""
<style>
    /* 全体のベースカラーを落ち着いたオフホワイトに */
    .stApp {
        background-color: #FAFAFA;
        color: #333333;
    }

    /* フォント設定：読みやすく、モダンなゴシック体 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* タイトルとヘッダーを控えめに */
    h1, h2, h3 {
        color: #2D2D2D !important;
        font-weight: 500 !important;
    }

    /* 入力フォームの角を丸めて柔らかく */
    div[data-baseweb="base-input"], div[data-baseweb="select"] {
        border-radius: 8px !important;
    }

/* ボタンの強制上書き */
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #333333 !important;
        color: #f0f0f0 !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        padding: 0.5rem 3rem !important;
        transition: all 0.3s ease !important;
    }

    /* ボタンにカーソルを合わせた時の変化 */
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #f0f0f0 !important;
        color: #333333 !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("最強のToDoアプリ")

# --- タスク入力 ---
with st.form("todo_input"):
    new_task = st.text_input("タスク名")
    new_date = st.date_input("期限")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    submit = st.form_submit_button("追加")
    if submit:
        sheet.append_row([new_task, str(new_date), "未着手", priority, category])
        st.rerun()

# 3. データ取得
data = sheet.get_all_values()
if len(data) > 1:
    df = pd.DataFrame(data[1:], columns=['タスク名', '期限', '完了フラグ', '優先度', 'カテゴリ'])
    
    # 完了ではないものを抽出
    df = df[df['完了フラグ'] != '完了']
    
    # 並び替え
    priority_map = {"高": 1, "中": 2, "低": 3}
    df['p_num'] = df['優先度'].map(priority_map)
    df = df.sort_values(by=['p_num', '期限'])
    
# 5. 一覧表示（st.table から st.dataframe に変更）
    st.subheader("進行中・未着手タスク一覧")
    if not df.empty:
        # use_container_width=True で幅を広げ、hide_index=True で左の列番号を消します
        st.dataframe(
            df[['タスク名', '期限', '完了フラグ', '優先度', 'カテゴリ']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.write("表示できるタスクはありません。")
