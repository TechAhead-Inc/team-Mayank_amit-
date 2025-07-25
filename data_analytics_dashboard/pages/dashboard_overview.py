"""
Dashboard Overview Page Module
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from database.queries import execute_sql_query
from ai.prompt_manager import get_sample_queries
from utils.helpers import get_sample_data_summary
from visualization.chart_generator import create_visualization

def render_dashboard_overview():
    """Render the dashboard overview page"""
    
    st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
    
    try:
        # Get basic table information
        table_stats = get_table_statistics()
        
        if not table_stats:
            st.error("Unable to load table statistics")
            return
        
        # Display key metrics
        display_key_metrics(table_stats)
        
        # Display dataset information
        display_dataset_info()
        
        # Create automatic visualizations
        create_overview_visualizations()
        
        # Display sample data
        display_sample_data()
        
        # Show quick insights and suggestions
        display_quick_insights()
        
    except Exception as e:
        st.error(f"Error creating dashboard overview: {str(e)}")
        show_fallback_overview()

def get_table_statistics():
    """Get basic statistics about the current table"""
    try:
        table_name = st.session_state.table_name
        db_engine = st.session_state.db_engine
        
        # Get total row count
        total_df = execute_sql_query(f"SELECT COUNT(*) as total FROM {table_name}", db_engine)
        total_records = total_df['total'].iloc[0] if not total_df.empty else 0
        
        # Get sample data for analysis
        sample_df = execute_sql_query(f"SELECT * FROM {table_name} LIMIT 1000", db_engine)
        
        if sample_df.empty:
            return None
        
        # Analyze data characteristics
        numeric_columns = sample_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = sample_df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_columns = sample_df.select_dtypes(include=['datetime64']).columns.tolist()
        
        return {
            'total_records': total_records,
            'total_columns': len(st.session_state.columns),
            'numeric_columns': numeric_columns,
            'categorical_columns': categorical_columns,
            'datetime_columns': datetime_columns,
            'sample_data': sample_df,
            'null_counts': sample_df.isnull().sum().to_dict(),
            'memory_usage': sample_df.memory_usage(deep=True).sum()
        }
        
    except Exception as e:
        st.error(f"Error getting table statistics: {str(e)}")
        return None

def display_key_metrics(stats):
    """Display key metrics in a card layout"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Records",
            value=f"{stats['total_records']:,}",
            help="Total number of rows in the dataset"
        )
    
    with col2:
        st.metric(
            label="Total Columns", 
            value=stats['total_columns'],
            help="Total number of columns in the dataset"
        )
    
    with col3:
        st.metric(
            label="Numeric Columns",
            value=len(stats['numeric_columns']),
            help="Number of numeric columns for analysis"
        )
    
    with col4:
        st.metric(
            label="Text Columns",
            value=len(stats['categorical_columns']),
            help="Number of text/categorical columns"
        )

def display_dataset_info():
    """Display detailed dataset information"""
    
    st.subheader("Dataset Information")
    
    # Create column information DataFrame
    columns = st.session_state.columns
    data_types = st.session_state.data_types
    
    col_info_data = []
    for col in columns:
        col_info_data.append({
            'Column Name': col,
            'Data Type': data_types.get(col, 'unknown'),
            'Null Values': '✓' if col in st.session_state.get('null_columns', []) else '✗'
        })
    
    col_info_df = pd.DataFrame(col_info_data)
    st.dataframe(col_info_df, use_container_width=True, hide_index=True)

def create_overview_visualizations():
    """Create automatic visualizations for data overview"""
    
    st.subheader("Data Overview Visualizations")
    
    try:
        sample_df = execute_sql_query(
            f"SELECT * FROM {st.session_state.table_name} LIMIT 500", 
            st.session_state.db_engine
        )
        
        if sample_df.empty:
            st.warning("No data available for visualization")
            return
        
        numeric_cols = sample_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = sample_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Create visualizations based on available data types
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            create_categorical_numeric_charts(sample_df, categorical_cols, numeric_cols)
        elif len(numeric_cols) >= 2:
            create_numeric_analysis_charts(sample_df, numeric_cols)
        elif len(categorical_cols) > 0:
            create_categorical_analysis_charts(sample_df, categorical_cols)
        else:
            st.info("Data structure not suitable for automatic visualization")
            
    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")

