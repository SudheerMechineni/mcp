# Payment Transaction MCP Server with LangGraph

A comprehensive Payment Transaction Management system built as an MCP (Model Context Protocol) server with intelligent LangGraph orchestration for Claude Desktop integration. Features persistent SQLite database storage and multi-customer support.

## 🛠️ Recent Fixes
- Fixed dispute management error: Added missing `resolution_date` column to `disputes` table
- Cleaned up unwanted files: payment_service_old.py, payment_service_new.py, payment_transactions.db-journal
- All MCP tools tested and working without errors

## 🚀 MCP Payment Transaction Server (LangGraph)

### Key Features
- Recent transactions: Fetch recent transactions (last 30 days, >100K by default)
- Relationship manager: Get details for current customer
- Customer switching: Switch context by ID or name
- List customers: View all available customers
- Service requests: Raise a service request for failed or pending transactions
- Transaction verification: Check if a transaction is credited
- Nostro accounts: View and filter nostro accounts, including EUR settlements
- Treasury pricing, investment proposals, cash forecasts, risk limits

### Tool Names (API)
- get_recent_transactions
- get_relationship_manager
- switch_customer
- list_customers
- raise_servicerequest
- verify_transaction_credit
- get_nostro_accounts
- get_treasury_pricing
- get_investment_proposals
- get_cash_forecasts
- get_risk_limits

### Recent Changes
- All references to 'dispute' replaced with 'servicerequest'
- 'get_high_value_transactions' replaced with 'get_recent_transactions'
- Codebase cleaned and error-free

### Usage Example
```
uv run python -c "from main import server; print('✅ MCP Server ready')"
```

## 📊 Database Schema

The system uses SQLite with 12 comprehensive tables:
- **customers**: Customer profiles and details
- **high_value_transactions**: Payment transactions above threshold
- **relationship_managers**: Account relationship managers
- **disputes**: Transaction dispute tracking
- **transaction_verifications**: Transaction verification records
- **nostro_accounts**: Correspondent banking accounts
- **euro_nostro_settlements**: Euro settlement tracking
- **treasury_pricing**: FX pricing data 🆕
- **investment_proposals**: Investment opportunities 🆕
- **cash_forecasts**: Cash flow projections 🆕
- **risk_limits**: Risk management limits 🆕
- **request_logs**: API audit trail 🆕

## 📁 Project Structure

```
mcp_payment_langgraph/
├── main.py                     # Primary MCP server (UV compatible)
├── mcp_server.py              # Alternative MCP server (Python compatible)
├── database.py                # SQLite database management 🆕
├── customer_manager.py        # Customer context switching 🆕
├── logger.py                  # Request/response logging 🆕
├── payment_service.py         # Core API service implementations (database-backed)
├── orchestrator.py            # LangGraph workflow orchestrator
├── models.py                  # Legacy data models (now replaced by database)
├── pyproject.toml            # UV project configuration with dependencies
├── requirements.txt          # Pip-compatible dependency list
├── claude_desktop_config.json # Claude Desktop integration config
├── langgraph_hierarchy.png   # Workflow visualization
├── payment_transactions.db   # SQLite database file (auto-created) 🆕
├── mcp_server.log           # Server log file (auto-created) 🆕
└── README.md                 # This documentation
```

## 📈 Development Status

### ✅ Completed Features (Version 2.0)
- **SQLite Database Integration**: Persistent storage with 12 comprehensive tables
- **Multi-Customer Support**: 5 customer profiles with seamless context switching
- **Enhanced Transaction Filtering**: Date ranges, amount thresholds, customer context
- **Treasury Services**: FX pricing, investment proposals, cash forecasts, risk limits
- **Audit Logging**: Request/response logging with execution time tracking
- **Auto-Population**: Realistic mock data generation on first run
- **MCP Tool Integration**: 12 enhanced MCP tools for Claude Desktop

### 🔄 Recently Enhanced
- **Enhanced Euro Nostro Logic**: Database-backed settlement tracking
- **Customer Context Management**: Natural language detection and switching
- **Performance Monitoring**: Execution time tracking for all operations
- **Data Integrity**: Foreign key relationships and database constraints

### 🎯 Future Enhancements (Optional)
- **LangGraph Orchestration**: Complex workflow automation (code exists, commented out)
- **User Memory System**: Transaction caching per user (code exists, commented out)
- **Advanced Analytics**: Transaction pattern analysis and insights
- **Real-time Notifications**: Payment status change alerts

## 🔧 Technical Implementation

### Database Architecture
- **SQLite File**: `payment_transactions.db` (auto-created)
- **12 Tables**: Comprehensive relational schema with foreign keys
- **Data Population**: Faker-generated realistic data on first run
- **Context Management**: Customer-aware queries and operations

### Logging & Monitoring
- **File Logging**: `mcp_server.log` with detailed request/response logs
- **Database Audit**: `request_logs` table for persistence
- **Performance Tracking**: Execution time monitoring
- **Customer Context**: All logs include current customer information

## 📊 Sample Data

