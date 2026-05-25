import streamlit as st
from supabase import create_client

# Read Supabase credentials from Streamlit secrets.
# Do not display these values in the app UI.
url = st.secrets["SUPABASE_URL"].strip()
key = st.secrets["SUPABASE_KEY"].strip()

@st.cache_resource
def get_supabase():
    return create_client(url, key)

supabase = get_supabase()
