"""
User Management Module - Authentication and Registration
"""

import bcrypt
import streamlit as st
from sqlalchemy import text
from utils.validators import validate_username, validate_password

def create_users_table(engine):
    """
    Create users table if it doesn't exist
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating users table: {str(e)}")
        return False

def hash_password(password):
    """
    Hash password using bcrypt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify password against hash
    
    Args:
        password (str): Plain text password
        hashed_password (str): Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(engine, username, password):
    """
    Register a new user with hashed password
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username
        password (str): Plain text password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate input
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            return False, username_msg
        
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            return False, password_msg
        
        # Check if username already exists
        if user_exists(engine, username):
            return False, "Username already exists"
        
        # Hash password and create user
        password_hash = hash_password(password)
        
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"),
                {"username": username, "password_hash": password_hash}
            )
            conn.commit()
        
        return True, "User registered successfully"
        
    except Exception as e:
        return False, f"Error registering user: {str(e)}"

def verify_user(engine, username, password):
    """
    Verify user credentials and update last login
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username
        password (str): Plain text password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT password_hash, is_active FROM users WHERE username = :username"),
                {"username": username}
            )
            user = result.fetchone()
            
            if not user:
                return False, "User not found"
            
            if not user[1]:  # is_active
                return False, "Account is disabled"
            
            if verify_password(password, user[0]):
                # Update last login
                conn.execute(
                    text("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = :username"),
                    {"username": username}
                )
                conn.commit()
                return True, "Login successful"
            else:
                return False, "Invalid password"
                
    except Exception as e:
        return False, f"Error verifying user: {str(e)}"

def user_exists(engine, username):
    """
    Check if username already exists
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username to check
        
    Returns:
        bool: True if user exists, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM users WHERE username = :username"),
                {"username": username}
            )
            count = result.fetchone()[0]
            return count > 0
    except Exception as e:
        st.error(f"Error checking user existence: {str(e)}")
        return False

def get_user_info(engine, username):
    """
    Get user information
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username
        
    Returns:
        dict or None: User information if found, None otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, username, created_at, last_login, is_active FROM users WHERE username = :username"),
                {"username": username}
            )
            user = result.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'created_at': user[2],
                    'last_login': user[3],
                    'is_active': user[4]
                }
    except Exception as e:
        st.error(f"Error getting user info: {str(e)}")
    
    return None

def update_user_status(engine, username, is_active):
    """
    Update user active status
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username
        is_active (bool): Active status
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE users SET is_active = :is_active WHERE username = :username"),
                {"username": username, "is_active": is_active}
            )
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating user status: {str(e)}")
        return False

def change_password(engine, username, old_password, new_password):
    """
    Change user password
    
    Args:
        engine: SQLAlchemy database engine
        username (str): Username
        old_password (str): Current password
        new_password (str): New password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verify current password
        verify_success, verify_msg = verify_user(engine, username, old_password)
        if not verify_success:
            return False, "Current password is incorrect"
        
        # Validate new password
        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            return False, password_msg
        
        # Update password
        new_password_hash = hash_password(new_password)
        
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE username = :username"),
                {"username": username, "password_hash": new_password_hash}
            )
            conn.commit()
        
        return True, "Password changed successfully"
        
    except Exception as e:
        return False, f"Error changing password: {str(e)}"