def create_categorical_numeric_charts(df, categorical_cols, numeric_cols):
    """Create charts for categorical and numeric data combination"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top categories by first numeric column
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        
        try:
            # Aggregate data to avoid issues with multiple rows per category
            agg_df = df.groupby(cat_col)[num_col].sum().reset_index()
            top_categories = agg_df.nlargest(10, num_col)
            
            if not top_categories.empty:
                fig = px.bar(
                    top_categories, 
                    x=cat_col, 
                    y=num_col,
                    title=f"Top 10 {cat_col} by {num_col}"
                )
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No data to display for {cat_col} vs {num_col}")
                
        except Exception as e:
            st.error(f"Error creating categorical chart: {str(e)}")
    
    with col2:
        # Distribution of first numeric column
        num_col = numeric_cols[0]
        
        try:
            if not df[num_col].isna().all():
                fig = px.histogram(
                    df, 
                    x=num_col, 
                    title=f"{num_col} Distribution",
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No valid data for {num_col} distribution")
                
        except Exception as e:
            st.error(f"Error creating histogram: {str(e)}")

def create_numeric_analysis_charts(df, numeric_cols):
    """Create charts for numeric data analysis"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Correlation heatmap
        try:
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols[:5]].corr()  # Limit to first 5 columns
                fig = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    aspect="auto",
                    title="Correlation Matrix"
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating correlation matrix: {str(e)}")
    
    with col2:
        # Scatter plot of first two numeric columns
        try:
            x_col, y_col = numeric_cols[0], numeric_cols[1]
            fig = px.scatter(
                df, 
                x=x_col, 
                y=y_col,
                title=f"{y_col} vs {x_col}"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating scatter plot: {str(e)}")

def create_categorical_analysis_charts(df, categorical_cols):
    """Create charts for categorical data analysis"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Value counts for first categorical column
        cat_col = categorical_cols[0]
        try:
            value_counts = df[cat_col].value_counts().head(10)
            fig = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=f"Distribution of {cat_col}"
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating value counts chart: {str(e)}")
    
    with col2:
        # Pie chart if suitable
        if len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            try:
                value_counts = df[cat_col].value_counts().head(8)
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"{cat_col} Composition"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating pie chart: {str(e)}")

def display_sample_data():
    """Display sample data from the table"""
    
    st.subheader("Sample Data Preview")
    
    try:
        sample_df = execute_sql_query(
            f"SELECT * FROM {st.session_state.table_name} LIMIT 10", 
            st.session_state.db_engine
        )
        
        if not sample_df.empty:
            st.dataframe(sample_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No sample data available")
            
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")

def display_quick_insights():
    """Display quick insights and analysis suggestions"""
    
    st.subheader("Quick Insights & Suggestions")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("**📊 Data Summary:**")
        
        # Basic statistics
        total_records = st.session_state.row_count
        total_columns = len(st.session_state.columns)
        data_types = st.session_state.data_types
        
        numeric_count = sum(1 for dtype in data_types.values() if dtype in ['integer', 'numeric'])
        text_count = sum(1 for dtype in data_types.values() if dtype == 'text')
        
        st.write(f"• **{total_records:,}** total records")
        st.write(f"• **{total_columns}** total columns")
        st.write(f"• **{numeric_count}** numeric fields for analysis")
        st.write(f"• **{text_count}** categorical fields for grouping")
        
        # Data quality insights
        if hasattr(st.session_state, 'sample_stats'):
            stats = st.session_state.sample_stats
            if 'null_counts' in stats:
                null_columns = [col for col, count in stats['null_counts'].items() if count > 0]
                if null_columns:
                    st.write(f"• **{len(null_columns)}** columns have missing values")
    
    with insights_col2:
        st.markdown("**💡 Suggested Analyses:**")
        
        # Generate contextual suggestions
        suggestions = get_sample_queries(
            st.session_state.table_name,
            st.session_state.columns,
            st.session_state.data_types
        )
        
        for suggestion in suggestions[:5]:
            st.write(f"• {suggestion}")
        
        st.markdown("**🔍 Next Steps:**")
        st.write("• Use the **Custom Query** tab to ask specific questions")
        st.write("• Try the **Data Explorer** for interactive filtering")
        st.write("• Click on any suggestion above to run it automatically")

def show_fallback_overview():
    """Show fallback overview when main overview fails"""
    
    st.subheader("Basic Table Information")
    
    # Show basic session state info
    if st.session_state.table_name:
        st.write(f"**Table Name:** {st.session_state.table_name}")
        st.write(f"**Total Columns:** {len(st.session_state.columns)}")
        
        if st.session_state.columns:
            st.write("**Available Columns:**")
            for i, col in enumerate(st.session_state.columns[:10]):  # Show first 10
                dtype = st.session_state.data_types.get(col, 'unknown')
                st.write(f"{i+1}. {col} ({dtype})")
            
            if len(st.session_state.columns) > 10:
                st.write(f"... and {len(st.session_state.columns) - 10} more columns")
        
        # Basic connection info
        conn_type = "PostgreSQL" if st.session_state.connection_type == "postgres" else "File Upload"
        st.write(f"**Data Source:** {conn_type}")
        
        if st.session_state.row_count:
            st.write(f"**Estimated Rows:** {st.session_state.row_count:,}")

def refresh_overview():
    """Refresh the overview data (for future use)"""
    # This function could be used to refresh the overview without reloading the entire page
    st.rerun()

def export_overview_summary():
    """Export overview summary (placeholder for future implementation)"""
    # This function could export the overview as PDF or other formats
    st.info("Overview export functionality would be implemented here")