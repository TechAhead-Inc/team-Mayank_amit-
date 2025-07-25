"""
AI Prompt Management Module
"""

def create_dynamic_prompt(table_name, columns, data_types=None, is_postgres=False):
    """
    Create dynamic prompt for AI query generation
    
    Args:
        table_name (str): Name of the table
        columns (list): List of column names
        data_types (dict): Dictionary mapping columns to data types
        is_postgres (bool): Whether using PostgreSQL or SQLite
        
    Returns:
        str: Dynamic prompt for AI
    """
    db_type = "PostgreSQL" if is_postgres else "SQLite"
    
    # Analyze available columns to provide context
    numeric_cols = [col for col, dtype in (data_types or {}).items() if dtype in ['integer', 'numeric']]
    text_cols = [col for col, dtype in (data_types or {}).items() if dtype == 'text']
    date_cols = [col for col, dtype in (data_types or {}).items() if dtype == 'datetime']
    
    prompt = f"""
    You are an expert data analyst and SQL specialist. You must be creative and flexible in interpreting user questions.
    
    Database: {db_type}
    Table: '{table_name}'
    Available Columns: {', '.join(columns)}
    
    Column Types:
    - Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}
    - Text columns: {', '.join(text_cols) if text_cols else 'None'}  
    - Date columns: {', '.join(date_cols) if date_cols else 'None'}
    
    CRITICAL INSTRUCTIONS:
    1. Be FLEXIBLE with user requests - if they ask about "sales" but you have "revenue", use revenue
    2. If exact columns don't exist, find the CLOSEST match
    3. Always try to provide a working query, even if it's not exactly what was requested
    4. Focus on providing business insights with available data
    5. If uncertain, create exploratory queries that reveal interesting patterns
    
    Common Query Patterns:
    - Counts: SELECT column, COUNT(*) FROM {table_name} GROUP BY column
    - Trends: SELECT date_column, SUM(numeric_column) FROM {table_name} GROUP BY date_column
    - Rankings: SELECT column, SUM(value) FROM {table_name} GROUP BY column ORDER BY SUM(value) DESC
    - Distributions: SELECT column, COUNT(*) FROM {table_name} GROUP BY column
    - Statistics: SELECT AVG(column), MIN(column), MAX(column) FROM {table_name}
    
    Smart Column Mapping Examples:
    - "sales/revenue/income" → use any monetary column
    - "customers/users/clients" → use any person-related column  
    - "products/items/goods" → use any product-related column
    - "date/time/when" → use any date/timestamp column
    - "amount/value/price/cost" → use any numeric column
    - "name/title/description" → use any text column
    
    If query fails, suggest alternatives using available columns.
    Always aim to provide business value and insights.
    """
    return prompt

def create_business_context_prompt(table_name, columns, business_domain=None):
    """
    Create business context-aware prompt
    
    Args:
        table_name (str): Name of the table
        columns (list): List of column names
        business_domain (str): Business domain (e.g., 'retail', 'finance', 'healthcare')
        
    Returns:
        str: Business context prompt
    """
    # Detect business domain from column names if not provided
    if not business_domain:
        business_domain = detect_business_domain(columns)
    
    domain_examples = get_domain_specific_examples(business_domain, table_name)
    
    prompt = f"""
    You are analyzing {business_domain} data. Here are domain-specific insights you should consider:
    
    Table: {table_name}
    Business Domain: {business_domain}
    
    {domain_examples}
    
    When generating queries, consider these business contexts and provide insights that would be valuable 
    for {business_domain} professionals.
    """
    
    return prompt

def detect_business_domain(columns):
    """
    Detect business domain from column names
    
    Args:
        columns (list): List of column names
        
    Returns:
        str: Detected business domain
    """
    column_text = ' '.join(columns).lower()
    
    # Define domain keywords
    domains = {
        'retail': ['sales', 'product', 'customer', 'order', 'price', 'quantity', 'inventory'],
        'finance': ['account', 'transaction', 'balance', 'amount', 'payment', 'credit', 'debit'],
        'healthcare': ['patient', 'diagnosis', 'treatment', 'medication', 'hospital', 'doctor'],
        'marketing': ['campaign', 'click', 'impression', 'conversion', 'lead', 'channel'],
        'hr': ['employee', 'salary', 'department', 'hire', 'performance', 'training'],
        'education': ['student', 'course', 'grade', 'enrollment', 'teacher', 'class'],
        'logistics': ['shipment', 'delivery', 'warehouse', 'supplier', 'inventory', 'transport']
    }
    
    # Score each domain
    domain_scores = {}
    for domain, keywords in domains.items():
        score = sum(1 for keyword in keywords if keyword in column_text)
        domain_scores[domain] = score
    
    # Return domain with highest score, or 'general' if no clear match
    max_score = max(domain_scores.values()) if domain_scores else 0
    if max_score >= 2:  # Threshold for domain detection
        return max(domain_scores, key=domain_scores.get)
    else:
        return 'general'

