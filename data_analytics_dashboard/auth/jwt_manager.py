"""
JWT Token Management Module
"""

import jwt
import streamlit as st
from datetime import datetime, timedelta
from config.settings import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

def generate_jwt_token(username):
    """
    Generate a JWT token for the user
    
    Args:
        username (str): Username for token generation
        
    Returns:
        str: JWT token
    """
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """
    Verify and decode JWT token
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        str or None: Username if token is valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user():
    """
    Get current authenticated user from session state
    
    Returns:
        str or None: Current username if authenticated, None otherwise
    """
    if 'jwt_token' in st.session_state:
        username = verify_jwt_token(st.session_state.jwt_token)
        if username:
            return username
    return None

def get_token_expiration_info(token):
    """
    Get token expiration information
    
    Args:
        token (str): JWT token
        
    Returns:
        dict: Token expiration info with hours_left and is_expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        exp_time = datetime.fromtimestamp(payload['exp'])
        time_left = exp_time - datetime.now()
        
        return {
            'hours_left': int(time_left.total_seconds() // 3600),
            'is_expired': time_left.total_seconds() <= 0,
            'exp_time': exp_time
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {
            'hours_left': 0,
            'is_expired': True,
            'exp_time': None
        }

def logout_user():
    """Clear all session state to log out user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def is_token_valid(token):
    """
    Check if token is valid without decoding
    
    Args:
        token (str): JWT token to check
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    return verify_jwt_token(token) is not None

def refresh_token_if_needed(token, threshold_hours=2):
    """
    Refresh token if it's close to expiration
    
    Args:
        token (str): Current JWT token
        threshold_hours (int): Hours before expiration to refresh
        
    Returns:
        str or None: New token if refreshed, None if not needed or failed
    """
    token_info = get_token_expiration_info(token)
    
    if not token_info['is_expired'] and token_info['hours_left'] <= threshold_hours:
        username = verify_jwt_token(token)
        if username:
            return generate_jwt_token(username)
    
    return None