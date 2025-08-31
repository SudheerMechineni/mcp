from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import random
from faker import Faker
from pydantic import BaseModel, Field

fake = Faker()

class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    DISPUTED = "disputed"

class ServiceRequestStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class PaymentTransaction(BaseModel):
    transaction_id: str
    account_number: str
    amount: float
    currency: str = "USD"
    status: TransactionStatus
    transaction_date: datetime
    description: str
    recipient_name: str
    recipient_account: str
    transaction_type: str

class RelationshipManager(BaseModel):
    manager_id: str
    name: str
    email: str
    phone: str
    branch: str
    specialization: List[str]
    experience_years: int

class ServiceRequest(BaseModel):
    service_request_id: str
    transaction_id: str
    customer_account: str
    sr_reason: str
    status: ServiceRequestStatus
    created_date: datetime
    assigned_manager_id: str
    resolution_notes: Optional[str] = None

class TransactionVerification(BaseModel):
    transaction_id: str
    is_credited: bool
    credited_amount: Optional[float] = None
    credited_date: Optional[datetime] = None
    verification_status: str
    notes: str

class AccountType(str, Enum):
    NOSTRO = "nostro"
    VOSTRO = "vostro"
    REGULAR = "regular"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"

class SettlementType(str, Enum):
    EXPORT = "export"
    IMPORT = "import"
    TRADE_FINANCE = "trade_finance"
    FX_SETTLEMENT = "fx_settlement"

class NostroAccount(BaseModel):
    account_id: str
    currency: Currency
    account_type: AccountType
    correspondent_bank: str
    correspondent_swift: str
    balance: float
    available_balance: float
    last_updated: datetime
    account_status: str = "active"

class ExportSettlement(BaseModel):
    settlement_id: str
    nostro_account_id: str
    amount: float
    currency: Currency
    settlement_type: SettlementType
    export_reference: str
    counterparty: str
    settlement_date: datetime
    expected_credit_date: datetime
    actual_credit_date: Optional[datetime] = None
    status: TransactionStatus
    swift_message_ref: Optional[str] = None

