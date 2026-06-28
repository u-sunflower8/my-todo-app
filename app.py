import streamlit as st
import gspread
import requests
import datetime
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
    url = st.secrets["DISCORD"]["WEBHOOK_URL"]
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


import datetime # 一番上のimportに追加してください

# --- 期限チェック関数 ---
def check_deadlines(todos):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    for todo in todos:
        # スプレッドシートの「期限」が文字列なので日付型に変換
        # ※スプレッドシートの形式に合わせて yyyy-mm-dd を調整してください
        due_date = datetime.datetime.strptime(todo["期限"], '%Y-%m-%d').date()
        
        if due_date == tomorrow:
            # 既に通知済みかどうかの管理が必要ですが、まずはシンプルに通知！
            send_discord_notification(f"⚠️ 期限通知: '{todo['タスク名']}' が明日({due_date})期限です！")

# --- アプリの処理内で実行 ---
# サイドバーの下や一覧表示の前に以下を置くと、アプリを開くたびにチェックされます
if st.sidebar.button("期限チェック実行"):
    check_deadlines(all_todos)
    st.sidebar.success("チェック完了！")

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
