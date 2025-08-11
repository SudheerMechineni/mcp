from typing import Any, Dict, List, Optional, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from payment_service import payment_service
import json
from collections import defaultdict, deque
from langgraph.graph import StateGraph, END

class PaymentGraphState(TypedDict):
    """State for the payment processing graph"""
    messages: Sequence[BaseMessage]
    user_input: str
    action_needed: List[str]  # List of actions: ['get_transactions', 'raise_dispute', 'get_rm', 'verify_transaction', 'check_nostro', 'get_nostro_accounts']
    transactions: Optional[List[Dict[str, Any]]]
    relationship_manager: Optional[Dict[str, Any]]
    dispute_details: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    nostro_credit_result: Optional[Dict[str, Any]]
    nostro_accounts: Optional[Dict[str, Any]]
    final_response: str

class PaymentOrchestrator:
    """LangGraph orchestrator for payment operations"""
    
    def __init__(self):
        self.service = payment_service
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()
        # Memory: user_id -> deque of last 5 transactions
        self.user_transaction_memory = defaultdict(lambda: deque(maxlen=5))
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(PaymentGraphState)
        
        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("get_transactions", self._get_transactions)
        workflow.add_node("get_relationship_manager", self._get_relationship_manager)
        workflow.add_node("raise_dispute", self._raise_dispute)
        workflow.add_node("verify_transaction", self._verify_transaction)
        workflow.add_node("check_nostro_credit", self._check_nostro_credit)
        workflow.add_node("get_nostro_accounts", self._get_nostro_accounts)
        workflow.add_node("format_response", self._format_response)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        # Add edges with conditional logic
        workflow.add_conditional_edges(
            "analyze_request",
            self._route_actions,
            {
                "get_transactions": "get_transactions",
                "get_rm": "get_relationship_manager",
                "verify_transaction": "verify_transaction",
                "check_nostro_credit": "check_nostro_credit",
                "get_nostro_accounts": "get_nostro_accounts",
                "format_response": "format_response"
            }
        )
        
        # Transaction flow
        workflow.add_conditional_edges(
            "get_transactions",
            self._check_next_action,
            {
                "raise_dispute": "get_relationship_manager",
                "format_response": "format_response"
            }
        )
        
        # RM flow (needed for disputes)
        workflow.add_conditional_edges(
            "get_relationship_manager",
            self._check_dispute_needed,
            {
                "raise_dispute": "raise_dispute",
                "format_response": "format_response"
            }
        )
        
        # Dispute and verification flow
        workflow.add_edge("raise_dispute", "format_response")
        workflow.add_edge("verify_transaction", "format_response")
        workflow.add_edge("check_nostro_credit", "format_response")
        workflow.add_edge("get_nostro_accounts", "format_response")
        workflow.add_edge("format_response", END)
        return workflow
    
    def _analyze_request(self, state: PaymentGraphState) -> PaymentGraphState:
        """Analyze user request to determine required actions"""
        user_input = state["user_input"].lower()
        actions = []
        
        # Determine what actions are needed based on user input
        if any(keyword in user_input for keyword in ["transaction", "payment", "high value", "last 5"]):
            actions.append("get_transactions")
        
        if any(keyword in user_input for keyword in ["dispute", "raise dispute", "failed", "pending"]):
            actions.append("raise_dispute")
        
        if any(keyword in user_input for keyword in ["relationship manager", "manager", "rm"]):
            actions.append("get_rm")
        
        if any(keyword in user_input for keyword in ["verify", "credited", "credit", "check transaction"]):
            actions.append("verify_transaction")
        
        # Euro Nostro account queries
        if any(keyword in user_input for keyword in ["nostro", "euro nostro", "export settlement", "euro account", "euro credit"]):
            actions.append("check_nostro")
        
        if any(keyword in user_input for keyword in ["nostro accounts", "correspondent accounts", "nostro list"]):
            actions.append("get_nostro_accounts")
        
        # If dispute is needed, we also need RM
        if "raise_dispute" in actions and "get_rm" not in actions:
            actions.append("get_rm")
        
        state["action_needed"] = actions
        return state
    
    def _route_actions(self, state: PaymentGraphState) -> str:
        """Route to the first action needed"""
        actions = state["action_needed"]
        
        if "check_nostro" in actions:
            return "check_nostro_credit"
        elif "get_nostro_accounts" in actions:
            return "get_nostro_accounts"
        elif "get_transactions" in actions:
            return "get_transactions"
        elif "verify_transaction" in actions:
            return "verify_transaction"
        elif "get_rm" in actions:
            return "get_rm"
        else:
            return "format_response"
    
    def _check_next_action(self, state: PaymentGraphState) -> str:
        """Check what to do after getting transactions"""
        if "raise_dispute" in state["action_needed"]:
            return "raise_dispute"
        return "format_response"
    
    def _check_dispute_needed(self, state: PaymentGraphState) -> str:
        """Check if dispute needs to be raised after getting RM"""
        if "raise_dispute" in state["action_needed"]:
            return "raise_dispute"
        return "format_response"
    
    def _get_user_id(self, state: PaymentGraphState) -> str:
        user_input = state.get("user_input", "")
        for word in user_input.split():
            if word.startswith("ACC") or word.startswith("account_"):
                return word
        return "default_user"

    def _get_transactions(self, state: PaymentGraphState) -> PaymentGraphState:
        """Get high value transactions and update memory"""
        try:
            transactions = self.service.get_high_value_transactions(5)
            state["transactions"] = transactions
            # --- Memory: store for user ---
            user_id = self._get_user_id(state)
            for txn in transactions:
                self.user_transaction_memory[user_id].appendleft(txn)
        except Exception as e:
            state["transactions"] = []
            print(f"Error getting transactions: {e}")
        return state
    
    def get_last_transactions_for_user(self, user_id: str) -> list:
        """Return last 5 transactions for a user from memory"""
        return list(self.user_transaction_memory[user_id])

    def _get_relationship_manager(self, state: PaymentGraphState) -> PaymentGraphState:
        """Get relationship manager details"""
        try:
            rm = self.service.get_relationship_manager_details()
            state["relationship_manager"] = rm
        except Exception as e:
            state["relationship_manager"] = None
            print(f"Error getting relationship manager: {e}")
        
        return state
    
    def _raise_dispute(self, state: PaymentGraphState) -> PaymentGraphState:
        """Raise dispute for a transaction"""
        try:
            transactions = state.get("transactions", [])
            if transactions:
                # Find a failed or pending transaction to dispute
                disputable_txn = None
                for txn in transactions:
                    if txn["status"] in ["failed", "pending"]:
                        disputable_txn = txn
                        break
                
                if disputable_txn:
                    dispute = self.service.raise_dispute(
                        disputable_txn["transaction_id"],
                        "Transaction failed to process within expected timeframe"
                    )
                    state["dispute_details"] = dispute
                else:
                    state["dispute_details"] = {"error": "No disputable transactions found"}
            else:
                state["dispute_details"] = {"error": "No transactions available to dispute"}
                
        except Exception as e:
            state["dispute_details"] = {"error": f"Error raising dispute: {e}"}
        
        return state
    
    def _verify_transaction(self, state: PaymentGraphState) -> PaymentGraphState:
        """Verify transaction credit status"""
        try:
            # For demo purposes, use a transaction from the list or create a sample ID
            transactions = state.get("transactions", [])
            transaction_id = None
            
            if transactions:
                transaction_id = transactions[0]["transaction_id"]
            else:
                # Get a transaction ID from the service for verification
                sample_transactions = self.service.get_high_value_transactions(1)
                if sample_transactions:
                    transaction_id = sample_transactions[0]["transaction_id"]
            
            if transaction_id:
                verification = self.service.verify_transaction_credit(transaction_id)
                state["verification_result"] = verification
            else:
                state["verification_result"] = {"error": "No transaction ID available for verification"}
                
        except Exception as e:
            state["verification_result"] = {"error": f"Error verifying transaction: {e}"}
        
        return state
    
    def _check_nostro_credit(self, state: PaymentGraphState) -> PaymentGraphState:
        """Check Euro nostro account credit for export settlement"""
        try:
            # Extract export reference if mentioned in user input
            user_input = state.get("user_input", "").lower()
            export_reference = None
            
            # Look for export reference patterns
            words = user_input.split()
            for i, word in enumerate(words):
                if word in ["export", "settlement", "reference"] and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word.upper().startswith("EXP") or len(next_word) > 8:
                        export_reference = next_word
                        break
            
            nostro_result = self.service.check_euro_nostro_credit(export_reference)
            state["nostro_credit_result"] = nostro_result
            
        except Exception as e:
            state["nostro_credit_result"] = {"error": f"Error checking Euro nostro credit: {e}"}
        
        return state
    
    def _get_nostro_accounts(self, state: PaymentGraphState) -> PaymentGraphState:
        """Get nostro accounts, optionally filtered by currency"""
        try:
            # Extract currency if mentioned in user input
            user_input = state.get("user_input", "").lower()
            currency = None
            
            # Check for currency mentions
            currencies = ["eur", "euro", "usd", "dollar", "gbp", "pound", "jpy", "yen", "chf", "franc"]
            for curr in currencies:
                if curr in user_input:
                    if curr in ["eur", "euro"]:
                        currency = "EUR"
                    elif curr in ["usd", "dollar"]:
                        currency = "USD"
                    elif curr in ["gbp", "pound"]:
                        currency = "GBP"
                    elif curr in ["jpy", "yen"]:
                        currency = "JPY"
                    elif curr in ["chf", "franc"]:
                        currency = "CHF"
                    break
            
            nostro_accounts = self.service.get_nostro_accounts(currency)
            state["nostro_accounts"] = nostro_accounts
            
        except Exception as e:
            state["nostro_accounts"] = {"error": f"Error getting nostro accounts: {e}"}
        
        return state

    def _format_response(self, state: PaymentGraphState) -> PaymentGraphState:
        """Format the final response"""
        response_parts = []
        txns = state.get("transactions") or []
        if txns:
            response_parts.append("**High Value Transactions (Last 5):**")
            for i, txn in enumerate(txns, 1):
                response_parts.append(
                    f"{i}. Transaction ID: {txn['transaction_id']}\n"
                    f"   Amount: {txn['currency']} {txn['amount']:,.2f}\n"
                    f"   Status: {txn['status']}\n"
                    f"   Date: {txn['transaction_date']}\n"
                    f"   Recipient: {txn['recipient_name']}\n"
                )
        
        rm = state.get("relationship_manager")
        if rm:
            response_parts.append(
                f"**Relationship Manager Details:**\n"
                f"Name: {rm['name']}\n"
                f"Email: {rm['email']}\n"
                f"Phone: {rm['phone']}\n"
                f"Branch: {rm['branch']}\n"
                f"Specialization: {', '.join(rm['specialization'])}\n"
                f"Experience: {rm['experience_years']} years"
            )
        
        dispute = state.get("dispute_details")
        if dispute:
            if isinstance(dispute, dict) and "error" in dispute:
                response_parts.append(f"**Dispute Error:** {dispute['error']}")
            else:
                response_parts.append(
                    f"**Dispute Raised Successfully:**\n"
                    f"Dispute ID: {dispute.get('dispute_id','')}\n"
                    f"Transaction ID: {dispute.get('transaction_id','')}\n"
                    f"Status: {dispute.get('status','')}\n"
                    f"Assigned Manager: {dispute.get('assigned_manager',{}).get('name','N/A')}\n"
                    f"Manager Contact: {dispute.get('assigned_manager',{}).get('email','N/A')}"
                )
        
        verification = state.get("verification_result")
        if verification:
            if isinstance(verification, dict) and "error" in verification:
                response_parts.append(f"**Verification Error:** {verification['error']}")
            else:
                response_parts.append(
                    f"**Transaction Verification:**\n"
                    f"Transaction ID: {verification.get('transaction_id','')}\n"
                    f"Is Credited: {'Yes' if verification.get('is_credited') else 'No'}\n"
                    f"Status: {verification.get('verification_status','')}\n"
                    f"Notes: {verification.get('notes','')}"
                )
                if verification.get("credited_amount"):
                    response_parts.append(f"Credited Amount: USD {verification['credited_amount']:,.2f}")
                if verification.get("credited_date"):
                    response_parts.append(f"Credited Date: {verification['credited_date']}")
        
        # Euro Nostro credit check results
        nostro_credit = state.get("nostro_credit_result")
        if nostro_credit:
            if isinstance(nostro_credit, dict) and "error" in nostro_credit:
                response_parts.append(f"**Euro Nostro Error:** {nostro_credit['error']}")
            else:
                response_parts.append(f"**Euro Nostro Account Credit Status:**")
                response_parts.append(f"Status: {nostro_credit.get('status', 'unknown')}")
                response_parts.append(f"Message: {nostro_credit.get('message', '')}")
                
                if nostro_credit.get("nostro_account"):
                    acc = nostro_credit["nostro_account"]
                    response_parts.append(
                        f"**Account Details:**\n"
                        f"Account ID: {acc.get('account_id', '')}\n"
                        f"Currency: {acc.get('currency', '')}\n"
                        f"Correspondent Bank: {acc.get('correspondent_bank', '')}\n"
                        f"SWIFT: {acc.get('correspondent_swift', '')}\n"
                        f"Current Balance: {acc.get('currency', 'EUR')} {acc.get('current_balance', 0):,.2f}\n"
                        f"Available Balance: {acc.get('currency', 'EUR')} {acc.get('available_balance', 0):,.2f}"
                    )
                
                if nostro_credit.get("settlements"):
                    response_parts.append("**Export Settlements:**")
                    for i, settlement in enumerate(nostro_credit["settlements"], 1):
                        status_indicator = "✅" if settlement.get("is_credited") else "⏳"
                        response_parts.append(
                            f"{i}. {status_indicator} Settlement ID: {settlement.get('settlement_id', '')}\n"
                            f"   Export Reference: {settlement.get('export_reference', '')}\n"
                            f"   Amount: {settlement.get('currency', 'EUR')} {settlement.get('amount', 0):,.2f}\n"
                            f"   Counterparty: {settlement.get('counterparty', '')}\n"
                            f"   Status: {settlement.get('status', '')}\n"
                            f"   Settlement Date: {settlement.get('settlement_date', '')[:10] if settlement.get('settlement_date') else ''}"
                        )
                        if settlement.get("actual_credit_date"):
                            response_parts.append(f"   Credited Date: {settlement['actual_credit_date'][:10]}")
                
                if nostro_credit.get("summary"):
                    summary = nostro_credit["summary"]
                    response_parts.append(
                        f"**Summary:**\n"
                        f"Total Settlements: {summary.get('total_settlements', 0)}\n"
                        f"Credited: {summary.get('credited_count', 0)} (EUR {summary.get('total_credited_amount', 0):,.2f})\n"
                        f"Pending: {summary.get('pending_count', 0)} (EUR {summary.get('total_pending_amount', 0):,.2f})"
                    )
        
        # Nostro accounts results
        nostro_accounts = state.get("nostro_accounts")
        if nostro_accounts:
            if isinstance(nostro_accounts, dict) and "error" in nostro_accounts:
                response_parts.append(f"**Nostro Accounts Error:** {nostro_accounts['error']}")
            else:
                response_parts.append(f"**Nostro Accounts ({nostro_accounts.get('currency_filter', 'all')} filter):**")
                response_parts.append(f"Total Count: {nostro_accounts.get('total_count', 0)}")
                
                for i, acc in enumerate(nostro_accounts.get("accounts", []), 1):
                    response_parts.append(
                        f"{i}. Account ID: {acc.get('account_id', '')}\n"
                        f"   Currency: {acc.get('currency', '')}\n"
                        f"   Type: {acc.get('account_type', '')}\n"
                        f"   Correspondent: {acc.get('correspondent_bank', '')}\n"
                        f"   SWIFT: {acc.get('correspondent_swift', '')}\n"
                        f"   Balance: {acc.get('currency', '')} {acc.get('balance', 0):,.2f}\n"
                        f"   Status: {acc.get('account_status', '')}"
                    )
        
        if not response_parts:
            response_parts.append("No actions were performed. Please specify what you'd like to do.")
        
        state["final_response"] = "\n\n".join(response_parts)
        return state
    
    def process_request(self, user_input: str) -> str:
        """Process a user request through the graph"""
        initial_state = PaymentGraphState(
            messages=[HumanMessage(content=user_input)],
            user_input=user_input,
            action_needed=[],
            transactions=None,
            relationship_manager=None,
            dispute_details=None,
            verification_result=None,
            nostro_credit_result=None,
            nostro_accounts=None,
            final_response=""
        )
        
        # Run the graph
        result = self.compiled_graph.invoke(initial_state)
        return result["final_response"]

# Global orchestrator instance
payment_orchestrator = PaymentOrchestrator()
