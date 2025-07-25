"""
Data Explorer Page Module
"""

import streamlit as st
import pandas as pd
import numpy as np
from database.queries import execute_sql_query
from visualization.data_explorer import (
    render_column_selector, 
    render_filter_interface, 
    apply_filters,
    render_data_preview,
    render_export_options,
    render_quick_stats,
    render_column_profiler
)
from visualization.dashboard_components import render_metrics_cards, render_status_indicator
from visualization.chart_generator import create_visualization
from utils.constants import DEFAULT_VALUES

def render_data_explorer():
    """Render the data explorer page"""
    
    st.markdown('<div class="sub-header">Data Explorer</div>', unsafe_allow_html=True)
    
    try:
        # Main explorer interface
        render_explorer_interface()
        
    except Exception as e:
        st.error(f"Error in data explorer: {str(e)}")
        render_explorer_fallback()

def render_explorer_interface():
    """Render the main data explorer interface"""
    
    # Step 1: Column Selection
    st.subheader("🔍 Step 1: Select Columns to Explore")
    
    selected_columns = render_column_selector(
        columns=st.session_state.columns,
        data_types=st.session_state.data_types,
        key="explorer_columns"
    )
    
    if not selected_columns:
        st.warning("Please select at least one column to continue.")
        return
    
    # Step 2: Load and Filter Data
    st.markdown("---")
    st.subheader("⚙️ Step 2: Configure Filters and Data Settings")
    
    # Data loading controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_size = st.selectbox(
            "Sample size:",
            options=[100, 500, 1000, 5000, 10000, "All"],
            index=2,
            help="Number of records to load for exploration"
        )
    
    with col2:
        sort_column = st.selectbox(
            "Sort by column (optional):",
            options=["None"] + selected_columns,
            index=0,
            help="Choose a column to sort the data by"
        )
    
    with col3:
        sort_order = st.selectbox(
            "Sort order:",
            options=["Ascending", "Descending"],
            index=0,
            disabled=sort_column == "None"
        )
    
    # Load data based on selections
    if st.button("🔄 Load Data with Current Settings", use_container_width=True, type="primary"):
        with st.spinner("Loading data..."):
            df = load_explorer_data(selected_columns, sample_size, sort_column, sort_order)
            
            if not df.empty:
                st.session_state.explorer_data = df
                st.session_state.explorer_columns = selected_columns
                st.success(f"✅ Loaded {len(df):,} rows with {len(selected_columns)} columns")
            else:
                st.error("No data loaded. Please check your selection.")
                return
    
    # Continue with loaded data
    if 'explorer_data' in st.session_state and not st.session_state.explorer_data.empty:
        render_data_analysis_section()

def load_explorer_data(selected_columns, sample_size, sort_column, sort_order):
    """Load data based on user selections"""
    
    try:
        # Build SQL query
        columns_str = ', '.join([f'"{col}"' for col in selected_columns])
        query = f"SELECT {columns_str} FROM {st.session_state.table_name}"
        
        # Add sorting if specified
        if sort_column != "None":
            order_direction = "DESC" if sort_order == "Descending" else "ASC"
            query += f' ORDER BY "{sort_column}" {order_direction}'
        
        # Add limit if not "All"
        if sample_size != "All":
            query += f" LIMIT {sample_size}"
        
        # Execute query
        df = execute_sql_query(query, st.session_state.db_engine)
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def render_data_analysis_section():
    """Render the data analysis and exploration section"""
    
    df = st.session_state.explorer_data
    
    # Step 3: Data Analysis
    st.markdown("---")
    st.subheader("📊 Step 3: Explore and Analyze Data")
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Overview", "🔍 Filter & Search", "📈 Quick Visualizations", "🔬 Column Analysis"])
    
    with tab1:
        render_data_overview_tab(df)
    
    with tab2:
        render_filter_search_tab(df)
    
    with tab3:
        render_visualization_tab(df)
    
    with tab4:
        render_column_analysis_tab(df)

def render_data_overview_tab(df):
    """Render data overview tab"""
    
    # Quick statistics
    render_quick_stats(df)
    
    st.markdown("---")
    
    # Data preview with controls
    render_data_preview(df, max_rows=100)
    
    # Export options
    st.markdown("---")
    render_export_options(df, "explorer_data")

