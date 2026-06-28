import streamlit as st
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. 認証と設定 ---
creds_dict = st.secrets["GOOGLE_SHEETS"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = "101hhNwt1VrR0fn3me63ifsduMqelnVIrY1ozr_Ul74w"
sheet = client.open_by_key(SHEET_ID).sheet1

# Discord通知関数（このブロックをそのまま差し替えてください）
def send_discord_notification(message):
    # 関数の「中」でURLを定義すれば、エラーになりません
    url = st.secrets["DISCORD_WEBHOOK_URL"]
    payload = {"content": message}
    
    # 送信処理
    response = requests.post(url, json=payload)
    return response.status_code, response.text

# --- 3. アプリのUIと処理 ---
st.title("ToDoリスト")

# 登録フォーム
with st.form("add_todo"):
    title = st.text_input("タスク名")
    due = st.date_input("期限")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    submit = st.form_submit_button("追加")

# ボタンが押された時の処理
if submit:
    # シートへの書き込み
    sheet.append_row([title, str(due), "未", priority, category])
    
    # Discord通知の実行と診断
    status, text = send_discord_notification(f"📝 新タスク: {title} ({category})")
    
    if status in [200, 204]:
        st.success("追加完了！Discordにも通知しました。")
    else:
        st.error(f"追加は成功しましたが、Discord通知でエラー(コード:{status})が出ました。")
        st.write(f"詳細: {text}")
    
    st.rerun()

# --- 4. 一覧表示とサイドバー ---
st.sidebar.header("フィルター")
all_todos = sheet.get_all_records()

if all_todos:
    categories = ["すべて"] + list(set([t["カテゴリ"] for t in all_todos]))
    selected_cat = st.sidebar.selectbox("カテゴリで絞り込む", categories)
    
    if selected_cat == "すべて":
        filtered_todos = all_todos
    else:
        filtered_todos = [t for t in all_todos if t["カテゴリ"] == selected_cat]
    
    st.subheader("タスク一覧")
    st.table(filtered_todos)
else:
    st.write("タスクはありません。")
