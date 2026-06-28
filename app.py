import streamlit as st
import gspread
import requests  # ★これが必要！
from oauth2client.service_account import ServiceAccountCredentials

# 認証設定
creds_dict = st.secrets["GOOGLE_SHEETS"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = "101hhNwt1VrR0fn3me63ifsduMqelnVIrY1ozr_Ul74w"
sheet = client.open_by_key(SHEET_ID).sheet1

# Discord通知関数
def send_discord_notification(message):
    url = st.secrets["DISCORD_WEBHOOK_URL"]
    payload = {"content": message}
    requests.post(url, json=payload)

st.title("ToDoリスト")

# 登録フォーム
with st.form("add_todo"):
    title = st.text_input("タスク名")
    due = st.date_input("期限")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    submit = st.form_submit_button("追加")
    
if submit:
        # 1. シートへの書き込み
        sheet.append_row([title, str(due), "未", priority, category])
        
        # 2. Discord通知 (try-exceptでエラーを回避して表示)
# ファイルの最後の方に、一時的に以下を追記して保存してください
# アプリを開くたびにDiscordにテストメッセージが飛ぶはずです
try:
    send_discord_notification("テスト通知：アプリが起動しました！")
    st.write("テスト通知を送信しました！Discordを確認してください。")
except Exception as e:
    st.write(f"テスト通知でエラー: {e}")
        
        st.rerun()
# サイドバー絞り込み
st.sidebar.header("フィルター")
all_todos = sheet.get_all_records()
if all_todos:
    categories = ["すべて"] + list(set([t["カテゴリ"] for t in all_todos]))
    selected_cat = st.sidebar.selectbox("カテゴリで絞り込む", categories)
    
    if selected_cat == "すべて":
        filtered_todos = all_todos
    else:
        filtered_todos = [t for t in all_todos if t["カテゴリ"] == selected_cat]
    st.table(filtered_todos)
else:
    st.write("タスクはありません。")
