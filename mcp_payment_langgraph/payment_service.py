from typing import List, Dict, Any, Optional
import json
import time
import sys
from datetime import datetime, timedelta
from database import payment_db
from customer_manager import customer_manager
from logger import request_logger, log_execution_time

class PaymentAPIService:
    """Service class to handle all payment-related API operations with database integration"""
    
    def __init__(self):
        pass  # No more mock data generator needed
    
    @log_execution_time
    def get_transactions(
        self, 
        limit: int = 5, 
        days_filter: int = 30,
        min_amount: float = 100000.0,
        customer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch high value payment transactions with enhanced filtering
        
        Args:
            limit: Number of transactions to fetch (default: 5)
            days_filter: Number of days to look back (default: 30 for "recent")
            min_amount: Minimum amount for high value filter (default: 100K)
            customer_id: Optional customer ID override
            
        Returns:
            List of high value transactions
        """
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Calculate date filter
                cutoff_date = datetime.now() - timedelta(days=days_filter)
                
                cursor.execute("""
                    SELECT transaction_id, customer_id, account_number, amount, currency, 
                           status, transaction_date, description, recipient_name, 
                           recipient_account, transaction_type
                    FROM high_value_transactions 
                    WHERE customer_id = ? 
                      AND amount >= ?
                      AND transaction_date >= ?
                    ORDER BY transaction_date DESC 
                    LIMIT ?
                """, (customer_id, min_amount, cutoff_date.isoformat(), limit))
                
                transactions = []
                for row in cursor.fetchall():
                    transactions.append({
                        "transaction_id": row['transaction_id'],
                        "customer_id": row['customer_id'],
                        "account_number": row['account_number'],
                        "amount": row['amount'],
                        "currency": row['currency'],
                        "status": row['status'],
                        "transaction_date": row['transaction_date'],
                        "description": row['description'],
                        "recipient_name": row['recipient_name'],
                        "recipient_account": row['recipient_account'],
                        "transaction_type": row['transaction_type']
                    })
                
                # Log request and response
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_transactions",
                    {"customer_id": customer_id, "limit": limit, "days_filter": days_filter, "min_amount": min_amount},
                    {"transaction_count": len(transactions), "transactions": transactions},
                    execution_time
                )
                
                return transactions
                
        except Exception as e:
            request_logger.log_error("get_transactions", str(e), {"customer_id": customer_id, "limit": limit})
            raise
    
    @log_execution_time
    def get_relationship_manager_details(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get relationship manager details for current customer
        
        Args:
            customer_id: Optional customer ID override
            
        Returns:
            Relationship manager details
        """
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT rm.manager_id, rm.name, rm.email, rm.phone, rm.specialization, 
                           rm.experience_years, rm.branch
                    FROM relationship_managers rm
                    INNER JOIN customers c ON c.relationship_manager_id = rm.manager_id
                    WHERE c.customer_id = ?
                """, (customer_id,))
                
                rm = cursor.fetchone()
                if not rm:
                    raise ValueError(f"No relationship manager found for customer {customer_id}")
                
                result = {
                    "manager_id": rm['manager_id'],
                    "customer_id": customer_id,
                    "name": rm['name'],
                    "email": rm['email'],
                    "phone": rm['phone'],
                    "specialization": rm['specialization'],
                    "experience_years": rm['experience_years'],
                    "department": rm['branch'] if 'branch' in rm.keys() else 'Not specified',
                    "availability_hours": 'Standard business hours'
                }
                
                # Log request and response
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_relationship_manager_details",
                    {"customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_relationship_manager_details", str(e), {"customer_id": customer_id})
            raise
    
    @log_execution_time
    def raise_servicerequest(self, transaction_id: str, servicerequest_reason: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Raise a service request for a transaction
        
        Args:
            transaction_id: ID of the transaction for service request
            servicerequest_reason: Reason for the service request
            customer_id: Optional customer ID override
            
        Returns:
            Service request details
        """
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if transaction exists
                cursor.execute("""
                    SELECT transaction_id, amount, currency, status, account_number
                    FROM high_value_transactions 
                    WHERE transaction_id = ? AND customer_id = ?
                """, (transaction_id, customer_id))
                
                transaction = cursor.fetchone()
                if not transaction:
                    raise ValueError(f"Transaction {transaction_id} not found for customer {customer_id}")
                
                # Get customer account from transaction
                customer_account = transaction['account_number'] if 'account_number' in transaction.keys() else None
                if not customer_account:
                    raise ValueError(f"Account number not found for transaction {transaction_id}")
                
                # Create service request
                servicerequest_id = f"SR_{int(time.time() * 1000)}"
                
                cursor.execute("""
                    INSERT INTO disputes 
                    (dispute_id, transaction_id, customer_id, customer_account, dispute_reason, status, 
                     created_date, resolution_date, assigned_to, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (servicerequest_id, transaction_id, customer_id, customer_account, servicerequest_reason, 'open',
                     datetime.now().isoformat(), None, 'Support Team', 
                     f'Service request created for transaction {transaction_id}') )
                
                conn.commit()
                
                result = {
                    "servicerequest_id": servicerequest_id,
                    "transaction_id": transaction_id,
                    "customer_id": customer_id,
                    "customer_account": customer_account,
                    "servicerequest_reason": servicerequest_reason,
                    "status": "open",
                    "created_date": datetime.now().isoformat(),
                    "assigned_to": "Support Team"
                }
                
                # Log request and response
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "raise_servicerequest",
                    {"transaction_id": transaction_id, "servicerequest_reason": servicerequest_reason, "customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("raise_servicerequest", str(e), {"transaction_id": transaction_id, "customer_id": customer_id})
            raise
    
    @log_execution_time
    def verify_transaction_credit(self, transaction_id: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify if a transaction has been credited
        
        Args:
            transaction_id: ID of the transaction to verify
            customer_id: Optional customer ID override
            
        Returns:
            Verification details
        """
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT verification_id, transaction_id, is_credited, credited_amount,
                           credited_date, verification_status, notes
                    FROM transaction_verifications 
                    WHERE transaction_id = ? AND customer_id = ?
                """, (transaction_id, customer_id))
                
                verification = cursor.fetchone()
                
                if verification:
                    result = {
                        "transaction_id": verification['transaction_id'],
                        "is_credited": bool(verification['is_credited']),
                        "verification_status": verification['verification_status'],
                        "notes": verification['notes']
                    }
                    
                    if verification['credited_amount']:
                        result["credited_amount"] = verification['credited_amount']
                    
                    if verification['credited_date']:
                        result["credited_date"] = verification['credited_date']
                else:
                    # Create new verification if doesn't exist
                    cursor.execute("""
                        SELECT transaction_id, status, amount, currency
                        FROM high_value_transactions 
                        WHERE transaction_id = ? AND customer_id = ?
                    """, (transaction_id, customer_id))
                    
                    transaction = cursor.fetchone()
                    if not transaction:
                        raise ValueError(f"Transaction {transaction_id} not found for customer {customer_id}")
                    
                    is_credited = transaction['status'] == 'completed'
                    verification_id = f"VER_{int(time.time() * 1000)}"
                    
                    cursor.execute("""
                        INSERT INTO transaction_verifications 
                        (verification_id, transaction_id, customer_id, is_credited, credited_amount,
                         credited_date, verification_status, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (verification_id, transaction_id, customer_id, is_credited,
                         transaction['amount'] if is_credited else None,
                         datetime.now().isoformat() if is_credited else None,
                         'verified' if is_credited else 'pending',
                         'Auto-generated verification record'))
                    
                    conn.commit()
                    
                    result = {
                        "transaction_id": transaction_id,
                        "is_credited": is_credited,
                        "verification_status": 'verified' if is_credited else 'pending',
                        "notes": 'Auto-generated verification record'
                    }
                    
                    if is_credited:
                        result["credited_amount"] = transaction['amount']
                        result["credited_date"] = datetime.now().isoformat()
                
                # Log request and response
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "verify_transaction_credit",
                    {"transaction_id": transaction_id, "customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("verify_transaction_credit", str(e), {"transaction_id": transaction_id, "customer_id": customer_id})
            raise
    
    @log_execution_time
    def get_nostro_accounts(self, currency: Optional[str] = None, export_reference: Optional[str] = None) -> Dict[str, Any]:
        """
        Get nostro accounts, optionally filtered by currency. For EUR, includes settlement details.
        
        Args:
            currency: Currency filter (EUR, USD, GBP, etc.)
            export_reference: For EUR currency, specific export reference to check settlements
            
        Returns:
            List of nostro accounts with settlement details for EUR
        """
        start_time = time.time()
        
        # Get current customer context
        current_customer = customer_manager.get_current_customer()
        if not current_customer:
            raise ValueError("No customer context available")
        customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                if (currency):
                    cursor.execute("""
                        SELECT account_id, currency, account_type, correspondent_bank,
                               correspondent_swift, balance, available_balance, 
                               last_updated, account_status
                        FROM nostro_accounts 
                        WHERE currency = ?
                        ORDER BY balance DESC
                    """, (currency,))
                else:
                    cursor.execute("""
                        SELECT account_id, currency, account_type, correspondent_bank,
                               correspondent_swift, balance, available_balance, 
                               last_updated, account_status
                        FROM nostro_accounts 
                        ORDER BY currency, balance DESC
                    """)
                
                accounts = []
                for row in cursor.fetchall():
                    account_data = {
                        "account_id": row['account_id'],
                        "currency": row['currency'],
                        "account_type": row['account_type'],
                        "correspondent_bank": row['correspondent_bank'],
                        "correspondent_swift": row['correspondent_swift'],
                        "balance": row['balance'],
                        "available_balance": row['available_balance'],
                        "last_updated": row['last_updated'],
                        "account_status": row['account_status']
                    }
                    
                    # Add settlement details for EUR accounts
                    if row['currency'] == 'EUR':
                        # Get settlements for this customer
                        settlement_query = """
                            SELECT settlement_id, amount, export_reference, counterparty, 
                                   settlement_date, actual_credit_date, status
                            FROM euro_nostro_settlements 
                            WHERE customer_id = ?
                        """
                        settlement_params = [customer_id]
                        
                        if export_reference:
                            settlement_query += " AND export_reference = ?"
                            settlement_params.append(export_reference)
                        
                        settlement_query += " ORDER BY settlement_date DESC LIMIT 10"
                        
                        cursor.execute(settlement_query, settlement_params)
                        settlements = cursor.fetchall()
                        
                        # Process settlements
                        settlements_data = []
                        total_credited = 0
                        total_pending = 0
                        credited_count = 0
                        pending_count = 0
                        
                        for settlement in settlements:
                            settlement_data = {
                                "settlement_id": settlement['settlement_id'],
                                "amount": settlement['amount'],
                                "export_reference": settlement['export_reference'],
                                "counterparty": settlement['counterparty'],
                                "settlement_date": settlement['settlement_date'],
                                "actual_credit_date": settlement['actual_credit_date'],
                                "status": settlement['status']
                            }
                            settlements_data.append(settlement_data)
                            
                            if settlement['status'] == 'credited':
                                total_credited += settlement['amount']
                                credited_count += 1
                            elif settlement['status'] == 'pending':
                                total_pending += settlement['amount']
                                pending_count += 1
                        
                        account_data['settlements'] = {
                            "settlements": settlements_data,
                            "summary": {
                                "total_settlements": len(settlements_data),
                                "credited_count": credited_count,
                                "pending_count": pending_count,
                                "total_credited_amount": total_credited,
                                "total_pending_amount": total_pending
                            }
                        }
                        
                        if settlements_data:
                            account_data['settlement_status'] = "settlements_found"
                        elif export_reference:
                            account_data['settlement_status'] = "no_settlements_for_reference"
                        else:
                            account_data['settlement_status'] = "no_recent_settlements"
                    
                    accounts.append(account_data)
                
                result = {
                    "accounts": accounts,
                    "total_count": len(accounts),
                    "currency_filter": currency or "all"
                }
                
                # Log request and response
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_nostro_accounts",
                    {"currency": currency, "export_reference": export_reference},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_nostro_accounts", str(e), {"currency": currency})
            raise
    
    # Treasury and Investment APIs for Personalized Journey
    
    @log_execution_time
    def get_treasury_pricing(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get treasury FX pricing for customer"""
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT pricing_id, currency_pair, rate, margin, valid_until, pricing_tier
                    FROM treasury_pricing 
                    WHERE customer_id = ? AND valid_until > CURRENT_TIMESTAMP
                    ORDER BY currency_pair
                """, (customer_id,))
                
                pricing_data = []
                for row in cursor.fetchall():
                    pricing_data.append({
                        "pricing_id": row['pricing_id'],
                        "currency_pair": row['currency_pair'],
                        "rate": row['rate'],
                        "margin": row['margin'],
                        "valid_until": row['valid_until'],
                        "pricing_tier": row['pricing_tier']
                    })
                
                result = {
                    "customer_id": customer_id,
                    "pricing_data": pricing_data,
                    "total_pairs": len(pricing_data)
                }
                
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_treasury_pricing",
                    {"customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_treasury_pricing", str(e), {"customer_id": customer_id})
            raise
    
    @log_execution_time 
    def get_investment_proposals(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get investment proposals for customer"""
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT proposal_id, product_type, amount, currency, expected_return,
                           risk_level, proposal_date, status, maturity_date
                    FROM investment_proposals 
                    WHERE customer_id = ?
                    ORDER BY proposal_date DESC
                """, (customer_id,))
                
                proposals = []
                for row in cursor.fetchall():
                    proposals.append({
                        "proposal_id": row['proposal_id'],
                        "product_type": row['product_type'],
                        "amount": row['amount'],
                        "currency": row['currency'],
                        "expected_return": row['expected_return'],
                        "risk_level": row['risk_level'],
                        "proposal_date": row['proposal_date'],
                        "status": row['status'],
                        "maturity_date": row['maturity_date']
                    })
                
                result = {
                    "customer_id": customer_id,
                    "proposals": proposals,
                    "total_proposals": len(proposals)
                }
                
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_investment_proposals",
                    {"customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_investment_proposals", str(e), {"customer_id": customer_id})
            raise
            request_logger.log_error("get_investment_proposals", str(e), {"customer_id": customer_id})
            raise
    
    @log_execution_time
    def get_cash_forecasts(self, customer_id: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """Get cash forecasts for customer"""
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT forecast_id, forecast_date, currency, opening_balance, 
                           projected_inflows, projected_outflows, closing_balance, confidence_level
                    FROM cash_forecasts 
                    WHERE customer_id = ?
                    ORDER BY forecast_date
                """, (customer_id,))
                
                forecasts = []
                for row in cursor.fetchall():
                    forecasts.append({
                        "forecast_id": row['forecast_id'],
                        "forecast_date": row['forecast_date'],
                        "currency": row['currency'],
                        "opening_balance": row['opening_balance'],
                        "projected_inflows": row['projected_inflows'],
                        "projected_outflows": row['projected_outflows'],
                        "closing_balance": row['closing_balance'],
                        "confidence_level": row['confidence_level']
                    })
                
                result = {
                    "customer_id": customer_id,
                    "forecasts": forecasts,
                    "total_forecasts": len(forecasts),
                    "forecast_period_days": days
                }
                
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_cash_forecasts",
                    {"customer_id": customer_id, "days": days},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_cash_forecasts", str(e), {"customer_id": customer_id})
            raise
    
    @log_execution_time
    def get_risk_limits(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get risk limits for customer"""
        start_time = time.time()
        
        # Get current customer context
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            if not current_customer:
                raise ValueError("No customer context available")
            customer_id = current_customer['customer_id']
        
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT limit_id, limit_type, limit_amount, currency, utilization, utilization_percentage
                    FROM risk_limits 
                    WHERE customer_id = ?
                    ORDER BY limit_type
                """, (customer_id,))
                
                limits = []
                for row in cursor.fetchall():
                    limits.append({
                        "limit_id": row['limit_id'],
                        "limit_type": row['limit_type'],
                        "limit_amount": row['limit_amount'],
                        "currency": row['currency'],
                        "utilization": row['utilization'],
                        "utilization_percentage": row['utilization_percentage'],
                        "available_limit": row['limit_amount'] - row['utilization'],
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "status": "active"
                    })
                
                result = {
                    "customer_id": customer_id,
                    "limits": limits,
                    "total_limits": len(limits)
                }
                
                execution_time = int((time.time() - start_time) * 1000)
                request_logger.log_request_response(
                    "get_risk_limits",
                    {"customer_id": customer_id},
                    result,
                    execution_time
                )
                
                return result
                
        except Exception as e:
            request_logger.log_error("get_risk_limits", str(e), {"customer_id": customer_id})
            raise

# Create global service instance
payment_service = PaymentAPIService()
