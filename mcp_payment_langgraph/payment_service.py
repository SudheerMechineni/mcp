from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from models import (
    data_generator, 
    PaymentTransaction, 
    RelationshipManager, 
    DisputeRequest, 
    TransactionVerification,
    TransactionStatus
)

class PaymentAPIService:
    """Service class to handle all payment-related API operations"""
    
    def __init__(self):
        self.data_generator = data_generator
    
    def get_high_value_transactions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        API 1: Fetch last 5 high value payment transactions
        
        Args:
            limit: Number of transactions to fetch (default: 5)
            
        Returns:
            List of high value transactions
        """
        transactions = self.data_generator.get_high_value_transactions(limit)
        
        result = []
        for txn in transactions:
            result.append({
                "transaction_id": txn.transaction_id,
                "account_number": txn.account_number,
                "amount": txn.amount,
                "currency": txn.currency,
                "status": txn.status.value,
                "transaction_date": txn.transaction_date.isoformat(),
                "description": txn.description,
                "recipient_name": txn.recipient_name,
                "recipient_account": txn.recipient_account,
                "transaction_type": txn.transaction_type
            })
        
        return result
    
    def get_relationship_manager_details(self, account_number: Optional[str] = None) -> Dict[str, Any]:
        """
        API 2: Fetch relationship manager details
        
        Args:
            account_number: Account number to find assigned RM (optional)
            
        Returns:
            Relationship manager details
        """
        rm = self.data_generator.get_relationship_manager(account_number)
        
        return {
            "manager_id": rm.manager_id,
            "name": rm.name,
            "email": rm.email,
            "phone": rm.phone,
            "branch": rm.branch,
            "specialization": rm.specialization,
            "experience_years": rm.experience_years
        }
    
    def raise_dispute(self, transaction_id: str, dispute_reason: str) -> Dict[str, Any]:
        """
        API 3: Raise dispute for failed/pending payment transactions
        
        Args:
            transaction_id: ID of the transaction to dispute
            dispute_reason: Reason for the dispute
            
        Returns:
            Dispute details with assigned relationship manager
        """
        # First verify the transaction exists and is disputable
        transactions = self.data_generator.get_high_value_transactions(20)
        transaction = None
        
        for txn in transactions:
            if txn.transaction_id == transaction_id:
                transaction = txn
                break
        
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        if transaction.status not in [TransactionStatus.FAILED, TransactionStatus.PENDING]:
            raise ValueError(f"Cannot dispute transaction with status: {transaction.status}")
        
        # Create dispute
        dispute = self.data_generator.create_dispute(transaction_id, dispute_reason)
        
        # Get assigned relationship manager details
        rm = None
        for manager in self.data_generator._relationship_managers:
            if manager.manager_id == dispute.assigned_manager_id:
                rm = manager
                break
        
        return {
            "dispute_id": dispute.dispute_id,
            "transaction_id": dispute.transaction_id,
            "customer_account": dispute.customer_account,
            "dispute_reason": dispute.dispute_reason,
            "status": dispute.status.value,
            "created_date": dispute.created_date.isoformat(),
            "assigned_manager": {
                "manager_id": rm.manager_id,
                "name": rm.name,
                "email": rm.email,
                "phone": rm.phone,
                "branch": rm.branch
            } if rm else None
        }
    
    def verify_transaction_credit(self, transaction_id: str) -> Dict[str, Any]:
        """
        API 4: Verify whether transaction credited to account or not
        
        Args:
            transaction_id: ID of the transaction to verify
            
        Returns:
            Transaction verification details
        """
        verification = self.data_generator.verify_transaction(transaction_id)
        
        result = {
            "transaction_id": verification.transaction_id,
            "is_credited": verification.is_credited,
            "verification_status": verification.verification_status,
            "notes": verification.notes
        }
        
        if verification.credited_amount:
            result["credited_amount"] = verification.credited_amount
        
        if verification.credited_date:
            result["credited_date"] = verification.credited_date.isoformat()
        
        return result
    
    def check_euro_nostro_credit(self, export_reference: Optional[str] = None) -> Dict[str, Any]:
        """
        API 5: Check if Euro Nostro account is credited for export settlement
        
        Args:
            export_reference: Specific export reference to check (optional)
            
        Returns:
            Euro nostro account credit status and settlement details
        """
        result = self.data_generator.check_export_settlement_credit(export_reference, "EUR")
        return result
    
    def get_nostro_accounts(self, currency: Optional[str] = None) -> Dict[str, Any]:
        """
        API 6: Get nostro accounts, optionally filtered by currency
        
        Args:
            currency: Currency filter (EUR, USD, GBP, etc.)
            
        Returns:
            List of nostro accounts
        """
        accounts = self.data_generator.get_nostro_accounts(currency)
        
        result = []
        for acc in accounts:
            result.append({
                "account_id": acc.account_id,
                "currency": acc.currency.value,
                "account_type": acc.account_type.value,
                "correspondent_bank": acc.correspondent_bank,
                "correspondent_swift": acc.correspondent_swift,
                "balance": acc.balance,
                "available_balance": acc.available_balance,
                "last_updated": acc.last_updated.isoformat(),
                "account_status": acc.account_status
            })
        
        return {
            "accounts": result,
            "total_count": len(result),
            "currency_filter": currency or "all"
        }

# Global service instance
payment_service = PaymentAPIService()