def render_filter_search_tab(df):
    """Render filter and search tab"""
    
    st.write("Apply filters to narrow down your data for analysis:")
    
    # Render filter interface
    filters = render_filter_interface(df, key="explorer_filters")
    
    # Apply filters and show results
    if any(filter_config is not None for filter_config in filters.values()):
        
        with st.spinner("Applying filters..."):
            filtered_df = apply_filters(df, filters)
        
        st.markdown("---")
        st.subheader("📊 Filtered Results")
        
        if not filtered_df.empty:
            # Show filter summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Original Rows", f"{len(df):,}")
            with col2:
                st.metric("Filtered Rows", f"{len(filtered_df):,}")
            
            # Show filtered data
            render_data_preview(filtered_df, max_rows=50)
            
            # Update session state with filtered data
            if st.button("🔄 Use Filtered Data for Analysis", use_container_width=True):
                st.session_state.explorer_data = filtered_df
                st.success("✅ Updated analysis data with filtered results")
                st.rerun()
            
            # Export filtered data
            st.markdown("---")
            render_export_options(filtered_df, "filtered_data")
            
        else:
            st.warning("⚠️ No data remains after applying filters. Please adjust your filter criteria.")
    
    else:
        st.info("💡 Configure filters above to narrow down your data")

def render_visualization_tab(df):
    """Render quick visualizations tab"""
    
    st.write("Generate quick visualizations of your data:")
    
    # Visualization controls
    col1, col2 = st.columns(2)
    
    with col1:
        viz_type = st.selectbox(
            "Visualization type:",
            options=["auto", "bar_chart", "line_chart", "scatter_plot", "histogram", "box_plot", "pie_chart"],
            index=0,
            help="Choose visualization type or let AI decide automatically"
        )
    
    with col2:
        chart_title = st.text_input(
            "Chart title (optional):",
            value=f"Analysis of {st.session_state.table_name}",
            help="Custom title for your visualization"
        )
    
    # Generate visualization
    if st.button("📈 Create Visualization", use_container_width=True, type="primary"):
        
        if not df.empty:
            with st.spinner("Creating visualization..."):
                
                # Limit data for performance if needed
                if len(df) > 5000:
                    display_df = df.sample(n=5000)
                    st.info(f"📊 Showing visualization for random sample of 5,000 rows (out of {len(df):,} total)")
                else:
                    display_df = df
                
                # Create visualization
                try:
                    create_visualization(
                        display_df, 
                        viz_type=viz_type if viz_type != "auto" else "bar_chart",
                        viz_reason=f"Interactive visualization of {chart_title}" if chart_title else "",
                        question="Data exploration visualization"
                    )
                except Exception as e:
                    st.error(f"Error creating visualization: {str(e)}")
                    
                    # Fallback to simple table
                    st.subheader("📋 Data Table (Fallback)")
                    st.dataframe(display_df.head(100), use_container_width=True)
        else:
            st.warning("No data available for visualization")
    
    # Additional chart options
    st.markdown("---")
    st.subheader("📊 Additional Chart Options")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        st.write("**Correlation Analysis:**")
        if st.button("📈 Show Correlation Matrix", use_container_width=True):
            try:
                create_visualization(df[numeric_cols], viz_type="heatmap", viz_reason="Correlation analysis of numeric columns")
            except Exception as e:
                st.error(f"Error creating correlation matrix: {str(e)}")
    
    if categorical_cols:
        st.write("**Category Analysis:**")
        selected_cat_col = st.selectbox("Select categorical column:", categorical_cols)
        if st.button(f"📊 Analyze {selected_cat_col}", use_container_width=True):
            try:
                # Create value counts visualization
                value_counts = df[selected_cat_col].value_counts().head(20)
                counts_df = pd.DataFrame({
                    selected_cat_col: value_counts.index,
                    'Count': value_counts.values
                })
                create_visualization(counts_df, viz_type="bar_chart", viz_reason=f"Distribution of {selected_cat_col}")
            except Exception as e:
                st.error(f"Error analyzing categorical data: {str(e)}")

def render_column_analysis_tab(df):
    """Render detailed column analysis tab"""
    
    st.write("Dive deep into individual columns:")
    
    # Column selection for analysis
    analysis_column = st.selectbox(
        "Select column for detailed analysis:",
        options=df.columns.tolist(),
        help="Choose a column to analyze in detail"
    )
    
    if analysis_column:
        
        # Column profiling
        render_column_profiler(df, analysis_column)
        
        st.markdown("---")
        
        # Column-specific visualizations
        col_data = df[analysis_column]
        
        if pd.api.types.is_numeric_dtype(col_data):
            render_numeric_column_analysis(df, analysis_column)
        elif col_data.dtype == 'object':
            render_categorical_column_analysis(df, analysis_column)
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            render_datetime_column_analysis(df, analysis_column)