The system automatically generates:
- **5 Customers**: Corporate (Smith-Bennett), Financial (Lambert and Sons), Government (Esparza-Thomas), SME (Spencer-Cruz), Private Banking (Tina Palmer)
- **10-25 Transactions per Customer**: High-value payments with realistic amounts and currencies
- **Relationship Managers**: Assigned to each customer with specializations
- **Treasury Data**: FX pricing, investment proposals, cash forecasts, risk limits
- **Nostro Accounts**: Multi-currency correspondent banking accounts (USD, EUR, GBP, JPY, CHF)

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12 or higher
- UV package manager (recommended) or pip

### Quick Start with UV (Recommended)

```bash
# Clone or navigate to the project directory
cd mcp_payment_langgraph

# Install dependencies
uv sync

# Test the installation
uv run python -c "from main import server; print('✅ Setup successful')"
```

### Alternative: Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Test the installation
python -c "from main import server; print('✅ Setup successful')"
```

## 🔧 Claude Desktop Integration

### For UV Users (Recommended)

Add this configuration to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "payment-transaction-server": {
      "command": "/Users/[username]/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/mcp_payment_langgraph",
        "run",
        "main.py"
      ]
    }
  }
}
```

### For Standard Python Users

```json
{
  "mcpServers": {
    "payment-transaction-server": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/mcp_payment_langgraph"
    }
  }
}
```

## 🎯 Available MCP Tools

### Customer Management 🆕
1. **switch_customer** - Switch between different customer contexts by ID, name, or partial match
2. **list_customers** - List all available customers with their details

### Core Payment Operations
3. **get_recent_transactions** - Fetch recent transactions (enhanced with filtering)
4. **get_relationship_manager** - Get relationship manager details  
5. **raise_servicerequest** - Raise a service request for failed/pending transactions
6. **verify_transaction_credit** - Verify transaction credit status

### Nostro Account Operations
7. **get_nostro_accounts** - Get nostro accounts with optional currency filtering (for EUR: includes settlement details and export reference tracking)

### Treasury & Personalized Journey 🆕
8. **get_treasury_pricing** - Get FX pricing and rates for the current customer
9. **get_investment_proposals** - Get personalized investment opportunities
10. **get_cash_forecasts** - Get cash flow forecasts and projections
11. **get_risk_limits** - Get risk limits and utilization monitoring

### ⚠️ Advanced Features (Currently Disabled)
The following tools are commented out in the code but can be re-enabled if needed:
- **orchestrate_payment_workflow** - LangGraph-powered natural language workflows

## 💡 Usage Examples

### Customer Switching
```
User: "Show me transactions for Smith-Bennett"
System: [Automatically switches to Smith-Bennett customer and shows their transactions]

User: "Switch to customer CUST_729051"
System: [Switches to that customer ID]

User: "List all customers"
System: [Shows all 5 available customers]
```

### Enhanced Transaction Filtering
```
User: "Show me recent transactions from last week"
System: [Shows transactions with 7-day filter]

User: "Show me transactions over 500K from the last month"
System: [Shows transactions with custom amount threshold and 30-day filter]
```

### Treasury Services
```
User: "What are the current FX rates for this customer?"
System: [Shows personalized treasury pricing]

User: "Show me investment opportunities"
System: [Shows customer-specific investment proposals]

User: "What's our cash forecast for next quarter?"
System: [Shows cash flow projections]
```
- **get_user_transaction_memory** - Retrieve cached transactions for users

*To re-enable these features, uncomment the relevant sections in `main.py`*

## 💬 Usage Examples

### Individual Tool Usage

```
"Show me the last 5 recent transactions"
"Get relationship manager details for account ACC123"
"Raise a service request for transaction TXN_001 due to processing failure"
"Verify if transaction TXN_002 has been credited"
"Check if our Euro nostro account is credited for export EXP_REF_001"
"Show me all EUR nostro accounts"
```

### ⚠️ Advanced Usage (Requires Re-enabling Features)

*The following examples require uncommenting the LangGraph orchestration tools in `main.py`:*

```
"Show me recent transactions and raise service requests for any failed ones"
"Get relationship manager details and check transaction history"
"Verify my latest transaction and show me my transaction memory"
"Check Euro nostro credits for export settlements and show account balances"
```

## 🧪 Testing

Test core functionality:

```bash
# With UV
uv run python -c "
from payment_service import payment_service

# Test individual APIs
txns = payment_service.get_recent_transactions(3)
print(f'✅ Retrieved {len(txns)} transactions')

rm = payment_service.get_relationship_manager_details()
print(f'✅ Retrieved RM: {rm[\"name\"]}')
"

# Test nostro functionality
uv run python -c "
from payment_service import payment_service

# Test consolidated nostro accounts (now includes EUR settlement details)
accounts = payment_service.get_nostro_accounts('EUR', 'EXP_2025_001')
print(f'✅ EUR Nostro with Settlement: {accounts.get(\"total_count\", 0)} accounts found')

# Test general nostro accounts
accounts = payment_service.get_nostro_accounts()
print(f'✅ All Nostro Accounts: {accounts.get(\"total_count\", 0)} found')
"

# Test MCP server startup
uv run python -c "from main import server; print('✅ MCP Server ready')"
```

