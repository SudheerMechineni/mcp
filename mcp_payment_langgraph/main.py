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
            name="get_high_value_transactions",
            description="Fetch the last 5 high value payment transactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to fetch (default: 5)",
                        "default": 5
                    }
                }
            }
        ),
        Tool(
            name="get_relationship_manager",
            description="Get relationship manager details for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_number": {
                        "type": "string",
                        "description": "Account number to find assigned relationship manager (optional)"
                    }
                }
            }
        ),
        Tool(
            name="raise_dispute",
            description="Raise a dispute for failed or pending payment transactions",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "ID of the transaction to dispute"
                    },
                    "dispute_reason": {
                        "type": "string",
                        "description": "Reason for raising the dispute"
                    }
                },
                "required": ["transaction_id", "dispute_reason"]
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
            name="orchestrate_payment_workflow",
            description="Orchestrate multiple payment operations based on natural language input using LangGraph",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_request": {
                        "type": "string",
                        "description": "Natural language description of what payment operations to perform"
                    }
                },
                "required": ["user_request"]
            }
        ),
        Tool(
            name="get_user_transaction_memory",
            description="Get the last 5 transactions from memory for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to retrieve transaction memory for (default: default_user)",
                        "default": "default_user"
                    }
                }
            }
        ),
        Tool(
            name="check_euro_nostro_credit",
            description="Check if Euro Nostro account is credited for export settlement",
            inputSchema={
                "type": "object",
                "properties": {
                    "export_reference": {
                        "type": "string",
                        "description": "Specific export reference to check (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_nostro_accounts",
            description="Get nostro accounts, optionally filtered by currency",
            inputSchema={
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "Currency filter (EUR, USD, GBP, etc.) - optional"
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
        if name == "get_high_value_transactions":
            limit = arguments.get("limit", 5)
            result = payment_service.get_high_value_transactions(limit)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": f"Retrieved {len(result)} high value transactions"
                    }, indent=2)
                )
            ]
        
        elif name == "get_relationship_manager":
            account_number = arguments.get("account_number")
            result = payment_service.get_relationship_manager_details(account_number)
            
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
        
        elif name == "raise_dispute":
            transaction_id = arguments.get("transaction_id")
            dispute_reason = arguments.get("dispute_reason")
            
            if not transaction_id or not dispute_reason:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "Both transaction_id and dispute_reason are required"
                        }, indent=2)
                    )
                ]
            
            result = payment_service.raise_dispute(transaction_id, dispute_reason)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Dispute raised successfully"
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
                )
            ]
        
        elif name == "orchestrate_payment_workflow":
            user_request = arguments.get("user_request")
            
            if not user_request:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "error",
                            "message": "user_request is required"
                        }, indent=2)
                    )
                ]
            
            # Use LangGraph orchestrator to process the request
            result = payment_orchestrator.process_request(user_request)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": {"response": result},
                        "message": "Payment workflow orchestrated successfully"
                    }, indent=2)
                )
            ]
        
        elif name == "get_user_transaction_memory":
            user_id = arguments.get("user_id", "default_user")
            result = payment_orchestrator.get_last_transactions_for_user(user_id)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": {
                            "user_id": user_id,
                            "last_transactions": result
                        },
                        "message": f"Retrieved {len(result)} transactions from memory for user {user_id}"
                    }, indent=2)
                )
            ]
        
        elif name == "check_euro_nostro_credit":
            export_reference = arguments.get("export_reference")
            result = payment_service.check_euro_nostro_credit(export_reference)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "data": result,
                        "message": "Euro Nostro credit check completed"
                    }, indent=2)
                )
            ]
        
        elif name == "get_nostro_accounts":
            currency = arguments.get("currency")
            result = payment_service.get_nostro_accounts(currency)
            
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
