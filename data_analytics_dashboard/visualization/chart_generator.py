"""
Chart Generation and Visualization Module
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.constants import CHART_CONFIGS, VISUALIZATION_CONSTANTS

def create_visualization(df, viz_type="auto", viz_reason="", question=""):
    """
    Create visualizations based on data and AI recommendations
    
    Args:
        df (pandas.DataFrame): Data to visualize
        viz_type (str): Type of visualization
        viz_reason (str): Reason for visualization choice
        question (str): Original user question
        
    Returns:
        None: Displays visualization in Streamlit
    """
    if df.empty:
        st.warning("No data to visualize")
        return
    
    # Show AI recommendation
    if viz_reason:
        st.info(f"**Visualization Recommendation:** {viz_type.replace('_', ' ').title()} - {viz_reason}")
    
    # Analyze data characteristics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Handle single metric display
    if df.shape[1] == 1 and df.shape[0] == 1:
        display_single_metric(df)
        return
    
    # Create visualization based on type
    try:
        if viz_type == "pie_chart":
            create_pie_chart(df, categorical_cols, numeric_cols)
        elif viz_type == "bar_chart":
            create_bar_chart(df, categorical_cols, numeric_cols)
        elif viz_type == "line_chart":
            create_line_chart(df, datetime_cols, numeric_cols)
        elif viz_type == "scatter_plot":
            create_scatter_plot(df, numeric_cols, categorical_cols)
        elif viz_type == "histogram":
            create_histogram(df, numeric_cols)
        elif viz_type == "box_plot":
            create_box_plot(df, categorical_cols, numeric_cols)
        elif viz_type == "heatmap":
            create_heatmap(df, numeric_cols)
        else:
            create_auto_visualization(df, numeric_cols, categorical_cols, datetime_cols)
    
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        # Fallback to table view
        st.subheader("Data Table")
        st.dataframe(df, use_container_width=True)
    
    # Always show data summary
    display_data_summary(df, numeric_cols, categorical_cols, datetime_cols)

def display_single_metric(df):
    """Display single metric value"""
    col1, col2, col3 = st.columns(3)
    with col2:
        value = df.iloc[0, 0]
        if pd.api.types.is_numeric_dtype(df.iloc[:, 0]):
            formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        else:
            formatted_value = str(value)
        
        st.metric(label="Result", value=formatted_value)

def create_pie_chart(df, categorical_cols, numeric_cols):
    """Create pie chart visualization"""
    if len(df.columns) >= 2 and len(categorical_cols) >= 1:
        # Use first categorical column for names
        names_col = categorical_cols[0] if categorical_cols else df.columns[0]
        
        # Use first numeric column for values, or count if no numeric columns
        if numeric_cols:
            values_col = numeric_cols[0]
            fig = px.pie(df, names=names_col, values=values_col, 
                        title=f"{names_col} Distribution by {values_col}")
        else:
            # Create count-based pie chart
            value_counts = df[names_col].value_counts()
            fig = px.pie(values=value_counts.values, names=value_counts.index,
                        title=f"{names_col} Distribution")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Pie chart requires at least one categorical column")

def create_bar_chart(df, categorical_cols, numeric_cols):
    """Create bar chart visualization"""
    if len(df.columns) >= 2:
        if categorical_cols and numeric_cols:
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            
            # Handle grouped data
            if len(df[x_col].unique()) > CHART_CONFIGS['bar_chart']['max_categories']:
                # Take top categories
                top_categories = df.groupby(x_col)[y_col].sum().nlargest(20)
                df_filtered = df[df[x_col].isin(top_categories.index)]
                st.info(f"Showing top 20 categories out of {len(df[x_col].unique())} total")
            else:
                df_filtered = df
            
            fig = px.bar(df_filtered, x=x_col, y=y_col,
                        title=f"{y_col} by {x_col}")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        elif categorical_cols:
            # Count-based bar chart
            x_col = categorical_cols[0]
            value_counts = df[x_col].value_counts()
            
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f"Count of {x_col}")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Bar chart requires at least two columns")

def create_line_chart(df, datetime_cols, numeric_cols):
    """Create line chart visualization"""
    if datetime_cols and numeric_cols:
        x_col = datetime_cols[0]
        y_col = numeric_cols[0]
        
        # Sort by date
        df_sorted = df.sort_values(x_col)
        
        fig = px.line(df_sorted, x=x_col, y=y_col,
                     title=f"{y_col} Trend Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    elif len(df.columns) >= 2 and numeric_cols:
        # Use index as x-axis
        y_col = numeric_cols[0]
        fig = px.line(df, y=y_col, title=f"{y_col} Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Line chart requires at least one numeric column, preferably with dates")

def create_scatter_plot(df, numeric_cols, categorical_cols):
    """Create scatter plot visualization"""
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Use categorical column for color if available
        color_col = categorical_cols[0] if categorical_cols else None
        
        # Limit data points for performance
        if len(df) > CHART_CONFIGS['scatter_plot']['max_data_points']:
            df_sample = df.sample(n=CHART_CONFIGS['scatter_plot']['max_data_points'])
            st.info(f"Showing random sample of {CHART_CONFIGS['scatter_plot']['max_data_points']} points")
        else:
            df_sample = df
        
        fig = px.scatter(df_sample, x=x_col, y=y_col, color=color_col,
                        title=f"{y_col} vs {x_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Scatter plot requires at least two numeric columns")

def create_histogram(df, numeric_cols):
    """Create histogram visualization"""
    if numeric_cols:
        col = numeric_cols[0]
        
        fig = px.histogram(df, x=col, nbins=CHART_CONFIGS['histogram']['default_bins'],
                          title=f"{col} Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Histogram requires at least one numeric column")

def create_box_plot(df, categorical_cols, numeric_cols):
    """Create box plot visualization"""
    if numeric_cols:
        y_col = numeric_cols[0]
        x_col = categorical_cols[0] if categorical_cols else None
        
        # Limit categories for readability
        if x_col and len(df[x_col].unique()) > CHART_CONFIGS['box_plot']['max_categories']:
            top_categories = df[x_col].value_counts().head(CHART_CONFIGS['box_plot']['max_categories']).index
            df_filtered = df[df[x_col].isin(top_categories)]
            st.info(f"Showing top {CHART_CONFIGS['box_plot']['max_categories']} categories")
        else:
            df_filtered = df
        
        fig = px.box(df_filtered, x=x_col, y=y_col,
                    title=f"{y_col} Distribution" + (f" by {x_col}" if x_col else ""))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Box plot requires at least one numeric column")

def create_heatmap(df, numeric_cols):
    """Create heatmap visualization"""
    if len(numeric_cols) >= 2:
        # Create correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(corr_matrix, 
                       text_auto=True, 
                       aspect="auto",
                       title="Correlation Heatmap",
                       color_continuous_scale='RdYlBu')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Heatmap requires at least two numeric columns")

def create_auto_visualization(df, numeric_cols, categorical_cols, datetime_cols):
    """Create automatic visualization based on data characteristics"""
    
    # Single column with many unique values - histogram or value counts
    if len(df.columns) == 1:
        col = df.columns[0]
        if col in numeric_cols:
            create_histogram(df, [col])
        else:
            value_counts = df[col].value_counts().head(20)
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f"Top Values in {col}")
            st.plotly_chart(fig, use_container_width=True)
    
    # Two columns - choose based on types
    elif len(df.columns) == 2:
        if len(numeric_cols) == 1 and len(categorical_cols) == 1:
            create_bar_chart(df, categorical_cols, numeric_cols)
        elif len(numeric_cols) == 2:
            create_scatter_plot(df, numeric_cols, categorical_cols)
        elif len(categorical_cols) == 2:
            # Cross-tabulation
            ct = pd.crosstab(df[categorical_cols[0]], df[categorical_cols[1]])
            fig = px.imshow(ct, title=f"{categorical_cols[0]} vs {categorical_cols[1]}")
            st.plotly_chart(fig, use_container_width=True)
    
    # Multiple columns - create dashboard
    else:
        create_multi_chart_dashboard(df, numeric_cols, categorical_cols, datetime_cols)

def create_multi_chart_dashboard(df, numeric_cols, categorical_cols, datetime_cols):
    """Create multi-chart dashboard for complex data"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(numeric_cols) >= 2:
            # Scatter plot
            fig1 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                             color=categorical_cols[0] if categorical_cols else None,
                             title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
            st.plotly_chart(fig1, use_container_width=True)
        elif numeric_cols and categorical_cols:
            # Bar chart
            fig1 = px.bar(df, x=categorical_cols[0], y=numeric_cols[0],
                         title=f"{numeric_cols[0]} by {categorical_cols[0]}")
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if numeric_cols:
            # Histogram
            fig2 = px.histogram(df, x=numeric_cols[0], 
                              title=f"{numeric_cols[0]} Distribution")
            st.plotly_chart(fig2, use_container_width=True)
        elif categorical_cols:
            # Value counts
            value_counts = df[categorical_cols[0]].value_counts().head(10)
            fig2 = px.bar(x=value_counts.values, y=value_counts.index,
                         orientation='h',
                         title=f"Top {categorical_cols[0]} Values")
            st.plotly_chart(fig2, use_container_width=True)

