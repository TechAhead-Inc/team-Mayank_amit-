"""
Authentication package for user management and JWT tokens

This package handles all authentication-related functionality including
user registration, login, JWT token management, and authentication UI.
"""

from .jwt_manager import (
    generate_jwt_token, 
    verify_jwt_token, 
    get_current_user,
    get_token_expiration_info,
    logout_user,
    is_token_valid
)
from .user_manager import (
    register_user, 
    verify_user, 
    create_users_table,
    user_exists,
    get_user_info,
    change_password
)
from .auth_ui import (
    render_authentication, 
    render_user_info_sidebar,
    handle_login,
    handle_registration,
    render_session_status
)

__version__ = "1.0.0"
__all__ = [
    # JWT Management
    'generate_jwt_token', 
    'verify_jwt_token', 
    'get_current_user',
    'get_token_expiration_info',
    'logout_user',
    'is_token_valid',
    # User Management
    'register_user', 
    'verify_user', 
    'create_users_table',
    'user_exists',
    'get_user_info',
    'change_password',
    # UI Components
    'render_authentication', 
    'render_user_info_sidebar',
    'handle_login',
    'handle_registration',
    'render_session_status'
]