def render_numeric_column_analysis(df, column):
    """Render analysis for numeric columns"""
    
    st.subheader(f"📊 Numeric Analysis: {column}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📈 Distribution of {column}", use_container_width=True):
            hist_df = pd.DataFrame({column: df[column].dropna()})
            create_visualization(hist_df, viz_type="histogram", viz_reason=f"Distribution analysis of {column}")
    
    with col2:
        if st.button(f"📦 Box Plot of {column}", use_container_width=True):
            box_df = pd.DataFrame({column: df[column].dropna()})
            create_visualization(box_df, viz_type="box_plot", viz_reason=f"Box plot analysis of {column}")
    
    # Correlation with other numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    other_numeric = [col for col in numeric_cols if col != column]
    
    if other_numeric:
        st.write("**Correlation with other numeric columns:**")
        corr_column = st.selectbox(f"Compare {column} with:", other_numeric)
        
        if st.button(f"📈 Scatter Plot: {column} vs {corr_column}", use_container_width=True):
            scatter_df = df[[column, corr_column]].dropna()
            create_visualization(scatter_df, viz_type="scatter_plot", viz_reason=f"Relationship between {column} and {corr_column}")

def render_categorical_column_analysis(df, column):
    """Render analysis for categorical columns"""
    
    st.subheader(f"📝 Categorical Analysis: {column}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📊 Value Counts for {column}", use_container_width=True):
            value_counts = df[column].value_counts().head(20)
            counts_df = pd.DataFrame({
                column: value_counts.index,
                'Count': value_counts.values
            })
            create_visualization(counts_df, viz_type="bar_chart", viz_reason=f"Value distribution of {column}")
    
    with col2:
        if st.button(f"🥧 Pie Chart for {column}", use_container_width=True):
            value_counts = df[column].value_counts().head(10)
            pie_df = pd.DataFrame({
                column: value_counts.index,
                'Count': value_counts.values
            })
            create_visualization(pie_df, viz_type="pie_chart", viz_reason=f"Composition analysis of {column}")
    
    # Cross-tabulation with other categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    other_categorical = [col for col in categorical_cols if col != column]
    
    if other_categorical:
        st.write("**Cross-tabulation with other categorical columns:**")
        cross_column = st.selectbox(f"Cross-analyze {column} with:", other_categorical)
        
        if st.button(f"📊 Cross-tab: {column} vs {cross_column}", use_container_width=True):
            try:
                # Create cross-tabulation
                crosstab = pd.crosstab(df[column], df[cross_column])
                
                # Show as heatmap if not too large
                if crosstab.shape[0] <= 20 and crosstab.shape[1] <= 20:
                    create_visualization(crosstab, viz_type="heatmap", viz_reason=f"Cross-tabulation of {column} and {cross_column}")
                else:
                    st.write("**Cross-tabulation Results:**")
                    st.dataframe(crosstab.head(20), use_container_width=True)
                    st.info("Cross-tabulation too large for heatmap visualization")
            except Exception as e:
                st.error(f"Error creating cross-tabulation: {str(e)}")
    
    # Relationship with numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        st.write("**Relationship with numeric columns:**")
        numeric_column = st.selectbox(f"Analyze {column} by:", numeric_cols)
        
        if st.button(f"📊 {numeric_column} by {column}", use_container_width=True):
            try:
                # Group by categorical and aggregate numeric
                grouped = df.groupby(column)[numeric_column].agg(['mean', 'count']).reset_index()
                grouped = grouped.sort_values('mean', ascending=False).head(20)
                
                # Rename columns for visualization
                grouped.columns = [column, f'Average {numeric_column}', 'Count']
                
                create_visualization(
                    grouped[[column, f'Average {numeric_column}']], 
                    viz_type="bar_chart", 
                    viz_reason=f"Average {numeric_column} by {column}"
                )
            except Exception as e:
                st.error(f"Error creating grouped analysis: {str(e)}")

