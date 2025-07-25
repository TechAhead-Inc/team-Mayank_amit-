"""
Custom Query Interface Page Module
"""

import streamlit as st
from ai.openai_client import generate_sql_from_question
from ai.prompt_manager import create_dynamic_prompt, get_sample_queries
from ai.response_parser import parse_openai_response
from database.queries import execute_sql_query
from visualization.chart_generator import create_visualization
from visualization.dashboard_components import render_status_indicator, render_info_box
from utils.constants import UI_MESSAGES

def render_custom_query():
    """Render the custom query interface page"""
    
    st.markdown('<div class="sub-header">Custom Query Interface</div>', unsafe_allow_html=True)
    
    # Show connection info
    display_connection_info()
    
    # Show query suggestions
    display_query_suggestions()
    
    # Main query interface
    render_query_input_section()
    
    # Handle auto-run queries from suggestions
    handle_auto_run_queries()

def display_connection_info():
    """Display current connection and table information"""
    
    conn_type = "PostgreSQL" if st.session_state.connection_type == "postgres" else "SQLite"
    table_name = st.session_state.table_name
    columns = st.session_state.columns
    
    connection_info = f"""
    **Connected to:** {conn_type}  
    **Table:** {table_name}  
    **Columns:** {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}
    """
    
    render_info_box(
        title="Connection Status",
        content=connection_info,
        box_type="info",
        expandable=False
    )

def display_query_suggestions():
    """Display sample query suggestions with clickable buttons"""
    
    with st.expander("Smart Query Suggestions Based on Your Data", expanded=True):
        st.write("**Quick Analytics - Click any button to run instantly:**")
        
        suggestions = get_sample_queries(
            st.session_state.table_name,
            st.session_state.columns,
            st.session_state.data_types
        )
        
        # Organize suggestions into categories
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Quick Start Queries:**")
            for i, suggestion in enumerate(suggestions[:3]):
                if st.button(f"📊 {suggestion}", key=f"quick_{i}", use_container_width=True):
                    st.session_state.auto_run_query = suggestion
                    st.rerun()
        
        with col2:
            st.write("**🔍 Data Exploration:**")
            exploration_queries = [
                "Show me interesting patterns in the data",
                "What are the data quality insights?",
                "Give me a comprehensive data overview"
            ]
            for i, query in enumerate(exploration_queries):
                if st.button(f"🔍 {query}", key=f"explore_{i}", use_container_width=True):
                    st.session_state.auto_run_query = query
                    st.rerun()
        
        # Domain-specific suggestions
        render_domain_specific_suggestions()

def render_domain_specific_suggestions():
    """Render domain-specific query suggestions based on column names"""
    
    columns_text = ' '.join(st.session_state.columns).lower()
    
    # Check for restaurant/retail data
    if any(keyword in columns_text for keyword in ['order', 'menu', 'customer', 'food', 'restaurant', 'price', 'sale']):
        st.write("**🍽️ Restaurant Analytics:**")
        restaurant_queries = [
            "Show me sales performance analysis",
            "What are the most popular items?",
            "Customer ordering patterns",
            "Revenue trends and insights"
        ]
        
        cols = st.columns(2)
        for i, query in enumerate(restaurant_queries):
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(f"🍽️ {query}", key=f"restaurant_{i}", use_container_width=True):
                    st.session_state.auto_run_query = query
                    st.rerun()

def render_query_input_section():
    """Render the main query input and processing section"""
    
    st.subheader("Ask a Question About Your Data")
    
    # Initialize clear flag
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False
    
    # Query input
    question = st.text_input(
        "Enter your data analysis question:",
        placeholder="e.g., Show me sales trends over time, What's the average revenue by category?",
        key="query_input",
        value="" if st.session_state.clear_input else st.session_state.get("query_input", ""),
        help="Use natural language to describe what you want to analyze"
    )
    
    # Reset clear flag after rerun
    if st.session_state.clear_input:
        st.session_state.clear_input = False
    
    # Control buttons
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        submit = st.button("🚀 Generate Analysis", use_container_width=True, type="primary")
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.clear_input = True
            st.rerun()
    with col3:
        if st.button("Help", use_container_width=True):
            show_query_help()
    
    # Process query submission
    if submit:
        handle_query_submission(question)

