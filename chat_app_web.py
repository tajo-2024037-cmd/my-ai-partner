import streamlit as st
import os
import datetime
import pytz
import google.generativeai as genai  # ここを import google.generativeai に修正

# --- 1. APIキーの設定 (Streamlit Cloud用) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("Streamlitの管理画面で GEMINI_API_KEY を設定してね！")

def get_ai_response(user_input):
    # 1. ルールベース（時刻など）
    if "時間" in user_input or "時刻" in user_input:
        jst = pytz.timezone('Asia/Tokyo')
        now_jst = datetime.datetime.now(jst)
        return f"現在の時刻は、{now_jst.hour}時{now_jst.minute}分です。"

    # 2. Gemini API (安定版の書き方)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"エラーが発生しました: {e}"

# --- Streamlit UI設定 ---
st.set_page_config(page_title="AI Chat", page_icon="🤖")
st.title("🤖 ブラウザ版AIアシスタント")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("メッセージを入力してください"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = get_ai_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
