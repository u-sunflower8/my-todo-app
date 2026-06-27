# --- 登録フォーム ---
with st.form("add_todo"):
    title = st.text_input("タスク名")
    due = st.date_input("期限")
    # 追加：選択肢を作る
    priority = st.selectbox("優先度", ["高", "中", "低"])
    category = st.selectbox("カテゴリ", ["仕事", "プライベート", "買い物", "その他"])
    
    submit = st.form_submit_button("追加")
    
    if submit:
        # スプレッドシートへ書き込む行を5項目に増やす
        sheet.append_row([title, str(due), "未", priority, category])
        st.success("追加しました！")
        st.rerun()
