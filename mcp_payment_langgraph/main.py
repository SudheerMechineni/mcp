#!/usr/bin/env python3
"""
MCP Server for Payment Transactions - UV Compatible
This version is designed to work with 'uv run' command for Claude Desktop
"""

import asyncio
import json
import sys
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
import mcp.server.stdio

# Add debug output to stderr for troubleshooting
print("Starting MCP Payment Transaction Server...", file=sys.stderr)

try:
    from orchestrator import payment_orchestrator
    from payment_service import payment_service
    from customer_manager import customer_manager
    from logger import request_logger
    from database import payment_db
    print("Successfully imported payment modules", file=sys.stderr)
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    raise

# Create MCP server instance
server = Server("payment-transaction-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available MCP tools for payment operations"""
    print("Listing tools...", file=sys.stderr)
    return [
        Tool(
            name="get_recent_transactions",
            description="Fetch recent transactions (last 30 days by default, >100K by default)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to fetch (default: 5)",
                        "default": 5
                    },
                    "days_filter": {
                        "type": "integer", 
                        "description": "Number of days to look back (default: 30 for 'recent', 7 for 'last week', 14 for 'past 2 weeks')",
                        "default": 30
                    },
                    "min_amount": {
                        "type": "number",
                        "description": "Minimum amount for transaction filter (default: 100000)",
                        "default": 100000
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID to switch context (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_relationship_manager",
            description="Get relationship manager details for current customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID to switch context (optional)"
                    }
                }
            }
        ),
        Tool(
            name="switch_customer",
            description="Switch customer context using customer ID or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_identifier": {
                        "type": "string",
                        "description": "Customer ID, customer name, or partial name to switch to"
                    }
                },
                "required": ["customer_identifier"]
            }
        ),
        Tool(
            name="list_customers", 
            description="List all available customers with their details",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="raise_servicerequest",
            description="Raise a service request for failed or pending payment transactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "ID of the transaction for service request"
                    },
                    "servicerequest_reason": {
                        "type": "string",
                        "description": "Reason for raising the service request"
                    }
                },
                "required": ["transaction_id", "servicerequest_reason"]
            }
        ),
        Tool(
            name="verify_transaction_credit",
            description="Verify whether a transaction has been credited to the account",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "ID of the transaction to verify"
                    }
                },
                "required": ["transaction_id"]
            }
        ),
        Tool(
            name="get_nostro_accounts",
            description="Get nostro accounts, optionally filtered by currency. For EUR, includes settlement details",
            inputSchema={
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Currency filter (EUR, USD, GBP, etc.) - optional"
                    },
                    "export_reference": {
                        "type": "string", 
                        "description": "For EUR currency, specific export reference to check settlements - optional"
                    }
                }
            }
        ),
        # Personalized Journey Assembly Tools
        Tool(
            name="get_treasury_pricing",
            description="Get treasury FX pricing for customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string", 
                        "description": "Customer ID (optional, uses current context)"
                    }
                }
            }
        ),
        Tool(
            name="get_investment_proposals",
            description="Get investment proposals and opportunities for customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (optional, uses current context)"
                    }
                }
            }
        ),
        Tool(
            name="get_cash_forecasts",
            description="Get cash flow forecasts for customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (optional, uses current context)"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (default: 30)",
                        "default": 30
                    }
                }
            }
        ),
        Tool(
            name="get_risk_limits",
            description="Get risk limits and utilization for customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (optional, uses current context)"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls for payment operations"""
    
    print(f"Calling tool: {name} with args: {arguments}", file=sys.stderr)
    
    if arguments is None:
        arguments = {}
    
    try:
        # Handle customer switching from user input if available
        user_input = ""
        for key in ["user_request", "customer_identifier"]:
            if key in arguments and arguments[key]:
                user_input = str(arguments[key])
                break
        
        if user_input:
            customer_switch = customer_manager.detect_customer_switch_request(user_input)
            if customer_switch:
                customer_manager.switch_customer(customer_switch)
        
        if name == "get_recent_transactions":
            limit = arguments.get("limit", 5)
            days_filter = arguments.get("days_filter", 30)
            min_amount = arguments.get("min_amount", 100000.0)
            customer_id = arguments.get("customer_id")
            
            # Switch customer if requested
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_transactions(
                limit=limit, 
                days_filter=days_filter, 
                min_amount=min_amount,
                customer_id=customer_id
            )
            
            current_customer = customer_manager.get_current_customer()
            customer_name = current_customer['customer_name'] if current_customer else 'Unknown'
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "customer": customer_name,
                        "filters": {
                            "days_filter": days_filter,
                            "min_amount": min_amount
                        },
                        "message": f"Retrieved {len(result)} recent transactions for {customer_name}"
                    }, indent=2)
                )
            ]
        
        elif name == "get_relationship_manager":
            customer_id = arguments.get("customer_id")
            
            # Switch customer if requested
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_relationship_manager_details(customer_id)
            
            current_customer = customer_manager.get_current_customer()
            customer_name = current_customer['customer_name'] if current_customer else 'Unknown'
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "customer": customer_name,
                        "message": f"Retrieved relationship manager for {customer_name}"
                    }, indent=2)
                )
            ]
        
        elif name == "switch_customer":
            customer_identifier = arguments.get("customer_identifier")
            if not customer_identifier:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "customer_identifier is required"
                        }, indent=2)
                    )
                ]
            
            success = customer_manager.switch_customer(customer_identifier)
            if success:
                current_customer = customer_manager.get_current_customer()
                if current_customer:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "success",
                                "data": current_customer,
                                "message": f"Successfully switched to customer: {current_customer['customer_name']}"
                            }, indent=2)
                        )
                    ]
                else:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "error",
                                "message": "Failed to retrieve customer after switch"
                            }, indent=2)
                        )
                    ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": f"Customer not found: {customer_identifier}"
                        }, indent=2)
                    )
                ]
        
        elif name == "list_customers":
            customers = customer_manager.list_customers()
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": customers,
                        "message": f"Retrieved {len(customers)} customers"
                    }, indent=2)
                )
            ]
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved relationship manager details"
                    }, indent=2)
                )
            ]
        
        elif name == "raise_servicerequest":
            transaction_id = arguments.get("transaction_id")
            servicerequest_reason = arguments.get("servicerequest_reason")
            
            if not transaction_id or not servicerequest_reason:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "Both transaction_id and servicerequest_reason are required"
                        }, indent=2)
                    )
                ]
            
            result = payment_service.raise_servicerequest(transaction_id, servicerequest_reason)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Service request raised successfully"
                    }, indent=2)
                )
            ]
        
        elif name == "verify_transaction_credit":
            transaction_id = arguments.get("transaction_id")
            
            if not transaction_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "transaction_id is required"
                        }, indent=2)
                    )
                ]
            
            result = payment_service.verify_transaction_credit(transaction_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Transaction verification completed"
                    }, indent=2)
                )            ]

        elif name == "get_nostro_accounts":
            currency = arguments.get("currency")
            export_reference = arguments.get("export_reference")
            result = payment_service.get_nostro_accounts(currency, export_reference)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved nostro accounts"
                    }, indent=2)
                )
            ]
        
        elif name == "get_treasury_pricing":
            customer_id = arguments.get("customer_id")
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_treasury_pricing(customer_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved treasury pricing"
                    }, indent=2)
                )
            ]
        
        elif name == "get_investment_proposals":
            customer_id = arguments.get("customer_id")
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_investment_proposals(customer_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved investment proposals"
                    }, indent=2)
                )
            ]
        
        elif name == "get_cash_forecasts":
            customer_id = arguments.get("customer_id")
            days = arguments.get("days", 30)
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_cash_forecasts(customer_id, days)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved cash forecasts"
                    }, indent=2)
                )
            ]
        
        elif name == "get_risk_limits":
            customer_id = arguments.get("customer_id")
            if customer_id:
                customer_manager.switch_customer(customer_id)
            
            result = payment_service.get_risk_limits(customer_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Retrieved risk limits"
                    }, indent=2)
                )
            ]
        
        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Unknown tool: {name}"
                    }, indent=2)
                )
            ]
    
    except Exception as e:
        print(f"Error in tool {name}: {str(e)}", file=sys.stderr)
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Error executing {name}: {str(e)}"
                }, indent=2)
            )
        ]

async def main():
    """Main function to run the MCP server"""
    print("Starting MCP server main loop...", file=sys.stderr)
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("MCP server connected successfully", file=sys.stderr)
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        print(f"Error in main: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("Running MCP server...", file=sys.stderr)
    asyncio.run(main())
