"""
Input Validation Functions
"""

import re
import pandas as pd

def validate_username(username):
    """
    Validate username format and requirements
    
    Args:
        username (str): Username to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters long"
    
    # Check for valid characters (alphanumeric and underscore only)
    if not re.match("^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    # Check if starts with letter
    if not username[0].isalpha():
        return False, "Username must start with a letter"
    
    return True, "Valid username"

def validate_password(password):
    """
    Validate password strength and requirements
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters long"
    
    # Check for at least one letter and one number (basic strength)
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not has_letter:
        return False, "Password must contain at least one letter"
    
    if not has_number:
        return False, "Password must contain at least one number"
    
    return True, "Valid password"

def validate_file_upload(uploaded_file, max_size_mb=200):
    """
    Validate uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        max_size_mb (int): Maximum file size in MB
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not uploaded_file:
        return False, "No file uploaded"
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.1f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
    
    # Check file extension
    allowed_extensions = ['csv', 'xlsx', 'xls', 'json']
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"File type '{file_extension}' not supported. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, "Valid file"

def validate_dataframe(df):
    """
    Validate DataFrame for processing
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if df is None:
        return False, "DataFrame is None"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    if len(df.columns) == 0:
        return False, "DataFrame has no columns"
    
    if len(df) > 1000000:  # 1 million rows limit
        return False, "DataFrame too large (> 1M rows). Please use a smaller dataset"
    
    if len(df.columns) > 1000:  # 1000 columns limit
        return False, "DataFrame has too many columns (> 1000). Please reduce the number of columns"
    
    return True, "Valid DataFrame"

def validate_column_name(column_name):
    """
    Validate column name for database usage
    
    Args:
        column_name (str): Column name to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not column_name:
        return False, "Column name is required"
    
    if len(column_name) > 63:  # PostgreSQL identifier limit
        return False, "Column name too long (> 63 characters)"
    
    # Check for valid characters
    if not re.match("^[a-zA-Z][a-zA-Z0-9_]*$", column_name):
        return False, "Column name must start with letter and contain only letters, numbers, and underscores"
    
    # Check for reserved words (basic list)
    reserved_words = [
        'select', 'from', 'where', 'insert', 'update', 'delete', 'create', 'drop',
        'alter', 'table', 'database', 'index', 'view', 'grant', 'revoke', 'user',
        'order', 'by', 'group', 'having', 'union', 'join', 'inner', 'outer', 'left', 'right'
    ]
    
    if column_name.lower() in reserved_words:
        return False, f"Column name '{column_name}' is a reserved word"
    
    return True, "Valid column name"

def validate_table_name(table_name):
    """
    Validate table name for database usage
    
    Args:
        table_name (str): Table name to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not table_name:
        return False, "Table name is required"
    
    if len(table_name) > 63:  # PostgreSQL identifier limit
        return False, "Table name too long (> 63 characters)"
    
    # Check for valid characters
    if not re.match("^[a-zA-Z][a-zA-Z0-9_]*$", table_name):
        return False, "Table name must start with letter and contain only letters, numbers, and underscores"
    
    return True, "Valid table name"

def validate_query_input(query):
    """
    Validate user query input
    
    Args:
        query (str): User query string
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 1000:
        return False, "Query too long (> 1000 characters)"
    
    # Check for potentially malicious content
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'eval\(',
        r'exec\('
    ]
    
    query_lower = query.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_lower):
            return False, "Query contains potentially malicious content"
    
    return True, "Valid query"

def validate_numeric_input(value, min_val=None, max_val=None):
    """
    Validate numeric input
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        tuple: (is_valid: bool, message: str, converted_value: float/int/None)
    """
    if value is None or value == "":
        return False, "Value is required", None
    
    try:
        # Try to convert to number
        if isinstance(value, str):
            # Remove commas and whitespace
            cleaned_value = value.replace(",", "").strip()
            if "." in cleaned_value:
                converted_value = float(cleaned_value)
            else:
                converted_value = int(cleaned_value)
        else:
            converted_value = value
        
        # Check range
        if min_val is not None and converted_value < min_val:
            return False, f"Value must be at least {min_val}", None
        
        if max_val is not None and converted_value > max_val:
            return False, f"Value must be at most {max_val}", None
        
        return True, "Valid number", converted_value
        
    except (ValueError, TypeError):
        return False, "Value must be a valid number", None

def validate_date_input(date_str):
    """
    Validate date input string
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str, parsed_date: datetime/None)
    """
    if not date_str:
        return False, "Date is required", None
    
    try:
        parsed_date = pd.to_datetime(date_str)
        return True, "Valid date", parsed_date
    except (ValueError, TypeError):
        return False, "Invalid date format. Use YYYY-MM-DD or similar standard format", None

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email (str): Email to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not email:
        return False, "Email is required"
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address too long"
    
    return True, "Valid email"

def sanitize_input(input_str):
    """
    Sanitize user input to prevent basic injection attacks
    
    Args:
        input_str (str): String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(input_str))
    
    # Remove excessive whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()

def validate_connection_params(host, port, database, username, password):
    """
    Validate database connection parameters
    
    Args:
        host (str): Database host
        port (str): Database port
        database (str): Database name
        username (str): Database username
        password (str): Database password
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not all([host, port, database, username, password]):
        return False, "All connection parameters are required"
    
    # Validate host
    if not re.match(r'^[a-zA-Z0-9.-]+$', host):
        return False, "Invalid host format"
    
    # Validate port
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            return False, "Port must be between 1 and 65535"
    except ValueError:
        return False, "Port must be a valid number"
    
    # Validate database name
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', database):
        return False, "Invalid database name format"
    
    # Validate username
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        return False, "Invalid username format"
    
    return True, "Valid connection parameters"