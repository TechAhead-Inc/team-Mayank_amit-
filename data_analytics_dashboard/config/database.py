"""
Database Configuration Module
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Database connection configuration
DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv("PG_HOST", "localhost"),
        'port': os.getenv("PG_PORT", "5432"),
        'database': os.getenv("PG_DATABASE"),
        'username': os.getenv("PG_USERNAME"),
        'password': os.getenv("PG_PASSWORD"),
        'driver': 'postgresql+psycopg2'
    },
    'sqlite': {
        'path': ':memory:',  # Default to in-memory SQLite
        'driver': 'sqlite'
    }
}

# Connection pool settings
POOL_CONFIG = {
    'pool_size': 5,
    'max_overflow': 10,
    'pool_timeout': 30,
    'pool_recycle': 3600
}

def get_database_url(db_type='postgresql', **kwargs):
    """
    Generate database URL for SQLAlchemy
    
    Args:
        db_type (str): Database type ('postgresql' or 'sqlite')
        **kwargs: Override configuration parameters
        
    Returns:
        str: Database URL
    """
    if db_type == 'postgresql':
        config = DATABASE_CONFIG['postgresql'].copy()
        config.update(kwargs)
        
        if not all([config['database'], config['username'], config['password']]):
            raise ValueError("Missing required PostgreSQL configuration parameters")
        
        return (f"{config['driver']}://{config['username']}:{config['password']}"
                f"@{config['host']}:{config['port']}/{config['database']}")
    
    elif db_type == 'sqlite':
        config = DATABASE_CONFIG['sqlite'].copy()
        config.update(kwargs)
        return f"sqlite:///{config['path']}"
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def create_database_engine(db_type='postgresql', **kwargs):
    """
    Create SQLAlchemy database engine with connection pooling
    
    Args:
        db_type (str): Database type
        **kwargs: Additional configuration parameters
        
    Returns:
        sqlalchemy.Engine: Database engine
    """
    database_url = get_database_url(db_type, **kwargs)
    
    if db_type == 'postgresql':
        return create_engine(
            database_url,
            poolclass=QueuePool,
            **POOL_CONFIG,
            echo=os.getenv('DEBUG', 'false').lower() == 'true'
        )
    else:
        return create_engine(database_url)

def validate_database_config(db_type='postgresql'):
    """
    Validate database configuration
    
    Args:
        db_type (str): Database type to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if db_type == 'postgresql':
        config = DATABASE_CONFIG['postgresql']
        required_fields = ['database', 'username', 'password']
        
        missing_fields = [field for field in required_fields if not config[field]]
        
        if missing_fields:
            return False, f"Missing PostgreSQL configuration: {', '.join(missing_fields)}"
        
        return True, "PostgreSQL configuration is valid"
    
    elif db_type == 'sqlite':
        return True, "SQLite configuration is valid"
    
    else:
        return False, f"Unsupported database type: {db_type}"