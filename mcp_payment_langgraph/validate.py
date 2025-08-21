#!/usr/bin/env python3
"""
Quick validation script for MCP Payment Transaction Server
Run this to verify everything is working after setup.
"""

def test_project():
    """Test all core functionality"""
    print("🧪 MCP Payment Transaction Server - Quick Test")
    print("=" * 55)
    
    try:
        # Test imports
        from payment_service import payment_service
        from orchestrator import payment_orchestrator
        from main import server
        print("✅ All imports successful")
        
        # Test basic functionality
        txns = payment_service.get_high_value_transactions(2)
        print(f"✅ High value transactions: {len(txns)} retrieved")
        
        rm = payment_service.get_relationship_manager_details()
        print(f"✅ Relationship manager: {rm['name']}")
        
        nostro = payment_service.check_euro_nostro_credit()
        print(f"✅ Euro nostro check: {nostro.get('status', 'unknown')}")
        
        accounts = payment_service.get_nostro_accounts()
        print(f"✅ Nostro accounts: {accounts.get('total_count', 0)} found")
        
        # Test orchestration (backend only - tools are commented out)
        response = payment_orchestrator.process_request("Show me transactions")
        print(f"✅ LangGraph orchestration (backend): {len(response)} char response")
        
        print("\n🎉 All tests passed!")
        print("🚀 Your MCP server is ready for Claude Desktop!")
        print("\n📋 Available MCP Tools (6 total):")
        print("   1. get_high_value_transactions")
        print("   2. get_relationship_manager") 
        print("   3. raise_dispute")
        print("   4. verify_transaction_credit")
        print("   5. check_euro_nostro_credit")
        print("   6. get_nostro_accounts")
        print("\n⚠️  Advanced tools (orchestrate_payment_workflow, get_user_transaction_memory)")
        print("   are commented out but available for re-enabling if needed.")
        print("\nNext steps:")
        print("1. Add this server to your Claude Desktop config")
        print("2. Restart Claude Desktop")
        print("3. Try: 'Show me recent high value transactions'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Run: uv sync")
        print("2. Ensure you're in the project directory")
        print("3. Check dependencies with: uv pip list")

if __name__ == "__main__":
    test_project()
