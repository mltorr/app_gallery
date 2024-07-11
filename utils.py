import streamlit as st
import security

def setup_page(page_title):
    st.set_page_config(
        page_title=page_title,
        layout="wide",
    )

    query_params = st.query_params
    if 'code' in query_params:
        security.handle_redirect()

    access_token = st.session_state.get('access_token')

    if access_token:
        user_info = security.get_user_info(access_token)
        st.session_state['user_info'] = user_info
        return True
    else:
        st.title("Welcome to BTG Application Gallery")
        st.write("Please sign-in to use this app.")
        auth_url = security.get_auth_url()
        st.image("btg1.jpg", width=800)  # Replace with your logo image path
        st.markdown(
            "<a href='" + auth_url + "' target='_self'><button style='background-color: #008CBA; color: white; padding: 10px 20px; "
            "text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin-top: 20px; "
            "border: none; border-radius: 4px; cursor: pointer;'>Sign In with Microsoft</button></a>",
            unsafe_allow_html=True,
        )
        st.stop()

def logout():
    security.logout()
