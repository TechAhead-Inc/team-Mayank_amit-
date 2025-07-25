"""
AI package for OpenAI integration and query generation

This package handles all AI-related functionality including
OpenAI API integration, prompt management, and response parsing.
"""

from .openai_client import (
    get_openai_client, 
    generate_sql_from_question, 
    test_openai_connection,
    OpenAIClient
)
from .prompt_manager import (
    create_dynamic_prompt, 
    get_sample_queries,
    create_business_context_prompt,
    detect_business_domain,
    get_domain_specific_examples,
    validate_prompt_parameters
)
from .response_parser import (
    parse_openai_response,
    extract_sql_from_text,
    validate_visualization_type,
    extract_insights_from_response,
    parse_error_response,
    validate_parsed_response
)

__version__ = "1.0.0"
__all__ = [
    # OpenAI Client
    'get_openai_client', 
    'generate_sql_from_question', 
    'test_openai_connection',
    'OpenAIClient',
    # Prompt Management
    'create_dynamic_prompt', 
    'get_sample_queries',
    'create_business_context_prompt',
    'detect_business_domain',
    'get_domain_specific_examples',
    'validate_prompt_parameters',
    # Response Parsing
    'parse_openai_response',
    'extract_sql_from_text',
    'validate_visualization_type',
    'extract_insights_from_response',
    'parse_error_response',
    'validate_parsed_response'
]
