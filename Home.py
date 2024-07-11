import streamlit as st
import utils
import security

utils.setup_page("Home")

st.title("Welcome to BTG Application Gallery")
st.write("Please select an application from the sidebar you wish to run.")
auth_url = security.get_auth_url()
st.image("btg1.jpg", width=800)  # Replace with your logo image path


with st.sidebar:
    if st.button("Logout"):
        utils.logout()
        st.rerun()
