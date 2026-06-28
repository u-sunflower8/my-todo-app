import streamlit as st
import gspread
import requests
import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 1. 接続設定
creds_dict = st.secrets["GOOGLE_SHEETS"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = "101hhNwt1VrR0fn3me63ifsduMqelnVIrY1ozr_Ul74w"
sheet = client.open_by_key(SHEET_ID).sheet1

# 2. 通知用・チェック用の関数
def send_discord_notification(message):
    url = st.secrets["DISCORD"]["WEBHOOK_URL"]
    requests.post(url, json={"content": message})

def check_deadlines(todos):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    found = False
    for todo in todos:
        try:
            # 1列目(0)をタスク名、2列目(1)を期限として取得
            values = list(todo.values())
            task_name = values[0]
            due_str = values[1]
            due_date = datetime.datetime.strptime(due_str, '%Y-%m-%d').date()
            if due_date == tomorrow:
                send_discord_notification(f"⚠️ 期限通知: '{task_name}' が明日({due_date})期限です！")
                found = True
        except:
            continue
    return found

# 3. 画面の作成（ここからが「書くところ」です）
st.title("🚀 最強のToDoアプリ")

# --- タスク入力フォーム ---
with st.form("todo_input"):
    st.subheader("📝 新しいタスクを追加")
    new_task = st.text_input("なにをしますか？")
    new_date = st.date_input("期限日を選んでください")
    submit = st.form_submit_button("スプレッドシートに保存")

    if submit:
        if new_task:
            # シートに書き込む（1列目:タスク名, 2列目:期限, 3列目:状態）
            sheet.append_row([new_task, str(new_date), "未着手"])
            send_discord_notification(f"🆕 タスクが追加されました: {new_task} (期限: {new_date})")
            st.success("追加しました！")
            st.rerun() # 画面を更新
        else:
            st.error("タスクの内容を入力してください。")

# 4. データの取得と期限チェック
data = sheet.get_all_values()
if len(data) > 0:
    headers = data[0]
    all_todos = [dict(zip(headers, row)) for row in data[1:] if any(row)]
else:
    all_todos = []

# サイドバーのボタン
if st.sidebar.button("⏰ 明日の期限をチェック"):
    if all_todos:
        if check_deadlines(all_todos):
            st.sidebar.success("期限が近いタスクをDiscordに通知しました！")
        else:
            st.sidebar.info("明日が期限のタスクはありません。")
    else:
        st.sidebar.warning("タスクがまだありません。")

# 5. 一覧表示
st.subheader("📊 現在のタスク一覧")
if all_todos:
    st.table(all_todos)
else:
    st.write("タスクはまだ登録されていません。上のフォームから追加してください。")