def render_datetime_column_analysis(df, column):
    """Render analysis for datetime columns"""
    
    st.subheader(f"📅 DateTime Analysis: {column}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"📈 Time Series for {column}", use_container_width=True):
            try:
                # Create time series count
                time_counts = df[column].dt.date.value_counts().sort_index()
                time_df = pd.DataFrame({
                    'Date': time_counts.index,
                    'Count': time_counts.values
                })
                create_visualization(time_df, viz_type="line_chart", viz_reason=f"Time series analysis of {column}")
            except Exception as e:
                st.error(f"Error creating time series: {str(e)}")
    
    with col2:
        if st.button(f"📊 Monthly Distribution", use_container_width=True):
            try:
                # Create monthly distribution
                monthly_counts = df[column].dt.month.value_counts().sort_index()
                month_df = pd.DataFrame({
                    'Month': monthly_counts.index,
                    'Count': monthly_counts.values
                })
                create_visualization(month_df, viz_type="bar_chart", viz_reason=f"Monthly distribution of {column}")
            except Exception as e:
                st.error(f"Error creating monthly distribution: {str(e)}")

def render_explorer_fallback():
    """Render fallback interface when main explorer fails"""
    
    st.subheader("📋 Basic Data Information")
    
    if st.session_state.table_name:
        st.write(f"**Table:** {st.session_state.table_name}")
        st.write(f"**Available Columns:** {len(st.session_state.columns)}")
        
        if st.session_state.columns:
            # Show column list
            st.write("**Columns:**")
            for i, col in enumerate(st.session_state.columns[:20]):  # Show first 20
                dtype = st.session_state.data_types.get(col, 'unknown')
                st.write(f"{i+1}. **{col}** ({dtype})")
            
            if len(st.session_state.columns) > 20:
                st.write(f"... and {len(st.session_state.columns) - 20} more columns")
        
        # Basic data sample
        st.subheader("📋 Data Sample")
        try:
            sample_df = execute_sql_query(
                f"SELECT * FROM {st.session_state.table_name} LIMIT 10", 
                st.session_state.db_engine
            )
            
            if not sample_df.empty:
                st.dataframe(sample_df, use_container_width=True)
            else:
                st.warning("No sample data available")
                
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")

def save_exploration_state():
    """Save current exploration state for later use"""
    
    if 'explorer_data' in st.session_state:
        st.session_state.saved_exploration = {
            'data': st.session_state.explorer_data,
            'columns': st.session_state.get('explorer_columns', []),
            'timestamp': pd.Timestamp.now()
        }
        st.success("✅ Exploration state saved!")

def load_exploration_state():
    """Load previously saved exploration state"""
    
    if 'saved_exploration' in st.session_state:
        saved = st.session_state.saved_exploration
        st.session_state.explorer_data = saved['data']
        st.session_state.explorer_columns = saved['columns']
        st.success(f"✅ Loaded exploration from {saved['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.warning("No saved exploration state found")

def clear_exploration_data():
    """Clear current exploration data"""
    
    keys_to_clear = ['explorer_data', 'explorer_columns', 'saved_exploration']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ Exploration data cleared")

def render_exploration_controls():
    """Render exploration state management controls"""
    
    st.markdown("---")
    st.subheader("💾 Exploration State Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Current State", use_container_width=True):
            save_exploration_state()
    
    with col2:
        if st.button("📁 Load Saved State", use_container_width=True):
            load_exploration_state()
    
    with col3:
        if st.button("🗑️ Clear Data", use_container_width=True):
            clear_exploration_data()
            st.rerun()

def render_data_summary_sidebar():
    """Render data summary in sidebar"""
    
    if 'explorer_data' in st.session_state:
        df = st.session_state.explorer_data
        
        with st.sidebar:
            st.subheader("📊 Current Data Summary")
            
            metrics = [
                {'label': 'Rows', 'value': len(df)},
                {'label': 'Columns', 'value': len(df.columns)},
            ]
            
            # Data type breakdown
            numeric_count = len(df.select_dtypes(include=[np.number]).columns)
            text_count = len(df.select_dtypes(include=['object']).columns)
            
            if numeric_count > 0:
                st.write(f"📊 Numeric: {numeric_count}")
            if text_count > 0:
                st.write(f"📝 Text: {text_count}")
            
            # Memory usage
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            st.write(f"💾 Memory: {memory_mb:.1f} MB")
            
            # Quick actions
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("📋 Show Info", use_container_width=True):
                st.session_state.show_data_info = True

# Add this function call at the end of render_data_explorer() if needed
def finalize_explorer_page():
    """Finalize the explorer page with additional controls"""
    
    # Add exploration controls if data is loaded
    if 'explorer_data' in st.session_state:
        render_exploration_controls()
    
    # Add sidebar summary
    render_data_summary_sidebar()
    
    # Show data info if requested
    if st.session_state.get('show_data_info', False):
        with st.expander("📋 Detailed Data Information", expanded=True):
            if 'explorer_data' in st.session_state:
                df = st.session_state.explorer_data
                st.write(f"**Shape:** {df.shape}")
                st.write(f"**Data Types:**")
                for col, dtype in df.dtypes.items():
                    st.write(f"- {col}: {dtype}")
        
        st.session_state.show_data_info = False