def get_domain_specific_examples(domain, table_name):
    """
    Get domain-specific query examples and insights
    
    Args:
        domain (str): Business domain
        table_name (str): Table name
        
    Returns:
        str: Domain-specific examples
    """
    examples = {
        'retail': f"""
        Retail Analytics Focus:
        - Revenue trends: "Show sales performance over time"
        - Product analysis: "Which products are top performers?"
        - Customer insights: "Customer purchasing patterns"
        - Inventory management: "Stock levels and turnover rates"
        
        Example queries:
        - SELECT product_category, SUM(sales_amount) FROM {table_name} GROUP BY product_category
        - SELECT DATE_TRUNC('month', order_date), COUNT(*) FROM {table_name} GROUP BY 1
        """,
        
        'finance': f"""
        Financial Analytics Focus:
        - Transaction patterns: "Monthly transaction volumes"
        - Account analysis: "Account balance trends and distributions"
        - Risk assessment: "Transaction anomalies and patterns"
        - Performance metrics: "ROI, profitability, and growth rates"
        
        Example queries:
        - SELECT account_type, AVG(balance) FROM {table_name} GROUP BY account_type
        - SELECT DATE_TRUNC('month', transaction_date), SUM(amount) FROM {table_name} GROUP BY 1
        """,
        
        'healthcare': f"""
        Healthcare Analytics Focus:
        - Patient demographics: "Age, gender, and geographic distributions"
        - Treatment outcomes: "Recovery rates and treatment effectiveness"
        - Resource utilization: "Bed occupancy and staff allocation"
        - Cost analysis: "Treatment costs and insurance coverage"
        
        Example queries:
        - SELECT diagnosis, COUNT(*) FROM {table_name} GROUP BY diagnosis
        - SELECT age_group, AVG(treatment_duration) FROM {table_name} GROUP BY age_group
        """,
        
        'marketing': f"""
        Marketing Analytics Focus:
        - Campaign performance: "CTR, conversion rates, and ROI"
        - Channel effectiveness: "Which channels drive best results"
        - Customer acquisition: "Lead generation and conversion funnels"
        - Audience insights: "Demographics and behavior patterns"
        
        Example queries:
        - SELECT campaign_name, SUM(conversions)/SUM(clicks) as conversion_rate FROM {table_name} GROUP BY campaign_name
        - SELECT channel, AVG(cost_per_acquisition) FROM {table_name} GROUP BY channel
        """,
        
        'general': f"""
        General Data Analysis Focus:
        - Data distribution: "Show patterns and distributions in your data"
        - Trends over time: "Identify trends and seasonal patterns"
        - Correlations: "Find relationships between different variables"
        - Outliers: "Identify unusual or interesting data points"
        
        Example queries:
        - SELECT column1, COUNT(*) FROM {table_name} GROUP BY column1
        - SELECT DATE_TRUNC('month', date_column), AVG(numeric_column) FROM {table_name} GROUP BY 1
        """
    }
    
    return examples.get(domain, examples['general'])

def get_sample_queries(table_name, columns, data_types):
    """
    Generate sample queries based on available data
    
    Args:
        table_name (str): Name of the table
        columns (list): List of column names
        data_types (dict): Dictionary mapping columns to data types
        
    Returns:
        list: List of sample query suggestions
    """
    queries = []
    
    # Analyze available columns
    numeric_cols = [col for col, dtype in (data_types or {}).items() if dtype in ['integer', 'numeric']]
    text_cols = [col for col, dtype in (data_types or {}).items() if dtype == 'text']
    date_cols = [col for col, dtype in (data_types or {}).items() if dtype == 'datetime']
    
    # Basic exploration queries
    queries.extend([
        "Show me a sample of the data",
        "What are the column statistics?",
        "How many total records are there?",
    ])
    
    # Column-specific queries
    if text_cols:
        queries.extend([
            f"Show distribution of {text_cols[0]}",
            f"What are the most common values in {text_cols[0]}?",
        ])
    
    if numeric_cols:
        queries.extend([
            f"Show statistics for {numeric_cols[0]}",
            f"What's the average {numeric_cols[0]}?",
        ])
    
    if len(numeric_cols) >= 2:
        queries.append(f"Compare {numeric_cols[0]} and {numeric_cols[1]}")
    
    if text_cols and numeric_cols:
        queries.append(f"Show {numeric_cols[0]} by {text_cols[0]}")
    
    if date_cols:
        queries.extend([
            f"Show trends over {date_cols[0]}",
            f"What's the date range in the data?",
        ])
    
    return queries[:8]  # Return top 8 suggestions

