import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Samarasa", page_icon="❤️", layout="centered")
st.title("❤️ Samarasa")
st.markdown("### AI Relationship Counselor for Couples")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "token" not in st.session_state:
    st.session_state.token = None
if "messages" not in st.session_state:
    st.session_state.messages = []

SYSTEM_PROMPT = """You are Samarasa, a warm and wise AI counselor for couples. You support two partners. Be empathetic, balanced, and practical. Help with communication, intimacy, and connection. Use "Psst" suggestions when appropriate. Never take sides."""

if not st.session_state.token:
    st.subheader("Login or Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.user_id = res.user.id
                    st.session_state.token = res.session.access_token
                    st.success("Logged in!")
                    st.rerun()
            except Exception as e:
                st.error(f"Login error: {e}")

    with col2:
        if st.button("Sign Up"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Check your email to confirm!")
            except Exception as e:
                st.error(f"Sign up error: {e}")
else:
    st.success(f"Logged in as {st.session_state.user_id}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Talk to Samarasa...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")
            response = client.chat.completions.create(
                model="grok-3",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]],
                max_tokens=500,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()