### Advanced Testing (Requires Re-enabling LangGraph)

*To test orchestration features, uncomment the LangGraph tools in `main.py` first:*

```bash
uv run python -c "
from orchestrator import payment_orchestrator
response = payment_orchestrator.process_request('Show me recent transactions')
print(f'✅ Orchestration response: {len(response)} characters')
"
```

## 🔄 Workflow Diagram

The LangGraph workflow intelligently routes requests through appropriate APIs:

```
User Input → Analyze Request → Route Actions → Execute APIs → Format Response
     ↓              ↓              ↓              ↓              ↓
Natural Language → Action Detection → Conditional Logic → API Calls → Unified Output
```

See `langgraph_hierarchy.png` for the complete visual workflow.

## 📦 Dependencies

- **mcp** (≥1.12.4): Model Context Protocol server framework
- **langgraph** (≥0.6.4): Workflow orchestration and state management  
- **langchain-core** (≥0.3.74): Core language model abstractions
- **faker** (≥22.0.0): Realistic mock data generation
- **pydantic** (≥2.11.0): Data validation and serialization
- **fastapi** (≥0.116.1): HTTP server capabilities (optional)
- **uvicorn** (≥0.35.0): ASGI server (optional)
- **httpx** (≥0.28.1): HTTP client functionality
- **graphviz** (≥0.21): Workflow visualization
- **python-dateutil** (≥2.9.0.post0): Date/time utilities

## 🔧 Development & Extension

### Adding New APIs
1. Define data models in `models.py`
2. Implement API logic in `payment_service.py`
3. Add workflow nodes in `orchestrator.py`
4. Register MCP tools in `main.py`

### Testing Changes
```bash
# Quick validation
uv run python -c "from main import server; print('✅ Imports working')"

# Test specific functionality
uv run python -c "
from payment_service import payment_service
result = payment_service.get_recent_transactions(1)
print('✅ API test passed')
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `uv sync`
2. **Claude Desktop Connection**: Verify the path in `claude_desktop_config.json` is absolute
3. **Permission Issues**: Make sure UV binary path is correct in config
4. **Module Not Found**: Use `uv run` prefix for all Python commands

### Debug Mode

Enable detailed logging by checking stderr output when running with Claude Desktop.

## 🎯 Key Features Summary

✅ **8 Core MCP Tools** - Complete payment transaction management  
✅ **LangGraph Orchestration** - Intelligent natural language workflows  
✅ **Mock Data Generation** - Realistic test data with Faker  
✅ **Memory Management** - User transaction history tracking  
✅ **Euro Nostro Operations** - Specialized export settlement features  
✅ **Multi-Currency Support** - USD, EUR, GBP, JPY, CHF  
✅ **Claude Desktop Ready** - Plug-and-play MCP integration  
✅ **UV Compatible** - Modern Python package management  

## 📋 Project Status

This is a **production-ready** MCP server with comprehensive payment transaction management capabilities. All core features are implemented and tested, with clean codebase and updated dependencies.

**Last Updated**: August 2025  
**Dependencies**: All packages updated to latest versions  
**Compatibility**: Python 3.12+, UV package manager, Claude Desktop MCP

## 🔄 Recent Changes

### Cleanup & Updates (August 2025)
- ✅ **Removed unused files**: Eliminated duplicate documentation, test files, and setup scripts
- ✅ **Updated dependencies**: All packages upgraded to latest versions (mcp 1.12.4, langgraph 0.6.4, etc.)
- ✅ **Streamlined structure**: Clean project with only essential files remaining
- ✅ **Verified functionality**: All imports and core features tested and working
- ✅ **Refreshed documentation**: Updated README with current project state

### Core Files Retained
- `main.py` - Primary UV-compatible MCP server
- `mcp_server.py` - Alternative Python-compatible MCP server  
- `models.py` - Data models and mock data generation
- `payment_service.py` - API implementations
- `orchestrator.py` - LangGraph workflow management
- `pyproject.toml` & `requirements.txt` - Dependency management
- `claude_desktop_config.json` - Integration configuration

**Ready for production use with Claude Desktop!** 🚀

## 🔧 Re-enabling Advanced Features

The LangGraph orchestration tools are commented out but can be easily re-enabled:

### To Re-enable `orchestrate_payment_workflow` and `get_user_transaction_memory`:

1. **In `main.py`**, uncomment the tool definitions around lines 87-108:
   ```python
   # Remove the comment markers from:
   # Tool(name="orchestrate_payment_workflow", ...)
   # Tool(name="get_user_transaction_memory", ...)
   ```

2. **In `main.py`**, uncomment the tool handlers around lines 245-287:
   ```python
   # Remove the comment markers from:
   # elif name == "orchestrate_payment_workflow":
   # elif name == "get_user_transaction_memory":
   ```

3. **Restart Claude Desktop** to load the updated tools

### Benefits of Re-enabling:
- Natural language multi-step workflows
- User transaction memory and caching
- Complex orchestration capabilities
- Advanced LangGraph features

These tools were commented out to simplify the Claude Desktop interface but remain fully functional when enabled.