def create_visualization_prompt(query_type, data_characteristics):
    """
    Create prompt for visualization recommendations
    
    Args:
        query_type (str): Type of query being executed
        data_characteristics (dict): Characteristics of the result data
        
    Returns:
        str: Visualization recommendation prompt
    """
    prompt = f"""
    Based on the query type '{query_type}' and data characteristics, recommend the best visualization:
    
    Data Characteristics:
    - Row count: {data_characteristics.get('rows', 0)}
    - Column count: {data_characteristics.get('columns', 0)}
    - Numeric columns: {data_characteristics.get('numeric_cols', [])}
    - Categorical columns: {data_characteristics.get('categorical_cols', [])}
    - Date columns: {data_characteristics.get('date_cols', [])}
    
    Visualization Options:
    1. bar_chart - For categorical data comparisons
    2. line_chart - For trends over time
    3. pie_chart - For composition/parts of whole
    4. scatter_plot - For relationships between variables
    5. histogram - For distribution of single variable
    6. box_plot - For distribution comparison across categories
    7. heatmap - For correlation matrices
    
    Choose the most appropriate visualization and explain why.
    """
    
    return prompt

def create_error_recovery_prompt(original_query, error_message, table_info):
    """
    Create prompt for error recovery and alternative query generation
    
    Args:
        original_query (str): The original user query that failed
        error_message (str): The error message received
        table_info (dict): Information about the table structure
        
    Returns:
        str: Error recovery prompt
    """
    prompt = f"""
    The original query "{original_query}" failed with error: {error_message}
    
    Table Information: {table_info}
    
    Please provide an alternative approach that:
    1. Addresses the user's original intent
    2. Uses only existing columns and valid syntax
    3. Provides useful insights even if not exactly matching the original request
    4. Includes explanation of what was changed and why
    
    Focus on creating a query that works with the available data structure.
    """
    
    return prompt

def get_prompt_templates():
    """
    Get collection of prompt templates for different scenarios
    
    Returns:
        dict: Dictionary of prompt templates
    """
    return {
        'basic_analysis': """
        Analyze the data in table '{table_name}' and provide insights about:
        1. Data distribution and patterns
        2. Key statistics and trends
        3. Interesting relationships or outliers
        4. Business implications of the findings
        """,
        
        'comparison': """
        Compare different segments in the data by:
        1. Identifying key grouping variables
        2. Calculating relevant metrics for each group
        3. Highlighting significant differences
        4. Providing actionable insights
        """,
        
        'trend_analysis': """
        Analyze trends over time by:
        1. Identifying temporal patterns
        2. Calculating growth rates or changes
        3. Detecting seasonality or cycles
        4. Forecasting implications
        """,
        
        'performance_metrics': """
        Calculate key performance indicators by:
        1. Identifying relevant business metrics
        2. Computing aggregated values
        3. Comparing against benchmarks
        4. Highlighting areas for improvement
        """
    }

def enhance_prompt_with_context(base_prompt, context_info):
    """
    Enhance base prompt with additional context information
    
    Args:
        base_prompt (str): Base prompt to enhance
        context_info (dict): Additional context information
        
    Returns:
        str: Enhanced prompt
    """
    enhancements = []
    
    if context_info.get('previous_queries'):
        enhancements.append(f"Previous queries in this session: {context_info['previous_queries']}")
    
    if context_info.get('user_preferences'):
        enhancements.append(f"User preferences: {context_info['user_preferences']}")
    
    if context_info.get('business_context'):
        enhancements.append(f"Business context: {context_info['business_context']}")
    
    if enhancements:
        enhanced_prompt = base_prompt + "\n\nAdditional Context:\n" + "\n".join(enhancements)
        return enhanced_prompt
    
    return base_prompt

def validate_prompt_parameters(table_name, columns, data_types):
    """
    Validate prompt parameters before generating prompt
    
    Args:
        table_name (str): Name of the table
        columns (list): List of column names
        data_types (dict): Dictionary mapping columns to data types
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not table_name:
        return False, "Table name is required"
    
    if not columns or len(columns) == 0:
        return False, "At least one column is required"
    
    if len(columns) > 1000:
        return False, "Too many columns (max 1000)"
    
    if data_types and len(data_types) != len(columns):
        return False, "Data types count must match columns count"
    
    return True, "Valid prompt parameters"