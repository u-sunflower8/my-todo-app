import streamlit as st

st.title("デバッグ：Secrets確認")

# Secretsの中身をそのまま表示（個人情報は伏せられますが、接続テストには使えます）
if "GOOGLE_SHEETS" in st.secrets:
    st.write("Secretsは読み込めています！")
    # 中身が空でないか確認
    st.write("キーの数:", len(st.secrets["GOOGLE_SHEETS"]))
else:
    st.error("Secretsが見つかりません！Streamlitの管理画面で設定を確認してください。")