def handle_query_submission(question):
    """Handle the main query submission and processing"""
    
    if not question or not question.strip():
        st.warning("Please enter a question to analyze your data.")
        return
    
    # Validate question
    if len(question.strip()) < 5:
        st.warning("Please enter a more detailed question.")
        return
    
    # Prepare for AI processing
    table_info = f"Table: {st.session_state.table_name}, Columns: {st.session_state.columns}, Data Types: {st.session_state.data_types}"
    is_postgres = st.session_state.connection_type == "postgres"
    prompt = create_dynamic_prompt(
        st.session_state.table_name, 
        st.session_state.columns, 
        st.session_state.data_types, 
        is_postgres
    )
    
    # Generate SQL with AI
    with st.spinner("🧠 Analyzing question and generating SQL..."):
        response = generate_sql_from_question(question, prompt, table_info, attempt=1)
    
    if response:
        process_ai_response(question, response, prompt, table_info)
    else:
        render_status_indicator("error", "Failed to generate SQL query. Please try again with a different question.")

def process_ai_response(question, response, prompt, table_info):
    """Process the AI response and execute the generated SQL"""
    
    # Parse AI response
    sql_query, viz_type, viz_reason, insights = parse_openai_response(response)
    
    if not sql_query:
        render_status_indicator("error", "Could not extract a valid SQL query from AI response.")
        return
    
    # Display generated SQL
    st.subheader("🔧 Generated SQL Query")
    st.code(sql_query, language="sql")
    
    # Execute query
    with st.spinner("⚡ Executing database query..."):
        df = execute_sql_query(sql_query, st.session_state.db_engine)
    
    if not df.empty:
        # Show successful results
        st.subheader("📊 Query Results & Visualization")
        
        # Create visualization
        with st.spinner("🎨 Creating visualization..."):
            create_visualization(df, viz_type, viz_reason, question)
        
        # Show insights if available
        if insights:
            render_info_box(
                title="AI Insights",
                content=insights,
                box_type="success",
                expandable=True,
                expanded=True
            )
        
        # Show query statistics
        display_query_statistics(df, sql_query)
        
    else:
        # Handle empty results with fallback
        handle_empty_results(question, prompt, table_info)

def handle_empty_results(question, prompt, table_info):
    """Handle case when query returns no results"""
    
    st.warning("🔄 No results found. Let me try a different approach...")
    
    # Try fallback query with AI
    with st.spinner("🔍 Exploring alternative queries..."):
        fallback_response = generate_sql_from_question(question, prompt, table_info, attempt=2)
    
    if fallback_response:
        fallback_sql, fallback_viz, fallback_reason, fallback_insights = parse_openai_response(fallback_response)
        
        if fallback_sql:
            st.subheader("🔄 Alternative Query Approach")
            st.code(fallback_sql, language="sql")
            
            # Execute fallback query
            fallback_df = execute_sql_query(fallback_sql, st.session_state.db_engine)
            
            if not fallback_df.empty:
                st.subheader("📊 Exploratory Results")
                create_visualization(fallback_df, fallback_viz, fallback_reason, question)
                
                if fallback_insights:
                    render_info_box(
                        title="Alternative Insights",
                        content=fallback_insights,
                        box_type="info"
                    )
            else:
                show_fallback_suggestions()
        else:
            show_fallback_suggestions()
    else:
        show_fallback_suggestions()

def show_fallback_suggestions():
    """Show fallback suggestions when queries fail"""
    
    render_status_indicator("error", "Unable to generate results. Here are some suggestions:")
    
    st.subheader("💡 Try These Queries Instead")
    st.write("**Click any suggestion below to run it automatically:**")
    
    suggestions = get_sample_queries(
        st.session_state.table_name, 
        st.session_state.columns, 
        st.session_state.data_types
    )
    
    # Create a grid of suggestion buttons
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        col_idx = i % 2
        with cols[col_idx]:
            if st.button(f"📊 {suggestion}", key=f"fallback_suggestion_{i}", use_container_width=True):
                st.session_state.auto_run_query = suggestion
                st.rerun()

