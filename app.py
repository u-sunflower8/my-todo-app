import streamlit as st
import gspread
import requests  # ★これが必要！
from oauth2client.service_account import ServiceAccountCredentials

# ファイルの先頭、import の直後に入れる
try:
    import requests
    st.write("requestsは読み込めています！")
except ImportError:
    st.error("requestsが見つかりません！requirements.txtを確認してください。")

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
        # スプレッドシートへ書き込み
        sheet.append_row([title, str(due), "未", priority, category])
        # Discord通知
        send_discord_notification(f"📝 新しいタスク: {title} ({category})")
        st.success("追加しました！")
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
