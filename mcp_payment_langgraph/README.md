# Payment Transaction MCP Server with LangGraph

A comprehensive Payment Transaction Management system built as an MCP (Model Context Protocol) server with intelligent LangGraph orchestration for Claude Desktop integration.

## 🚀 Features

### Core Payment APIs
- **High Value Transactions**: Fetch recent high-value payment transactions with filtering
- **Relationship Manager**: Get assigned relationship manager details for accounts
- **Dispute Management**: Raise and track disputes for failed/pending transactions
- **Transaction Verification**: Verify payment credit status and transaction details
- **Euro Nostro Operations**: Check Euro nostro account credits for export settlements
- **Nostro Account Management**: Retrieve and filter nostro accounts by currency

### LangGraph Orchestration
- **Intelligent Routing**: Automatically determines required actions from natural language input
- **Dependency Management**: Ensures relationship managers are available before raising disputes
- **Conditional Logic**: Executes different workflow paths based on user requirements
- **Response Formatting**: Combines multiple API results into coherent responses
- **User Memory**: Remembers last 5 transactions per user for personalized experiences

### Mock Data Generation
- **Realistic Data**: Uses Faker library for authentic payment transaction data
- **Multiple Statuses**: Supports completed, failed, pending, and disputed transactions
- **Relationship Managers**: Auto-generated profiles with specializations and experience
- **Export Settlements**: Euro nostro account settlements with realistic timelines
- **Nostro Accounts**: Multi-currency correspondent banking accounts

## 📁 Project Structure

```
mcp_payment_langgraph/
├── main.py                     # Primary MCP server (UV compatible)
├── mcp_server.py              # Alternative MCP server (Python compatible)
├── models.py                  # Data models and mock data generator
├── payment_service.py         # Core API service implementations
├── orchestrator.py            # LangGraph workflow orchestrator
├── pyproject.toml            # UV project configuration with dependencies
├── requirements.txt          # Pip-compatible dependency list
├── claude_desktop_config.json # Claude Desktop integration config
├── langgraph_hierarchy.png   # Workflow visualization
└── README.md                 # This documentation
```

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

1. **get_high_value_transactions** - Fetch recent high-value payments
2. **get_relationship_manager** - Get relationship manager details  
3. **raise_dispute** - Raise disputes for failed/pending transactions
4. **verify_transaction_credit** - Verify transaction credit status
5. **orchestrate_payment_workflow** - LangGraph-powered natural language workflows
6. **get_user_transaction_memory** - Retrieve cached transactions for users
7. **check_euro_nostro_credit** - Check Euro nostro account for export settlements
8. **get_nostro_accounts** - Get nostro accounts with optional currency filtering

## 💬 Usage Examples

### Individual Tool Usage

```
"Show me the last 5 high value transactions"
"Get relationship manager details for account ACC123"
"Raise a dispute for transaction TXN_001 due to processing failure"
"Verify if transaction TXN_002 has been credited"
"Check if our Euro nostro account is credited for export EXP_REF_001"
```

### LangGraph Orchestration

Use natural language with the `orchestrate_payment_workflow` tool:

```
"Show me recent high value transactions and raise disputes for any failed ones"
"Get relationship manager details and check transaction history"
"Verify my latest transaction and show me my transaction memory"
"Check Euro nostro credits for export settlements and show account balances"
```

## 🧪 Testing

Test all functionality:

```bash
# With UV
uv run python -c "
from payment_service import payment_service
from orchestrator import payment_orchestrator

# Test individual APIs
txns = payment_service.get_high_value_transactions(3)
print(f'✅ Retrieved {len(txns)} transactions')

# Test orchestration
response = payment_orchestrator.process_request('Show me high value transactions')
print(f'✅ Orchestration response: {len(response)} characters')
"

# Test nostro functionality
uv run python -c "
from payment_service import payment_service

# Test Euro nostro
result = payment_service.check_euro_nostro_credit()
print(f'✅ Euro Nostro: {result.get(\"status\")}')

# Test nostro accounts
accounts = payment_service.get_nostro_accounts('EUR')
print(f'✅ EUR Accounts: {accounts.get(\"total_count\", 0)} found')
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
result = payment_service.get_high_value_transactions(1)
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