def handle_auto_run_queries():
    """Handle automatically triggered queries from suggestion buttons"""
    
    if hasattr(st.session_state, 'auto_run_query'):
        auto_query = st.session_state.auto_run_query
        
        # Create a visual separator
        st.markdown("---")
        render_status_indicator("success", f"🚀 Running suggested query: {auto_query}")
        
        # Prepare AI processing
        table_info = f"Table: {st.session_state.table_name}, Columns: {st.session_state.columns}, Data Types: {st.session_state.data_types}"
        is_postgres = st.session_state.connection_type == "postgres"
        prompt = create_dynamic_prompt(
            st.session_state.table_name, 
            st.session_state.columns, 
            st.session_state.data_types, 
            is_postgres
        )
        
        # Generate and execute query
        with st.spinner(f"🧠 Processing: {auto_query}"):
            response = generate_sql_from_question(auto_query, prompt, table_info)
        
        if response:
            sql_query, viz_type, viz_reason, insights = parse_openai_response(response)
            
            if sql_query:
                st.subheader("🔧 Generated SQL Query")
                st.code(sql_query, language="sql")
                
                # Execute query
                df = execute_sql_query(sql_query, st.session_state.db_engine)
                
                if not df.empty:
                    st.subheader("📊 Query Results")
                    create_visualization(df, viz_type, viz_reason, auto_query)
                    
                    if insights:
                        render_info_box(
                            title="AI Insights",
                            content=insights,
                            box_type="info"
                        )
                    
                    # Show related suggestions
                    show_related_suggestions(auto_query)
                    
                else:
                    st.warning("No results found for this suggested query.")
                    st.info("💡 Try a different suggestion or ask your own question above.")
            else:
                render_status_indicator("error", "Could not generate a valid SQL query.")
        else:
            render_status_indicator("error", "Failed to process the suggested query. Please try a different one.")
        
        # Clear the auto-run query
        del st.session_state.auto_run_query

def show_related_suggestions(current_query):
    """Show related query suggestions based on current query results"""
    
    with st.expander("🔄 More Related Questions", expanded=False):
        st.write("**Based on this result, you might also want to ask:**")
        
        # Generate contextual suggestions based on current query
        related_suggestions = generate_related_suggestions(current_query)
        
        for i, suggestion in enumerate(related_suggestions[:3]):
            if st.button(f"➡️ {suggestion}", key=f"related_suggestion_{i}"):
                st.session_state.auto_run_query = suggestion
                st.rerun()

def generate_related_suggestions(current_query):
    """Generate related query suggestions based on current query"""
    
    # This is a simplified version - in a full implementation,
    # this could use AI to generate contextually relevant suggestions
    base_suggestions = [
        "Show me trends over time",
        "What are the top performers?",
        "Compare different categories",
        "Show data distribution",
        "Find correlations in the data"
    ]
    
    # Filter out suggestions similar to current query
    filtered_suggestions = [s for s in base_suggestions if s.lower() not in current_query.lower()]
    
    return filtered_suggestions[:3]

def display_query_statistics(df, sql_query):
    """Display statistics about the query results"""
    
    with st.expander("📈 Query Statistics", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows Returned", f"{len(df):,}")
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.metric("Memory Usage", f"{memory_mb:.2f} MB")
        
        # Show column information
        st.write("**Result Columns:**")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            st.write(f"- **{col}** ({dtype}) - {null_count} null values")

def show_query_help():
    """Display help information for writing queries"""
    
    with st.expander("💡 Query Help & Tips", expanded=True):
        st.markdown("""
        ### How to Ask Great Questions:
        
        **✅ Good Examples:**
        - "Show me sales trends over the last 6 months"
        - "What are the top 10 customers by revenue?"
        - "Compare performance across different product categories"
        - "Find correlations between price and quantity sold"
        
        **💡 Tips for Better Results:**
        - Be specific about what you want to analyze
        - Mention time periods if relevant (last month, this year, etc.)
        - Ask for comparisons between different groups
        - Request specific metrics (average, total, count, etc.)
        - Use natural language - the AI will convert it to SQL
        
        **🔧 Troubleshooting:**
        - If no results appear, try rephrasing your question
        - Check that your data source is properly connected
        - Ensure your question matches the available data columns
        - Try simpler queries if complex ones fail
        - Use the sample suggestions for inspiration
        """)

def export_query_results(df, query_description):
    """Export query results (placeholder for future implementation)"""
    
    if df.empty:
        return
    
    st.subheader("📁 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"query_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name=f"query_results.json",
            mime="application/json",
            use_container_width=True
        )