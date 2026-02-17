import streamlit as st
import google.generativeai as genai
import os

# --- 1. APIキーの設定 (Streamlit Cloud用) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("Streamlitの管理画面で GEMINI_API_KEY を設定してね！")

# --- 2. UIデザイン (タイトルサイズを調整) ---
st.set_page_config(page_title="My AI Partner", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-title {
        font-family: 'Hiragino Sans', sans-serif;
        color: #666666;
        text-align: center;
        font-size: 0.9rem; /* サイズを半分程度に調整 */
        font-weight: bold;
        padding-bottom: 8px;
        margin-bottom: 20px;
        border-bottom: 1px solid #f0f0f0;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; padding: 5px 0px !important; }
    </style>
    <div class="main-title">My AI Partner</div>
""", unsafe_allow_html=True)

# モデルの設定 (最新の2.0 Flash-liteを使用)
model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

# --- 3. 会話履歴の管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# サイドバーにクリアボタンを設置
with st.sidebar:
    if st.button("会話履歴をクリア"):
        st.session_state.messages = []
        st.rerun()

# 履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. チャット入力と性格判定 ---
if prompt := st.chat_input("話しかけてみてね..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    p = prompt.lower()
    context = ""
    for m in st.session_state.messages[-2:]:
        context += f"{m['role']}: {m['content']}\n"

    base_rule = "回答はすべて親しみやすいタメ口で。敬語禁止。絵文字は1回答につき1〜2個に絞って。"

    # 性格判定ロジック
    if any(k in p for k in ["なぜ", "理由", "教え", "解説", "方法"]):
        char_setting = f"{base_rule} あなたは【情熱的な先生】。要点を絞って。冒頭：🎓"
    elif any(k in p for k in ["頑張る", "目標", "やる気", "挫折"]):
        char_setting = f"{base_rule} あなたは【熱血コーチ】。短い言葉で力強く応援。冒頭：🔥"
    elif any(k in p for k in ["つまらない", "疲れた", "飽きた", "自由"]):
        char_setting = f"{base_rule} あなたは【自由奔放な旅人】。短い一言で。冒頭：🌍"
    elif any(k in p for k in ["悩み", "悲しい", "相談"]):
        char_setting = f"{base_rule} あなたは【温かい先輩】。現実的な短文で。冒頭：🌸"
    else:
        char_setting = f"{base_rule} あなたは【親友】。短文でノリ良く。冒頭：✨"

    with st.chat_message("assistant"):
        try:
            full_prompt = f"{base_rule}\n\n設定: {char_setting}\n\n会話履歴:\n{context}\n\n最新入力: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.error("ちょっと話しすぎちゃったみたい。1分くらい待ってからまた話しかけてね！")
            else:
                st.error(f"エラーが発生しました: {e}")
