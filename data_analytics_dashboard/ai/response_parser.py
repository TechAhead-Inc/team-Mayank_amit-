"""
AI Response Parsing Module
"""

import re

def parse_openai_response(response_text):
    """
    Parse OpenAI response to extract SQL and visualization info
    
    Args:
        response_text (str): Raw response from OpenAI
        
    Returns:
        tuple: (sql_query, viz_type, viz_reason, insights)
    """
    if not response_text:
        return "", "bar_chart", "Default visualization", ""
    
    lines = response_text.split('\n')
    sql_query = ""
    viz_type = "bar_chart"
    viz_reason = "Default visualization"
    insights = ""
    
    # First, try to find structured response
    for line in lines:
        if line.startswith('SQL_QUERY:'):
            sql_query = line.replace('SQL_QUERY:', '').strip()
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        elif line.startswith('VIZ_TYPE:'):
            viz_type = line.replace('VIZ_TYPE:', '').strip()
        elif line.startswith('VIZ_REASON:'):
            viz_reason = line.replace('VIZ_REASON:', '').strip()
        elif line.startswith('INSIGHTS:'):
            insights = line.replace('INSIGHTS:', '').strip()
    
    # If structured response not found, try alternative parsing
    if not sql_query:
        sql_query = extract_sql_from_text(response_text)
    
    # Clean and validate SQL query
    if sql_query:
        sql_query = clean_extracted_sql(sql_query)
    
    # Validate visualization type
    viz_type = validate_visualization_type(viz_type)
    
    return sql_query, viz_type, viz_reason, insights

