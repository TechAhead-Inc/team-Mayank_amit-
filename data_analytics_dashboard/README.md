# 📊 Data Analytics Dashboard

A powerful, AI-driven single-page analytics dashboard built with Streamlit that transforms your data into actionable insights through natural language queries and interactive visualizations.

## 🌟 Features

### 🔐 Secure Authentication
- JWT-based user authentication
- Session management
- Secure login/logout functionality

### 📊 Dashboard Overview
- **Automatic Data Profiling**: Get instant insights about your dataset
- **Interactive Visualizations**: Auto-generated charts based on data types
- **Statistical Summaries**: Key metrics and data quality insights
- **Smart Recommendations**: AI-powered analysis suggestions

### 🔍 Custom Query Interface
- **Natural Language to SQL**: Ask questions in plain English
- **AI-Powered Analysis**: GPT-powered query generation and insights
- **Smart Visualizations**: Automatic chart creation based on query results
- **Query Suggestions**: Pre-built queries tailored to your data structure
- **Real-time Execution**: Instant query processing and results

### 🔬 Data Explorer
- **Interactive Filtering**: Advanced filtering capabilities for all data types
- **Column Selection**: Choose specific columns for focused analysis
- **Quick Statistics**: Instant statistical summaries
- **Column Profiling**: Deep dive into individual column characteristics
- **Export Options**: Download filtered results in multiple formats
- **Visual Analysis**: Generate charts for any subset of your data

### 💾 Data Source Support
- **PostgreSQL**: Connect to existing PostgreSQL databases
- **File Upload**: Support for CSV, Excel, and other file formats
- **Multiple Tables**: Switch between different tables/datasets
- **Real-time Connection**: Live database connectivity


## 📁 Project Structure

```
data-analytics-dashboard/
├── main.py                 # Single-page application entry point (ALL FUNCTIONALITY)
├── config/
│   └── settings.py         # Application configuration and CSS
├── auth/
│   ├── auth_ui.py         # Authentication UI components
│   └── jwt_manager.py     # JWT token management
├── database/
│   ├── connection.py      # Database connection management
│   └── queries.py         # SQL query execution
├── ai/
│   ├── openai_client.py   # OpenAI API integration
│   ├── prompt_manager.py  # AI prompt templates
│   └── response_parser.py # AI response processing
├── visualization/
│   ├── chart_generator.py      # Chart creation logic
│   ├── dashboard_components.py # UI components
│   └── data_explorer.py        # Data exploration widgets
├── utils/
│   ├── helpers.py         # Utility functions
│   └── constants.py       # Application constants
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=sk-your-openai-api-key-here

# JWT Secret Key (Required for authentication)
SECRET_KEY=your-super-secret-jwt-key-here

# Database Configuration (Optional - for PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Application Settings (Optional)
APP_TITLE=Data Analytics Dashboard
DEBUG_MODE=False
MAX_UPLOAD_SIZE=200
```

### Application Settings

Modify `config/settings.py` to customize:
- UI themes and styling
- Default chart types
- Query timeout settings
- File upload limits
- Database connection parameters

## 🎯 Usage Guide

### 1. **Authentication**
- Create an account or log in with existing credentials
- Secure session management keeps you logged in

### 2. **Connect Your Data**
**Option A: PostgreSQL Database**
- Enter database connection details in the sidebar
- Select from available tables
- Automatic schema detection

**Option B: File Upload**
- Upload CSV, Excel, or other supported files
- Automatic data type detection
- Preview data before analysis

### 3. **Dashboard Overview**
- View automatic data profiling results
- Explore generated visualizations
- Review data quality insights
- Get AI-powered analysis suggestions

### 4. **Custom Queries**
- Ask questions in natural language:
  - "Show me sales trends over the last 6 months"
  - "What are the top 10 customers by revenue?"
  - "Find correlations between price and quantity"
- Review generated SQL queries
- Explore interactive visualizations
- Export results

### 5. **Data Explorer**
- Select specific columns for analysis
- Apply filters to narrow down data
- Generate quick statistics
- Create custom visualizations
- Export filtered datasets

## 🔧 Advanced Features

### AI-Powered Query Generation
- Understands complex business questions
- Generates optimized SQL queries
- Provides context-aware suggestions
- Explains query logic and results

### Smart Visualizations
- Automatic chart type selection
- Interactive Plotly charts
- Responsive design for all screen sizes
- Export charts as images

### Data Export Options
- CSV format for spreadsheet analysis
- JSON format for API integration
- Excel format with formatting
- Filtered dataset exports

### Performance Optimization
- Query result caching
- Lazy loading for large datasets
- Optimized database connections
- Progressive data loading

## 🛠️ Development

### Adding New Features

The application follows a modular architecture. To add new functionality:

1. **Database Operations**: Add to `database/queries.py`
2. **AI Features**: Extend `ai/` modules
3. **Visualizations**: Add to `visualization/` modules
4. **UI Components**: Create in `visualization/dashboard_components.py`
5. **Main Logic**: Integrate in `main.py`



### Database Integration

Add support for new database types in `database/connection.py`:

```python
def connect_new_database(connection_params):
    # Implement connection logic
    engine = create_engine(connection_string)
    return engine
```

## 🔍 Troubleshooting

### Common Issues

**1. OpenAI API Key Error**
```
Solution: Ensure OPENAI_API_KEY is set in .env file
Check: API key has sufficient credits and permissions
```

**2. Database Connection Failed**
```
Solution: Verify database credentials and network connectivity
Check: Database server is running and accessible
```

**3. File Upload Issues**
```
Solution: Check file format and size limits
Supported: CSV, Excel (.xlsx, .xls)
Max size: 200MB (configurable)
```

**4. Visualization Errors**
```
Solution: Ensure data types are compatible with chart types
Check: No missing or invalid data in selected columns
```

### Performance Tips

- **Large Datasets**: Use data sampling for exploration
- **Complex Queries**: Monitor query execution time
- **Memory Usage**: Clear session state periodically
- **Database Connections**: Use connection pooling for production

## 📊 Example Use Cases

### Sales Analytics
```
"Show me monthly sales trends for the last year"
"Which products have the highest profit margins?"
"Compare sales performance across different regions"
```

### Customer Analysis
```
"What are the characteristics of our top customers?"
"Show customer retention rates by segment"
"Find patterns in customer purchase behavior"
```

### Financial Reporting
```
"Generate a revenue breakdown by category"
"Show expense trends over time"
"Calculate key financial ratios"
```

### Operational Insights
```
"Identify bottlenecks in our process"
"Show performance metrics by team"
"Analyze resource utilization patterns"
```


## 🙏 Acknowledgments

- **Streamlit** - For the amazing web app framework
- **OpenAI** - For powerful AI capabilities
- **Plotly** - For interactive visualizations
- **Pandas** - For data manipulation
- **Postgres Sql** - For database connectivity


## 🔄 Updates & Changelog

### Version 2.0.0 (Current)
- ✅ Consolidated single-page architecture
- ✅ Integrated all features into main.py
- ✅ Improved performance and user experience
- ✅ Enhanced AI query capabilities
- ✅ Advanced data exploration tools

### Version 1.0.0
- 🎉 Initial release with multi-page architecture
- 📊 Basic dashboard functionality
- 🔍 Custom query interface
- 🔬 Data explorer features

