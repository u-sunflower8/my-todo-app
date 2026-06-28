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

# --- 通知関数 ---
def send_discord_notification(message):
    url = st.secrets["DISCORD"]["WEBHOOK_URL"]
    payload = {"content": message}
    response = requests.post(url, json=payload)
    return response.status_code, response.text

def check_deadlines(todos):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    # 読み込んだデータの「項目名」を画面に表示して確認する
    if todos:
        st.sidebar.write("読み込んだ列名:", todos[0].keys())
    
    found = False
    for todo in todos:
        # strip() を使うことで、もし「期限 」のようにスペースが入っていても無視します
        due_val = todo.get("期限") or todo.get(" 期限") 
        
        try:
            due_date = datetime.datetime.strptime(due_val, '%Y-%m-%d').date()
            if due_date == tomorrow:
                send_discord_notification(f"⚠️ 期限通知: '{todo['タスク名']}' が明日({due_date})期限です！")
                found = True
        except:
            continue
    return found
    
# --- メイン画面 ---
st.title("ToDoリスト")

# フォーム
with st.form("add_todo"):
    title = st.text_input("タスク名")
    due = st.date_input("期限")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    submit = st.form_submit_button("追加")

if submit:
    sheet.append_row([title, str(due), "未", priority, category])
    send_discord_notification(f"📝 新タスク: {title} ({category})")
    st.success("追加完了！")
    st.rerun()

# 期限チェックボタン
all_todos = sheet.get_all_records()
if st.sidebar.button("期限をチェックする"):
    if check_deadlines(all_todos):
        st.sidebar.success("期限が近いタスクを通知しました！")
    else:
        st.sidebar.info("明日が期限のタスクはありませんでした。")

st.subheader("タスク一覧")
st.table(all_todos)
