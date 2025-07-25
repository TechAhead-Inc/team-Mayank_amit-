"""
Data Analytics Dashboard - Single Page Application Entry Point
"""

import streamlit as st
from config.settings import load_app_config, CUSTOM_CSS
from auth.auth_ui import render_authentication
from auth.jwt_manager import get_current_user
from pages.dashboard_overview import render_dashboard_overview
from pages.custom_query import render_custom_query
from pages.data_explorer_page import render_data_explorer
from utils.helpers import initialize_session_state

def main():
    """Main application entry point"""
    
    # Load configuration
    config = load_app_config()
    
    # Set page configuration
    st.set_page_config(
        page_title="Data Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Check authentication
    current_user = get_current_user()
    
    if not current_user:
        # Show authentication interface
        render_authentication()
    else:
        # Show main dashboard
        render_single_page_dashboard(current_user)

def render_single_page_dashboard(current_user):
    """Render the single page dashboard interface"""
    
    # Main header
    st.markdown('<div class="main-header">Data Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar with user info and data connection
    render_sidebar(current_user)
    
    # Check if data is connected
    if st.session_state.db_engine and st.session_state.table_name and st.session_state.columns:
        # Single page layout - all components in one page
        render_unified_dashboard()
    elif st.session_state.db_engine:
        st.info("Please select a table from the sidebar to get started!")
    else:
        render_welcome_screen()

def render_unified_dashboard():
    """Render all dashboard components in a single unified page"""
    
    # Add section selector in the main area (optional)
    st.subheader("📊 Analytics Dashboard")
    
    # Section navigation (optional - you can remove this if you want everything visible at once)
    section = st.selectbox(
        "Choose section to focus on:",
        ["All Sections", "Dashboard Overview", "Custom Query", "Data Explorer"],
        index=0,
        help="Select which section to display, or 'All Sections' to show everything"
    )
    
    # Render sections based on selection
    if section == "All Sections":
        render_all_sections()
    elif section == "Dashboard Overview":
        render_dashboard_overview()
    elif section == "Custom Query":
        render_custom_query()
    elif section == "Data Explorer":
        render_data_explorer()

def render_all_sections():
    """Render all sections in a single scrollable page"""
    
    # Dashboard Overview Section
    with st.container():
        st.markdown("---")
        st.markdown("## 📊 Dashboard Overview")
        render_dashboard_overview()
    
    # Custom Query Section
    with st.container():
        st.markdown("---")
        st.markdown("## 🔍 Custom Query Interface")
        render_custom_query()
    
    # Data Explorer Section
    with st.container():
        st.markdown("---")
        st.markdown("## 🔬 Data Explorer")
        render_data_explorer()

def render_sidebar(current_user):
    """Render sidebar with user info and data connection only"""
    from auth.auth_ui import render_user_info_sidebar
    from database.connection import render_data_connection_ui
    
    with st.sidebar:
        # User information and logout
        render_user_info_sidebar(current_user)
        
        # Data connection interface
        render_data_connection_ui()
        
        # Optional: Add quick navigation for single page
        if st.session_state.db_engine and st.session_state.table_name and st.session_state.columns:
            st.markdown("---")
            st.markdown("### 🧭 Quick Navigation")
            
            if st.button("📊 Dashboard Overview", use_container_width=True):
                st.session_state.scroll_to = "dashboard_overview"
            
            if st.button("🔍 Custom Query", use_container_width=True):
                st.session_state.scroll_to = "custom_query"
            
            if st.button("🔬 Data Explorer", use_container_width=True):
                st.session_state.scroll_to = "data_explorer"

def render_welcome_screen():
    """Render welcome screen when no data is connected"""
    st.info("Please connect your data source from the sidebar to get started!")
    
    # Show feature overview
    st.markdown("### 🚀 Dashboard Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Dashboard Overview**
        - Automatic data profiling
        - Interactive visualizations  
        - Statistical summaries
        - Data quality insights
        """)
    
    with col2:
        st.markdown("""
        **🔍 Custom Queries**
        - Natural language to SQL
        - AI-powered analysis
        - Smart visualizations
        - Business insights
        """)
    
    with col3:
        st.markdown("""
        **🔬 Data Explorer**
        - Interactive filtering
        - Column selection
        - Quick statistics
        - Export capabilities
        """)
    
    # Getting started guide
    st.markdown("---")
    st.markdown("### 🎯 Getting Started")
    
    st.markdown("""
    **Follow these steps to start analyzing your data:**
    
    1. **🔗 Connect Data Source**: Use the sidebar to connect to PostgreSQL or upload a file
    2. **📋 Select Table**: Choose which table/dataset you want to analyze  
    3. **🚀 Start Exploring**: Once connected, all analytics features will be available on this single page:
        - **Dashboard Overview**: Get automatic insights and visualizations
        - **Custom Query**: Ask questions in natural language
        - **Data Explorer**: Filter and explore your data interactively
    
    **💡 Pro Tip**: All features are integrated into one seamless experience - no need to switch between pages!
    """)
    
    # Add some visual elements
    st.markdown("---")
    st.markdown("### 🌟 Why Choose This Dashboard?")
    
    benefits_col1, benefits_col2 = st.columns(2)
    
    with benefits_col1:
        st.markdown("""
        **✨ Key Benefits:**
        - 🚀 Fast and intuitive interface
        - 🤖 AI-powered query generation
        - 📊 Automatic visualization creation
        - 🔍 Advanced data exploration
        - 💾 Multiple data source support
        """)
    
    with benefits_col2:
        st.markdown("""
        **🔧 Technical Features:**
        - 🔐 Secure authentication
        - 📱 Responsive design
        - ⚡ Real-time query execution
        - 📈 Interactive charts
        - 📁 Data export capabilities
        """)

# Alternative simplified version without section selector
def render_simplified_dashboard():
    """Alternative: Render everything on one page without section selector"""
    
    # Dashboard Overview Section
    st.markdown("## 📊 Dashboard Overview")
    render_dashboard_overview()
    
    # Separator
    st.markdown("---")
    
    # Custom Query Section  
    st.markdown("## 🔍 Ask Questions About Your Data")
    render_custom_query()
    
    # Separator
    st.markdown("---")
    
    # Data Explorer Section
    st.markdown("## 🔬 Explore Your Data")
    render_data_explorer()

if __name__ == "__main__":
    main()