class MockDataGenerator:
    def __init__(self):
        self.fake = Faker()
        self._transactions = []
        self._relationship_managers = []
        self._service_requests = []
        self._nostro_accounts = []
        self._export_settlements = []
        self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate mock data for testing"""
        # Generate transactions
        for i in range(20):
            transaction = PaymentTransaction(
                transaction_id=f"TXN{self.fake.unique.random_number(digits=10)}",
                account_number=self.fake.unique.iban(),
                amount=round(random.uniform(50000, 500000), 2),
                status=random.choice(list(TransactionStatus)),
                transaction_date=self.fake.date_time_between(start_date='-30d', end_date='now'),
                description=self.fake.sentence(nb_words=6),
                recipient_name=self.fake.name(),
                recipient_account=self.fake.iban(),
                transaction_type=random.choice(["wire_transfer", "ach", "international", "domestic"])
            )
            self._transactions.append(transaction)
        
        # Sort by date (newest first)
        self._transactions.sort(key=lambda x: x.transaction_date, reverse=True)
        
        # Generate relationship managers
        specializations = [
            ["high_net_worth", "investment_banking"],
            ["corporate_banking", "treasury_management"],
            ["wealth_management", "private_banking"],
            ["commercial_lending", "cash_management"],
            ["international_banking", "trade_finance"]
        ]
        
        for i in range(10):
            manager = RelationshipManager(
                manager_id=f"RM{self.fake.unique.random_number(digits=6)}",
                name=self.fake.name(),
                email=self.fake.email(),
                phone=self.fake.phone_number(),
                branch=self.fake.city(),
                specialization=random.choice(specializations),
                experience_years=random.randint(2, 15)
            )
            self._relationship_managers.append(manager)
        
        # Generate Nostro accounts
        # Ensure we have at least one EUR account
        eur_account = NostroAccount(
            account_id=f"ACC{self.fake.unique.random_number(digits=10)}",
            currency=Currency.EUR,
            account_type=AccountType.NOSTRO,
            correspondent_bank="Deutsche Bank AG",
            correspondent_swift="DEUTDEFF",
            balance=round(random.uniform(500000, 2000000), 2),
            available_balance=round(random.uniform(300000, 1000000), 2),
            last_updated=self.fake.date_time_between(start_date='-30d', end_date='now'),
            account_status="active"
        )
        self._nostro_accounts.append(eur_account)
        
        # Generate other nostro accounts
        for i in range(9):
            account = NostroAccount(
                account_id=f"ACC{self.fake.unique.random_number(digits=10)}",
                currency=random.choice(list(Currency)),
                account_type=random.choice(list(AccountType)),
                correspondent_bank=self.fake.company(),
                correspondent_swift=self.fake.swift(),
                balance=round(random.uniform(100000, 1000000), 2),
                available_balance=round(random.uniform(50000, 500000), 2),
                last_updated=self.fake.date_time_between(start_date='-30d', end_date='now'),
                account_status=random.choice(["active", "inactive", "suspended"])
            )
            self._nostro_accounts.append(account)
        
        # Generate export settlements
        # Ensure we have at least one EUR export settlement
        eur_settlement = ExportSettlement(
            settlement_id=f"SETT{self.fake.unique.random_number(digits=10)}",
            nostro_account_id=eur_account.account_id,  # Link to EUR account
            amount=round(random.uniform(50000, 200000), 2),
            currency=Currency.EUR,
            settlement_type=SettlementType.EXPORT,
            export_reference=f"EXP{self.fake.unique.random_number(digits=8)}",
            counterparty=self.fake.company(),
            settlement_date=self.fake.date_time_between(start_date='-15d', end_date='now'),
            expected_credit_date=self.fake.date_time_between(start_date='now', end_date='+5d'),
            actual_credit_date=None,
            status=random.choice([TransactionStatus.COMPLETED, TransactionStatus.PENDING]),
            swift_message_ref=self.fake.swift()
        )
        self._export_settlements.append(eur_settlement)
        
        # Generate other settlements
        for i in range(9):
            settlement = ExportSettlement(
                settlement_id=f"SETT{self.fake.unique.random_number(digits=10)}",
                nostro_account_id=random.choice(self._nostro_accounts).account_id,
                amount=round(random.uniform(10000, 100000), 2),
                currency=random.choice(list(Currency)),
                settlement_type=random.choice(list(SettlementType)),
                export_reference=self.fake.uuid4(),
                counterparty=self.fake.company(),
                settlement_date=self.fake.date_time_between(start_date='-30d', end_date='now'),
                expected_credit_date=self.fake.date_time_between(start_date='now', end_date='+30d'),
                actual_credit_date=None,
                status=random.choice(list(TransactionStatus)),
                swift_message_ref=self.fake.swift()
            )
            self._export_settlements.append(settlement)
    
    def get_transactions(self, limit: int = 5) -> List[PaymentTransaction]:
        """Get last N transactions"""
        return self._transactions[:limit]
    
    def get_relationship_manager(self, account_number: Optional[str] = None) -> RelationshipManager:
        """Get relationship manager for account or random manager"""
        return random.choice(self._relationship_managers)

    def create_service_request(self, transaction_id: str, reason: str) -> ServiceRequest:
        """Create a new service request for a transaction"""
        manager = self.get_relationship_manager()

        service_request = ServiceRequest(
            service_request_id=f"SVC{self.fake.unique.random_number(digits=8)}",
            transaction_id=transaction_id,
            customer_account=self.fake.iban(),
            sr_reason=reason,
            status=ServiceRequestStatus.OPEN,
            created_date=datetime.now(),
            assigned_manager_id=manager.manager_id
        )

        self._service_requests.append(service_request)
        return service_request

    def verify_transaction(self, transaction_id: str) -> TransactionVerification:
        """Verify if transaction is credited to account"""
        # Find transaction in our mock data
        transaction = None
        for txn in self._transactions:
            if txn.transaction_id == transaction_id:
                transaction = txn
                break
        
        if not transaction:
            return TransactionVerification(
                transaction_id=transaction_id,
                is_credited=False,
                verification_status="transaction_not_found",
                notes="Transaction ID not found in system"
            )
        
        # Simulate verification logic based on transaction status
        if transaction.status == TransactionStatus.COMPLETED:
            is_credited = True
            credited_amount = transaction.amount
            credited_date = transaction.transaction_date + timedelta(hours=random.randint(1, 24))
            verification_status = "credited"
            notes = "Transaction successfully credited to account"
        elif transaction.status == TransactionStatus.PENDING:
            is_credited = False
            credited_amount = None
            credited_date = None
            verification_status = "pending"
            notes = "Transaction is still being processed"
        else:
            is_credited = False
            credited_amount = None
            credited_date = None
            verification_status = "failed"
            notes = "Transaction failed and amount not credited"
        
        return TransactionVerification(
            transaction_id=transaction_id,
            is_credited=is_credited,
            credited_amount=credited_amount,
            credited_date=credited_date,
            verification_status=verification_status,
            notes=notes
        )
    
    def get_nostro_accounts(self, currency: Optional[str] = None) -> List[NostroAccount]:
        """Get nostro accounts, optionally filtered by currency"""
        if currency:
            return [acc for acc in self._nostro_accounts if acc.currency.value == currency.upper()]
        return self._nostro_accounts
    
    def get_euro_nostro_account(self) -> Optional[NostroAccount]:
        """Get Euro nostro account specifically"""
        euro_accounts = [acc for acc in self._nostro_accounts if acc.currency == Currency.EUR]
        return euro_accounts[0] if euro_accounts else None
    
    def check_export_settlement_credit(self, export_reference: Optional[str] = None, currency: str = "EUR") -> Dict[str, Any]:
        """Check if Euro nostro account is credited for export settlement"""
        # Find export settlements for Euro currency
        euro_settlements = [
            settlement for settlement in self._export_settlements 
            if settlement.currency.value == currency.upper() and settlement.settlement_type == SettlementType.EXPORT
        ]
        
        if export_reference:
            # Find specific export settlement
            euro_settlements = [
                settlement for settlement in euro_settlements 
                if settlement.export_reference == export_reference
            ]
        
        if not euro_settlements:
            return {
                "status": "not_found",
                "message": f"No {currency} export settlements found" + (f" for reference {export_reference}" if export_reference else ""),
                "settlements": []
            }
        
        # Get Euro nostro account
        euro_nostro = self.get_euro_nostro_account()
        if not euro_nostro:
            return {
                "status": "error",
                "message": "Euro nostro account not found",
                "settlements": []
            }
        
        # Check credit status for settlements
        settlement_details = []
        total_credited = 0
        total_pending = 0
        
        for settlement in euro_settlements:
            is_credited = settlement.status == TransactionStatus.COMPLETED
            if is_credited:
                settlement.actual_credit_date = settlement.settlement_date + timedelta(days=random.randint(1, 3))
                total_credited += settlement.amount
            else:
                total_pending += settlement.amount
            
            settlement_details.append({
                "settlement_id": settlement.settlement_id,
                "export_reference": settlement.export_reference,
                "amount": settlement.amount,
                "currency": settlement.currency.value,
                "counterparty": settlement.counterparty,
                "settlement_date": settlement.settlement_date.isoformat(),
                "expected_credit_date": settlement.expected_credit_date.isoformat(),
                "actual_credit_date": settlement.actual_credit_date.isoformat() if settlement.actual_credit_date else None,
                "status": settlement.status.value,
                "is_credited": is_credited,
                "swift_message_ref": settlement.swift_message_ref
            })
        
        return {
            "status": "success",
            "message": f"Found {len(euro_settlements)} {currency} export settlement(s)",
            "nostro_account": {
                "account_id": euro_nostro.account_id,
                "currency": euro_nostro.currency.value,
                "correspondent_bank": euro_nostro.correspondent_bank,
                "correspondent_swift": euro_nostro.correspondent_swift,
                "current_balance": euro_nostro.balance,
                "available_balance": euro_nostro.available_balance,
                "last_updated": euro_nostro.last_updated.isoformat()
            },
            "settlements": settlement_details,
            "summary": {
                "total_settlements": len(euro_settlements),
                "total_credited_amount": total_credited,
                "total_pending_amount": total_pending,
                "credited_count": len([s for s in settlement_details if s["is_credited"]]),
                "pending_count": len([s for s in settlement_details if not s["is_credited"]])
            }
        }

# Global instance for the application
data_generator = MockDataGenerator()
