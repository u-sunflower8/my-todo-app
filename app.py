import streamlit as st
import gspread
import requests
import datetime
from oauth2client.service_account import ServiceAccountCredentials

# --- 設定 ---
creds_dict = st.secrets["GOOGLE_SHEETS"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
SHEET_ID = "101hhNwt1VrR0fn3me63ifsduMqelnVIrY1ozr_Ul74w"
sheet = client.open_by_key(SHEET_ID).sheet1

# --- 通知・チェック関数 ---
def send_discord_notification(message):
    url = st.secrets["DISCORD"]["WEBHOOK_URL"]
    requests.post(url, json={"content": message})

# --- データ取得の強制修正 ---
data = sheet.get_all_values()
# 1行目をヘッダーとする（A, B, C... ではなく「タスク名」などと認識させる）
headers = data[0]
all_todos = []
for row in data[1:]:
    # 空行は飛ばす
    if not any(row): continue
    # 辞書型に変換（これで「期限」というキーが確実に使えるようになります）
    all_todos.append(dict(zip(headers, row)))

# --- 期限チェック機能 ---
def check_deadlines(todos):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    found = False
    for todo in todos:
        try:
            # 辞書から「期限」を取得（もし見つからなければエラーを防ぐ）
            due_str = todo.get("期限", "")
            due_date = datetime.datetime.strptime(due_str, '%Y-%m-%d').date()
            if due_date == tomorrow:
                send_discord_notification(f"⚠️ 期限通知: '{todo.get('タスク名')}' が明日({due_date})期限です！")
                found = True
        except:
            continue
    return found

# --- UI ---
st.title("ToDoリスト")
if st.sidebar.button("期限をチェックする"):
    if check_deadlines(all_todos):
        st.sidebar.success("通知しました！")
    else:
        st.sidebar.info("明日期限のタスクはありません。")

st.table(all_todos)