def display_data_summary(df, numeric_cols, categorical_cols, datetime_cols):
    """Display comprehensive data summary"""
    
    with st.expander("Data Summary", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sample Data")
            st.dataframe(df.head(10), use_container_width=True)
        
        with col2:
            st.subheader("Data Statistics")
            st.write(f"**Rows:** {len(df):,}")
            st.write(f"**Columns:** {len(df.columns)}")
            
            if numeric_cols:
                st.write("**Numeric Columns:**")
                for col in numeric_cols[:5]:  # Show max 5
                    st.write(f"- {col}")
                if len(numeric_cols) > 5:
                    st.write(f"- ... and {len(numeric_cols) - 5} more")
            
            if categorical_cols:
                st.write("**Categorical Columns:**")
                for col in categorical_cols[:5]:  # Show max 5
                    unique_count = df[col].nunique()
                    st.write(f"- {col} ({unique_count} unique values)")
                if len(categorical_cols) > 5:
                    st.write(f"- ... and {len(categorical_cols) - 5} more")
            
            if datetime_cols:
                st.write("**Date/Time Columns:**")
                for col in datetime_cols:
                    st.write(f"- {col}")

def create_plotly_chart(chart_type, df, **kwargs):
    """
    Generic function to create Plotly charts
    
    Args:
        chart_type (str): Type of chart to create
        df (pandas.DataFrame): Data for the chart
        **kwargs: Additional arguments for chart customization
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    
    chart_functions = {
        'bar': px.bar,
        'line': px.line,
        'scatter': px.scatter,
        'pie': px.pie,
        'histogram': px.histogram,
        'box': px.box,
        'heatmap': px.imshow
    }
    
    if chart_type in chart_functions:
        return chart_functions[chart_type](df, **kwargs)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

def customize_chart_appearance(fig, title=None, theme='plotly'):
    """
    Customize chart appearance
    
    Args:
        fig: Plotly figure object
        title (str): Chart title
        theme (str): Chart theme
        
    Returns:
        plotly.graph_objects.Figure: Customized figure
    """
    
    if title:
        fig.update_layout(title=title)
    
    # Apply theme
    if theme == 'business':
        fig.update_layout(
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    
    # Make responsive
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def export_chart(fig, filename, format='png'):
    """
    Export chart to file (placeholder for future implementation)
    
    Args:
        fig: Plotly figure object
        filename (str): Output filename
        format (str): Export format
    """
    # This would implement chart export functionality
    # For now, just show download option in Streamlit
    st.info("Chart export functionality would be implemented here")