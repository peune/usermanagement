import requests
import streamlit as st
from jose import JWTError, jwt
import os
from datetime import datetime

from config import settings

FASTAPI_URL = settings.MAIN_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        st.error("Token expired. Please log in again.")
        st.stop()
    except jwt.PyJWTError:
        st.error("Invalid token. Access denied.")
        st.stop()

# --- Authentication Functions ---
def check_auth():    

    query_params = st.experimental_get_query_params()
    if "token" not in query_params:
        return False
    
    token = query_params["token"][0]
    user_data = verify_token(token)
    st.session_state["token"] = token
    st.session_state["user"] = user_data

    # add verify auth later if needed
    return True

def logout():
    """Clear session and FastAPI cookie"""
    if "token" in st.session_state:
        requests.post(f"http://fastapi:8000/logout", headers={"Authorization": f"Bearer {st.session_state.token}"})
    st.session_state.clear()

# --- Main App ---
def main():
    st.set_page_config(page_title="Data Analysis", layout="wide")
    
    # Force authentication
    if not check_auth():
        st.warning("Please log in to access this page.")
        st.markdown(f'<meta http-equiv="refresh" content="0; url={FASTAPI_URL}/login">', unsafe_allow_html=True)
        st.stop()
    
    # Authenticated UI
    st.title("Data Analysis Dashboard")
    
    user_name = st.session_state["user"]["name"]
    st.write(f"Welcome, {user_name}")
    
    # Logout button
    if st.button("Logout"):
        logout()
        st.markdown(f'<meta http-equiv="refresh" content="0; url={FASTAPI_URL}/">', unsafe_allow_html=True)
        st.stop()
    
    # --- Your Data Analysis Code Here ---
    st.line_chart([1, 2, 3, 4, 5])

if __name__ == "__main__":
    main()