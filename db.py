import streamlit as st
from supabase import create_client

url = st.secrets["SUPABASE_URL"].strip()
key = st.secrets["SUPABASE_KEY"].strip()

st.sidebar.write("Supabase URL:", url)
st.sidebar.write("URL ends correctly:", url.endswith(".supabase.co"))

@st.cache_resource
def get_supabase():
    return create_client(url, key)

supabase = get_supabase()
