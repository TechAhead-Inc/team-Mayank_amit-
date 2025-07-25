"""
Authentication UI Components
"""

import streamlit as st
from auth.jwt_manager import generate_jwt_token, get_token_expiration_info, logout_user
from auth.user_manager import register_user, verify_user
from database.connection import create_postgres_connection

def render_authentication():
    """Render authentication interface"""
    st.markdown('<div class="main-header">Data Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown("Please login or create an account to access the dashboard.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_registration_form()

def render_login_form():
    """Render login form"""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login", use_container_width=True)
        
        if submit_login:
            handle_login(login_username, login_password)

def render_registration_form():
    """Render registration form"""
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        reg_username = st.text_input("Username")
        reg_password = st.text_input("Password", type="password")
        reg_password_confirm = st.text_input("Confirm Password", type="password")
        submit_register = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit_register:
            handle_registration(reg_username, reg_password, reg_password_confirm)

def handle_login(username, password):
    """Handle login form submission"""
    if not username or not password:
        st.error("Please enter both username and password")
        return
    
    engine, success, message = create_postgres_connection()
    if not success:
        st.error(f"Database connection failed: {message}")
        return
    
    verify_success, verify_msg = verify_user(engine, username, password)
    if verify_success:
        # Generate JWT token and store in session
        token = generate_jwt_token(username)
        st.session_state.jwt_token = token
        st.session_state.db_engine = engine
        st.success("Successfully logged in!")
        st.rerun()
    else:
        st.error(verify_msg)

def handle_registration(username, password, password_confirm):
    """Handle registration form submission"""
    if not all([username, password, password_confirm]):
        st.error("Please fill in all fields")
        return
    
    if password != password_confirm:
        st.error("Passwords do not match")
        return
    
    engine, success, message = create_postgres_connection()
    if not success:
        st.error(f"Database connection failed: {message}")
        return
    
    register_success, register_msg = register_user(engine, username, password)
    if register_success:
        st.success("Account created successfully! Please login.")
    else:
        st.error(register_msg)

def render_user_info_sidebar(current_user):
    """Render user information in sidebar"""
    st.markdown(f"### Welcome, {current_user}")
    
    # Session info
    if 'jwt_token' in st.session_state:
        token_info = get_token_expiration_info(st.session_state.jwt_token)
        if not token_info['is_expired']:
            hours_left = token_info['hours_left']
            if hours_left > 0:
                st.info(f"Session expires in {hours_left} hours")
            else:
                st.warning("Session expires soon")
        else:
            st.warning("Session expired")
    
    if st.button("Logout", use_container_width=True):
        logout_user()
        st.rerun()
    
    st.markdown("---")

def render_session_status():
    """Render session status information"""
    if 'jwt_token' not in st.session_state:
        return
    
    token_info = get_token_expiration_info(st.session_state.jwt_token)
    
    if token_info['is_expired']:
        st.error("Your session has expired. Please login again.")
        logout_user()
        st.rerun()
    elif token_info['hours_left'] <= 1:
        st.warning(f"Your session will expire in {token_info['hours_left']} hour(s).")

def show_login_required_message():
    """Show message when login is required"""
    st.markdown("""
    <div class="info-box">
        <h3>Authentication Required</h3>
        <p>Please login to access the Data Analytics Dashboard.</p>
        <p>If you don't have an account, you can create one using the Register tab.</p>
    </div>
    """, unsafe_allow_html=True)