def extract_sql_from_text(text):
    """
    Extract SQL query from unstructured text
    
    Args:
        text (str): Text containing SQL query
        
    Returns:
        str: Extracted SQL query
    """
    # Try to find SQL in code blocks first
    sql_match = re.search(r'```sql\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    
    # Try to find SQL_QUERY: pattern anywhere in text
    sql_query_match = re.search(r'SQL_QUERY:\s*(.*?)(?:\n|$)', text, re.IGNORECASE)
    if sql_query_match:
        sql_query = sql_query_match.group(1).strip()
        return sql_query.replace('```sql', '').replace('```', '').strip()
    
    # Look for SELECT statements directly
    select_match = re.search(r'(SELECT.*?(?:;|$))', text, re.DOTALL | re.IGNORECASE)
    if select_match:
        sql_query = select_match.group(1).strip()
        return sql_query.rstrip(';').strip()
    
    # Try to find any SQL-like pattern
    sql_pattern = re.search(r'\b(SELECT|WITH)\b.*', text, re.IGNORECASE | re.DOTALL)
    if sql_pattern:
        # Extract until we hit a non-SQL pattern
        sql_text = sql_pattern.group(0)
        # Stop at common delimiters
        for delimiter in ['\n\n', 'VIZ_TYPE:', 'INSIGHTS:', 'Explanation:', 'Note:']:
            if delimiter in sql_text:
                sql_text = sql_text.split(delimiter)[0]
        return sql_text.strip().rstrip(';')
    
    return ""

def clean_extracted_sql(sql):
    """
    Clean extracted SQL query
    
    Args:
        sql (str): Raw SQL query
        
    Returns:
        str: Cleaned SQL query
    """
    if not sql:
        return ""
    
    # Remove any remaining markdown formatting
    sql = sql.replace('```sql', '').replace('```', '')
    
    # Remove extra whitespace and newlines
    sql = ' '.join(sql.split())
    
    # Remove trailing semicolon if present
    sql = sql.rstrip(';').strip()
    
    # Validate that it looks like SQL
    if not sql.upper().strip().startswith(('SELECT', 'WITH', 'SHOW')):
        # If it doesn't look like SQL, try to find a SELECT statement within it
        select_match = re.search(r'(SELECT.*?)(?:\s*(?:VIZ_TYPE|VIZ_REASON|ALTERNATIVE|INSIGHTS|$))', 
                               sql, re.DOTALL | re.IGNORECASE)
        if select_match:
            sql = select_match.group(1).strip()
    
    return sql

def validate_visualization_type(viz_type):
    """
    Validate and normalize visualization type
    
    Args:
        viz_type (str): Visualization type from AI response
        
    Returns:
        str: Valid visualization type
    """
    # Valid visualization types
    valid_types = [
        'bar_chart', 'line_chart', 'pie_chart', 'scatter_plot', 
        'histogram', 'box_plot', 'heatmap', 'table'
    ]
    
    # Normalize input
    viz_type = viz_type.lower().strip()
    
    # Handle common variations
    type_mappings = {
        'bar': 'bar_chart',
        'column': 'bar_chart',
        'line': 'line_chart',
        'trend': 'line_chart',
        'pie': 'pie_chart',
        'donut': 'pie_chart',
        'scatter': 'scatter_plot',
        'scatterplot': 'scatter_plot',
        'hist': 'histogram',
        'distribution': 'histogram',
        'box': 'box_plot',
        'boxplot': 'box_plot',
        'heat': 'heatmap',
        'correlation': 'heatmap'
    }
    
    # Check direct match
    if viz_type in valid_types:
        return viz_type
    
    # Check mappings
    for key, value in type_mappings.items():
        if key in viz_type:
            return value
    
    # Default fallback
    return 'bar_chart'

def extract_insights_from_response(response_text):
    """
    Extract business insights from AI response
    
    Args:
        response_text (str): AI response text
        
    Returns:
        str: Extracted insights
    """
    insights_patterns = [
        r'INSIGHTS?:\s*(.*?)(?:\n\n|$)',
        r'Business insights?:\s*(.*?)(?:\n\n|$)',
        r'Key findings?:\s*(.*?)(?:\n\n|$)',
        r'Analysis:\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in insights_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return ""

def parse_error_response(response_text, original_query):
    """
    Parse AI response for error recovery suggestions
    
    Args:
        response_text (str): AI response text
        original_query (str): Original user query that failed
        
    Returns:
        dict: Error recovery information
    """
    return {
        'alternative_sql': extract_sql_from_text(response_text),
        'explanation': extract_explanation_from_response(response_text),
        'suggestions': extract_suggestions_from_response(response_text),
        'original_query': original_query
    }

def extract_explanation_from_response(response_text):
    """
    Extract explanation from AI response
    
    Args:
        response_text (str): AI response text
        
    Returns:
        str: Extracted explanation
    """
    explanation_patterns = [
        r'EXPLANATION:\s*(.*?)(?:\n\n|$)',
        r'Explanation:\s*(.*?)(?:\n\n|$)',
        r'Why this works:\s*(.*?)(?:\n\n|$)',
        r'Changes made:\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in explanation_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return ""

def extract_suggestions_from_response(response_text):
    """
    Extract alternative suggestions from AI response
    
    Args:
        response_text (str): AI response text
        
    Returns:
        list: List of suggestions
    """
    suggestions_patterns = [
        r'SUGGESTIONS?:\s*(.*?)(?:\n\n|$)',
        r'Alternative questions?:\s*(.*?)(?:\n\n|$)',
        r'Try asking:\s*(.*?)(?:\n\n|$)',
        r'You could also:\s*(.*?)(?:\n\n|$)'
    ]
    
    for pattern in suggestions_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
        if match:
            suggestions_text = match.group(1).strip()
            # Split suggestions by common delimiters
            suggestions = []
            for delimiter in ['\n-', '\n•', '\n*', ',', ';']:
                if delimiter in suggestions_text:
                    suggestions = [s.strip() for s in suggestions_text.split(delimiter) if s.strip()]
                    break
            
            if not suggestions:
                suggestions = [suggestions_text]
            
            return suggestions[:5]  # Return max 5 suggestions
    
    return []

def validate_parsed_response(sql_query, viz_type, viz_reason, insights):
    """
    Validate parsed response components
    
    Args:
        sql_query (str): Parsed SQL query
        viz_type (str): Parsed visualization type
        viz_reason (str): Parsed visualization reason
        insights (str): Parsed insights
        
    Returns:
        tuple: (is_valid: bool, validation_message: str)
    """
    issues = []
    
    # Validate SQL query
    if not sql_query:
        issues.append("No SQL query found in response")
    elif len(sql_query) < 10:
        issues.append("SQL query appears too short")
    elif not sql_query.upper().strip().startswith(('SELECT', 'WITH')):
        issues.append("SQL query doesn't start with SELECT or WITH")
    
    # Validate visualization type
    valid_viz_types = ['bar_chart', 'line_chart', 'pie_chart', 'scatter_plot', 'histogram', 'box_plot', 'heatmap', 'table']
    if viz_type not in valid_viz_types:
        issues.append(f"Invalid visualization type: {viz_type}")
    
    # Check if we have meaningful content
    if not viz_reason:
        issues.append("No visualization reasoning provided")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "Response validation successful"

def format_response_for_display(sql_query, viz_type, viz_reason, insights):
    """
    Format parsed response for display to user
    
    Args:
        sql_query (str): SQL query
        viz_type (str): Visualization type
        viz_reason (str): Visualization reasoning
        insights (str): Business insights
        
    Returns:
        dict: Formatted response
    """
    return {
        'sql': {
            'query': sql_query,
            'formatted': format_sql_for_display(sql_query)
        },
        'visualization': {
            'type': viz_type,
            'reason': viz_reason,
            'display_name': viz_type.replace('_', ' ').title()
        },
        'insights': {
            'text': insights,
            'formatted': format_insights_for_display(insights)
        }
    }

def format_sql_for_display(sql):
    """
    Format SQL for better display
    
    Args:
        sql (str): SQL query
        
    Returns:
        str: Formatted SQL
    """
    if not sql:
        return ""
    
    # Basic SQL formatting
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN']
    
    formatted_sql = sql
    for keyword in keywords:
        formatted_sql = re.sub(f'\\b{keyword}\\b', f'\n{keyword}', formatted_sql, flags=re.IGNORECASE)
    
    return formatted_sql.strip()

def format_insights_for_display(insights):
    """
    Format insights for better display
    
    Args:
        insights (str): Raw insights text
        
    Returns:
        str: Formatted insights
    """
    if not insights:
        return ""
    
    # Split into sentences and format
    sentences = insights.split('.')
    formatted_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 10:
            # Capitalize first letter
            sentence = sentence[0].upper() + sentence[1:]
            formatted_sentences.append(sentence)
    
    return '. '.join(formatted_sentences) + '.'