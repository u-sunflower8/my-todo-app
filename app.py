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

st.title("🚀 最強のToDoアプリ")

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

# 3. データ取得 (列名を気にせず読み込む)
data = sheet.get_all_values()
if len(data) > 1:
    # ヘッダーを使わず、リストの番号(0,1,2,3,4)でデータを管理
    df = pd.DataFrame(data[1:], columns=['タスク名', '期限', '完了フラグ', '優先度', 'カテゴリ'])
    
    # 完了フラグが「未着手」のものだけ抽出
    df = df[df['完了フラグ'] == '未着手']
    
    # 並び替え
    priority_map = {"高": 1, "中": 2, "低": 3}
    df['p_num'] = df['優先度'].map(priority_map)
    df = df.sort_values(by=['p_num', '期限'])
    
    st.subheader("📊 未完了タスク一覧")
    st.table(df[['タスク名', '期限', '優先度', 'カテゴリ']])
else:
    st.write("タスクがありません")
