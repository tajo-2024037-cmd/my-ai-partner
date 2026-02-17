import streamlit as st
import google.generativeai as genai
import os

# --- 1. APIキーの設定 ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("StreamlitのSecretsに GEMINI_API_KEY を設定してください。")

# --- 2. UIデザイン（タイトルをコンパクトに） ---
st.set_page_config(page_title="My AI Partner", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-title {
        font-family: 'Hiragino Sans', sans-serif;
        color: #666666;
        text-align: center;
        font-size: 0.9rem; /* タイトルサイズを以前の半分に固定 */
        font-weight: bold;
        padding-bottom: 8px;
        margin-bottom: 20px;
        border-bottom: 1px solid #f0f0f0;
    }
    .stChatMessage { background-color: transparent !important; border: none !important; padding: 5px 0px !important; }
    </style>
    <div class="main-title">My AI Partner</div>
""", unsafe_allow_html=True)

# --- 3. モデルの設定 (最新の Gemini 2.5 Flash を指定) ---
# 2.5シリーズは安定性が高く、無料枠のエラー(429)も出にくい設計です。
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 4. 会話履歴の管理とクリア機能 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("Settings")
    if st.button("会話履歴をリセット"):
        st.session_state.messages = []
        st.rerun()

# 履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. 入力と最新の性格判定 ---
if prompt := st.chat_input("メッセージを入力..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 履歴をコンテキストとして追加（直近2件）
    context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:-1]])

    # 共通ルール（絵文字抑制）
    base_rule = "回答はタメ口で。敬語禁止。絵文字は1回答につき1つまで。短文で答えて。"

    # 性格判定
    p = prompt.lower()
    if any(k in p for k in ["なぜ", "方法", "教え"]):
        char_setting = f"{base_rule} 知的な先生として簡潔に。 冒頭:🎓"
    elif any(k in p for k in ["目標", "頑張る", "やる気"]):
        char_setting = f"{base_rule} 熱血コーチとして一言で励まして。 冒頭:🔥"
    elif any(k in p for k in ["疲れ", "自由", "旅"]):
        char_setting = f"{base_rule} 自由な旅人として。悟ったような短文で。 冒頭:🌍"
    elif any(k in p for k in ["悩み", "相談", "悲しい"]):
        char_setting = f"{base_rule} 優しい先輩として寄り添って。 冒頭:🌸"
    else:
        char_setting = f"{base_rule} 仲の良い親友として。 冒頭:✨"

    with st.chat_message("assistant"):
        try:
            full_prompt = f"{char_setting}\n\n会話履歴:\n{context}\n\n入力: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error("現在、AIが少し休憩しているみたい。1分後にまた話しかけてみて！")
