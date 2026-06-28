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

# 3. 画面の作成
st.title("最強のToDoアプリ")

# --- タスク入力フォーム ---
with st.form("todo_input"):
    st.subheader("新しいタスクを追加")
    new_task = st.text_input("なにをしますか？")
    new_date = st.date_input("期限日を選んでください")
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    submit = st.form_submit_button("追加")

    if submit:
        if new_task:
            # 1:タスク名, 2:期限, 3:完了フラグ, 4:優先度, 5:カテゴリ
            sheet.append_row([new_task, str(new_date), "未着手", priority, category])
            send_discord_notification(f"🆕 タスク追加: {new_task} (期限: {new_date}, 優先度: {priority})")
            st.success("追加しました！")
            st.rerun()
        else:
            st.error("タスクの内容を入力してください。")

# 4. データ取得と並び替え (ここを差し替えてください)
data = sheet.get_all_values()
if len(data) > 1:
    headers = data[0]
    # データ行を読み込む際、列の数がヘッダーと合わない行を自動で無視するようにします
    all_data = []
    for row in data[1:]:
        if len(row) == len(headers):
            all_data.append(row)
        elif len(row) < len(headers):
            # 足りない分を空欄で埋める
            row.extend([''] * (len(headers) - len(row)))
            all_data.append(row)
            
    df = pd.DataFrame(all_data, columns=headers)
    
    # ここから下は同じです
    df = df[df['完了フラグ'] == '未着手']
    priority_map = {"高": 1, "中": 2, "低": 3}
    df['p_num'] = df['優先度'].map(priority_map)
    df = df.sort_values(by=['p_num', '期限'])
    
    display_df = df[['タスク名', '期限', '優先度', 'カテゴリ']]
    st.subheader("未完了タスク一覧 (優先度順)")
    st.table(display_df)
else:
    st.write("タスクはまだ登録されていません。")

# 6. アプリを開いた瞬間に自動チェック（1日1回だけ実行）
if 'checked' not in st.session_state:
    st.session_state['checked'] = True
    # 自動チェック処理
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    for _, row in df.iterrows():
        try:
            due_date = datetime.datetime.strptime(row['期限'], '%Y-%m-%d').date()
            if due_date == tomorrow:
                send_discord_notification(f"⚠️ 期限通知: '{row['タスク名']}' が明日({due_date})期限です！")
        except:
            continue
