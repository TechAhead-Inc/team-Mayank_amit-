"""
OpenAI API Client and Query Generation
"""

import streamlit as st
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

class OpenAIClient:
    """OpenAI API client for SQL query generation"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in configuration")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_TOKENS
        self.temperature = OPENAI_TEMPERATURE
    
    def generate_sql_query(self, question, prompt, table_info, attempt=1):
        """
        Generate SQL query from natural language question
        
        Args:
            question (str): User's natural language question
            prompt (str): System prompt with table context
            table_info (str): Table information string
            attempt (int): Attempt number for different strategies
            
        Returns:
            str or None: Generated response text
        """
        try:
            if attempt == 1:
                enhanced_prompt = self._create_primary_prompt(prompt, table_info, question)
            else:
                enhanced_prompt = self._create_fallback_prompt(prompt, table_info, question)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert data analyst and SQL specialist."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def _create_primary_prompt(self, base_prompt, table_info, question):
        """Create primary prompt for first attempt"""
        return f"""
        {base_prompt}
        
        Table Information: {table_info}
        
        IMPORTANT: You must be flexible and creative in interpreting user questions. Even if the exact columns or data the user mentions don't exist, try to:
        1. Find similar or related columns that could provide insights
        2. Suggest alternative queries that answer related questions
        3. Provide the best possible analysis with available data
        
        For example:
        - If user asks about "sales" but only "revenue" column exists, use revenue
        - If user asks about "customer names" but only "customer_id" exists, show customer_id analysis
        - If user asks about "daily trends" but only monthly data exists, show monthly trends
        - If user asks about "products" but table has "items", use items instead
        
        Always try to provide SOME useful query, even if it's not exactly what was asked.
        
        CRITICAL: Format your response EXACTLY like this:
        SQL_QUERY: SELECT column1, column2 FROM table_name WHERE condition
        VIZ_TYPE: bar_chart
        VIZ_REASON: This visualization works best because...
        INSIGHTS: Business insights this query provides
        
        DO NOT use markdown code blocks (```sql) in the SQL_QUERY line. Just provide the raw SQL after "SQL_QUERY:"
        
        Question: {question}
        """
    
    def _create_fallback_prompt(self, base_prompt, table_info, question):
        """Create fallback prompt for second attempt"""
        return f"""
        {base_prompt}
        
        Table Information: {table_info}
        
        The user asked: "{question}"
        
        Since the previous query didn't work, let's explore the data and provide useful insights.
        
        Create a query that:
        1. Shows interesting patterns in the available data
        2. Provides useful business insights
        3. Uses the actual column names available
        4. Focuses on data exploration and discovery
        
        Choose from these exploratory approaches:
        - Show distribution of categorical columns
        - Show statistics of numeric columns  
        - Show relationships between columns
        - Show top/bottom records
        - Show data quality insights
        
        Format your response as:
        SQL_QUERY: [exploratory query using available columns]
        VIZ_TYPE: [recommended visualization]
        VIZ_REASON: [why this helps understand the data]
        INSIGHTS: [what business insights this query can provide]
        """
    
    def test_connection(self):
        """
        Test OpenAI API connection
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, please respond with 'Connection successful'"}],
                max_tokens=10,
                temperature=0
            )
            
            if "successful" in response.choices[0].message.content.lower():
                return True, "OpenAI API connection successful"
            else:
                return False, "Unexpected response from OpenAI API"
                
        except Exception as e:
            return False, f"OpenAI API connection failed: {str(e)}"
    
    def validate_query_generation(self, question):
        """
        Validate if question is suitable for query generation
        
        Args:
            question (str): User question
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        if not question or len(question.strip()) < 5:
            return False, "Question is too short or empty"
        
        if len(question) > 500:
            return False, "Question is too long (max 500 characters)"
        
        # Check for potentially problematic content
        problematic_keywords = ["hack", "exploit", "bypass", "inject"]
        question_lower = question.lower()
        
        for keyword in problematic_keywords:
            if keyword in question_lower:
                return False, f"Question contains inappropriate content: {keyword}"
        
        return True, "Question is valid for processing"
    
    def get_usage_stats(self):
        """
        Get current usage statistics (placeholder for future implementation)
        
        Returns:
            dict: Usage statistics
        """
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "requests_made": 0,  # Would track in production
            "tokens_used": 0     # Would track in production
        }

# Global client instance
_openai_client = None

def get_openai_client():
    """
    Get global OpenAI client instance
    
    Returns:
        OpenAIClient: OpenAI client instance
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client

def generate_sql_from_question(question, prompt, table_info, attempt=1):
    """
    Generate SQL query from natural language question (convenience function)
    
    Args:
        question (str): User's natural language question
        prompt (str): System prompt with table context
        table_info (str): Table information string
        attempt (int): Attempt number
        
    Returns:
        str or None: Generated response text
    """
    client = get_openai_client()
    return client.generate_sql_query(question, prompt, table_info, attempt)

def test_openai_connection():
    """
    Test OpenAI API connection (convenience function)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        client = get_openai_client()
        return client.test_connection()
    except Exception as e:
        return False, f"Failed to initialize OpenAI client: {str(e)}"