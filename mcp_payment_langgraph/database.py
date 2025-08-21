#!/usr/bin/env python3
"""
Database management module for MCP Payment Transaction Server
Implements SQLite-based persistent storage with best practices
"""

import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Generator
from faker import Faker
import random
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

class PaymentDatabase:
    """SQLite database manager for payment transactions with best practices"""
    
    def __init__(self, db_path: str = "payment_transactions.db"):
        self.db_path = db_path
        self.init_database()
        
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        if os.path.exists(self.db_path):
            logger.info("Database already exists, skipping creation")
            return
            
        logger.info("Creating new database and tables")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    customer_name TEXT NOT NULL,
                    customer_type TEXT NOT NULL,
                    relationship_manager_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # High value transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_value_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    status TEXT NOT NULL,
                    transaction_date TIMESTAMP NOT NULL,
                    description TEXT,
                    recipient_name TEXT,
                    recipient_account TEXT,
                    transaction_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Relationship managers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationship_managers (
                    manager_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    branch TEXT,
                    specialization TEXT,
                    experience_years INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Disputes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disputes (
                    dispute_id TEXT PRIMARY KEY,
                    transaction_id TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    customer_account TEXT NOT NULL,
                    dispute_reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_manager_id TEXT,
                    resolution_notes TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES high_value_transactions (transaction_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                    FOREIGN KEY (assigned_manager_id) REFERENCES relationship_managers (manager_id)
                )
            """)
            
            # Transaction verifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_verifications (
                    verification_id TEXT PRIMARY KEY,
                    transaction_id TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    is_credited BOOLEAN NOT NULL,
                    credited_amount REAL,
                    credited_date TIMESTAMP,
                    verification_status TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (transaction_id) REFERENCES high_value_transactions (transaction_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Nostro accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nostro_accounts (
                    account_id TEXT PRIMARY KEY,
                    currency TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    correspondent_bank TEXT NOT NULL,
                    correspondent_swift TEXT NOT NULL,
                    balance REAL NOT NULL,
                    available_balance REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    account_status TEXT DEFAULT 'active'
                )
            """)
            
            # Euro nostro settlements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS euro_nostro_settlements (
                    settlement_id TEXT PRIMARY KEY,
                    nostro_account_id TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'EUR',
                    settlement_type TEXT NOT NULL,
                    export_reference TEXT,
                    counterparty TEXT NOT NULL,
                    settlement_date TIMESTAMP NOT NULL,
                    expected_credit_date TIMESTAMP,
                    actual_credit_date TIMESTAMP,
                    status TEXT NOT NULL,
                    swift_message_ref TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nostro_account_id) REFERENCES nostro_accounts (account_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Treasury pricing table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS treasury_pricing (
                    pricing_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    currency_pair TEXT NOT NULL,
                    rate REAL NOT NULL,
                    margin REAL NOT NULL,
                    valid_until TIMESTAMP NOT NULL,
                    pricing_tier TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Investment proposals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_proposals (
                    proposal_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    product_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    expected_return REAL,
                    risk_level TEXT,
                    proposal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    maturity_date TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Cash forecasts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cash_forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    forecast_date TIMESTAMP NOT NULL,
                    currency TEXT NOT NULL,
                    opening_balance REAL NOT NULL,
                    projected_inflows REAL NOT NULL,
                    projected_outflows REAL NOT NULL,
                    closing_balance REAL NOT NULL,
                    confidence_level REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Risk limits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_limits (
                    limit_id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    limit_type TEXT NOT NULL,
                    limit_amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    utilization REAL DEFAULT 0,
                    utilization_percentage REAL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            """)
            
            # Request logs table for audit trail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS request_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    customer_id TEXT,
                    request_type TEXT NOT NULL,
                    request_data TEXT,
                    response_data TEXT,
                    execution_time_ms INTEGER
                )
            """)
            
            conn.commit()
            logger.info("Database tables created successfully")
            
            # Populate with initial data
            self.populate_initial_data()
    
    def populate_initial_data(self):
        """Populate database with mock data for 5 customers"""
        logger.info("Populating database with initial mock data")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] > 0:
                logger.info("Data already exists, skipping population")
                return
            
            # Create 5 relationship managers
            managers = []
            for i in range(5):
                manager = {
                    'manager_id': f"RM_{fake.random_int(1000, 9999)}",
                    'name': fake.name(),
                    'email': fake.email(),
                    'phone': fake.phone_number(),
                    'branch': fake.city(),
                    'specialization': json.dumps(random.choices([
                        'FX Trading', 'Treasury Management', 'Trade Finance', 
                        'Investment Banking', 'Risk Management', 'Cash Management'
                    ], k=random.randint(2, 4))),
                    'experience_years': random.randint(5, 20)
                }
                managers.append(manager)
                
                cursor.execute("""
                    INSERT INTO relationship_managers 
                    (manager_id, name, email, phone, branch, specialization, experience_years)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (manager['manager_id'], manager['name'], manager['email'], 
                     manager['phone'], manager['branch'], manager['specialization'], 
                     manager['experience_years']))
            
            # Create 5 customers
            customers = []
            customer_types = ['Corporate', 'Financial Institution', 'Government', 'SME', 'Private Banking']
            
            for i, ctype in enumerate(customer_types):
                customer = {
                    'customer_id': f"CUST_{fake.random_int(100000, 999999)}",
                    'customer_name': fake.company() if ctype != 'Private Banking' else fake.name(),
                    'customer_type': ctype,
                    'relationship_manager_id': managers[i]['manager_id']
                }
                customers.append(customer)
                
                cursor.execute("""
                    INSERT INTO customers (customer_id, customer_name, customer_type, relationship_manager_id)
                    VALUES (?, ?, ?, ?)
                """, (customer['customer_id'], customer['customer_name'], 
                     customer['customer_type'], customer['relationship_manager_id']))
            
            # Create nostro accounts
            currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF']
            correspondent_banks = [
                'JPMorgan Chase', 'Deutsche Bank', 'Barclays', 'MUFG Bank', 'UBS'
            ]
            swift_codes = ['CHASUS33', 'DEUTDEFF', 'BARCGB22', 'BOTKJPJT', 'UBSWCHZH']
            
            for i, currency in enumerate(currencies):
                for j in range(2):  # 2 accounts per currency
                    account = {
                        'account_id': f"NOSTRO_{currency}_{fake.random_int(1000, 9999)}",
                        'currency': currency,
                        'account_type': 'nostro',
                        'correspondent_bank': correspondent_banks[i],
                        'correspondent_swift': swift_codes[i],
                        'balance': round(random.uniform(1000000, 50000000), 2),
                        'available_balance': round(random.uniform(500000, 30000000), 2)
                    }
                    
                    cursor.execute("""
                        INSERT INTO nostro_accounts 
                        (account_id, currency, account_type, correspondent_bank, correspondent_swift, 
                         balance, available_balance)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (account['account_id'], account['currency'], account['account_type'],
                         account['correspondent_bank'], account['correspondent_swift'],
                         account['balance'], account['available_balance']))
            
            # Create high value transactions for each customer
            statuses = ['completed', 'failed', 'pending', 'disputed']
            transaction_types = ['SWIFT Wire', 'FX Settlement', 'Trade Finance', 'Treasury Payment']
            
            for customer in customers:
                for i in range(random.randint(10, 25)):  # 10-25 transactions per customer
                    # Generate transaction date within last 3 months
                    days_ago = random.randint(1, 90)
                    transaction_date = datetime.now() - timedelta(days=days_ago)
                    
                    transaction = {
                        'transaction_id': f"TXN_{fake.random_int(100000, 999999)}",
                        'customer_id': customer['customer_id'],
                        'account_number': f"ACC_{fake.random_int(100000, 999999)}",
                        'amount': round(random.uniform(100000, 10000000), 2),  # High value >100K
                        'currency': random.choice(currencies),
                        'status': random.choice(statuses),
                        'transaction_date': transaction_date.isoformat(),
                        'description': fake.sentence(),
                        'recipient_name': fake.company(),
                        'recipient_account': f"REC_{fake.random_int(100000, 999999)}",
                        'transaction_type': random.choice(transaction_types)
                    }
                    
                    cursor.execute("""
                        INSERT INTO high_value_transactions 
                        (transaction_id, customer_id, account_number, amount, currency, status,
                         transaction_date, description, recipient_name, recipient_account, transaction_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (transaction['transaction_id'], transaction['customer_id'], 
                         transaction['account_number'], transaction['amount'], transaction['currency'],
                         transaction['status'], transaction['transaction_date'], transaction['description'],
                         transaction['recipient_name'], transaction['recipient_account'], 
                         transaction['transaction_type']))
                    
                    # Create verification record for some transactions
                    if random.random() < 0.7:  # 70% have verification records
                        verification = {
                            'verification_id': f"VER_{fake.random_int(100000, 999999)}",
                            'transaction_id': transaction['transaction_id'],
                            'customer_id': customer['customer_id'],
                            'is_credited': transaction['status'] == 'completed',
                            'credited_amount': transaction['amount'] if transaction['status'] == 'completed' else None,
                            'credited_date': transaction_date.isoformat() if transaction['status'] == 'completed' else None,
                            'verification_status': 'verified' if transaction['status'] == 'completed' else 'pending',
                            'notes': fake.sentence()
                        }
                        
                        cursor.execute("""
                            INSERT INTO transaction_verifications 
                            (verification_id, transaction_id, customer_id, is_credited, credited_amount,
                             credited_date, verification_status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (verification['verification_id'], verification['transaction_id'],
                             verification['customer_id'], verification['is_credited'],
                             verification['credited_amount'], verification['credited_date'],
                             verification['verification_status'], verification['notes']))
            
            # Create EUR nostro settlements
            eur_accounts = cursor.execute("SELECT account_id FROM nostro_accounts WHERE currency = 'EUR'").fetchall()
            
            for customer in customers:
                for i in range(random.randint(2, 8)):  # 2-8 settlements per customer
                    settlement_date = datetime.now() - timedelta(days=random.randint(1, 60))
                    
                    settlement = {
                        'settlement_id': f"SETT_{fake.random_int(100000, 999999)}",
                        'nostro_account_id': random.choice(eur_accounts)['account_id'],
                        'customer_id': customer['customer_id'],
                        'amount': round(random.uniform(50000, 2000000), 2),
                        'currency': 'EUR',
                        'settlement_type': 'export',
                        'export_reference': f"EXP_{fake.random_int(100000, 999999)}",
                        'counterparty': fake.company(),
                        'settlement_date': settlement_date.isoformat(),
                        'expected_credit_date': (settlement_date + timedelta(days=random.randint(1, 3))).isoformat(),
                        'actual_credit_date': (settlement_date + timedelta(days=random.randint(1, 5))).isoformat() if random.random() < 0.8 else None,
                        'status': random.choice(['completed', 'pending', 'processing']),
                        'swift_message_ref': f"MT{random.randint(100, 999)}{fake.random_int(100000, 999999)}"
                    }
                    
                    cursor.execute("""
                        INSERT INTO euro_nostro_settlements 
                        (settlement_id, nostro_account_id, customer_id, amount, currency, settlement_type,
                         export_reference, counterparty, settlement_date, expected_credit_date,
                         actual_credit_date, status, swift_message_ref)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (settlement['settlement_id'], settlement['nostro_account_id'], settlement['customer_id'],
                         settlement['amount'], settlement['currency'], settlement['settlement_type'],
                         settlement['export_reference'], settlement['counterparty'], settlement['settlement_date'],
                         settlement['expected_credit_date'], settlement['actual_credit_date'],
                         settlement['status'], settlement['swift_message_ref']))
            
            # Create treasury pricing, investment proposals, cash forecasts, and risk limits
            self._create_treasury_data(cursor, customers)
            
            conn.commit()
            logger.info("Initial data population completed successfully")
    
    def _create_treasury_data(self, cursor, customers):
        """Create treasury-related data for personalized journey"""
        currency_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
        
        for customer in customers:
            # Treasury pricing
            for pair in currency_pairs:
                cursor.execute("""
                    INSERT INTO treasury_pricing 
                    (pricing_id, customer_id, currency_pair, rate, margin, valid_until, pricing_tier)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f"PRICE_{fake.random_int(100000, 999999)}", customer['customer_id'], pair,
                     round(random.uniform(0.5, 2.0), 4), round(random.uniform(0.001, 0.01), 4),
                     (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat(),
                     random.choice(['Standard', 'Premium', 'VIP'])))
            
            # Investment proposals
            products = ['Fixed Deposit', 'Money Market', 'Corporate Bonds', 'Treasury Bills']
            for i in range(random.randint(2, 5)):
                cursor.execute("""
                    INSERT INTO investment_proposals 
                    (proposal_id, customer_id, product_type, amount, currency, expected_return, 
                     risk_level, maturity_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"PROP_{fake.random_int(100000, 999999)}", customer['customer_id'],
                     random.choice(products), round(random.uniform(100000, 5000000), 2),
                     random.choice(['USD', 'EUR', 'GBP']), round(random.uniform(2.5, 8.5), 2),
                     random.choice(['Low', 'Medium', 'High']),
                     (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                     random.choice(['pending', 'approved', 'under_review'])))
            
            # Cash forecasts
            for i in range(random.randint(5, 10)):
                forecast_date = datetime.now() + timedelta(days=i+1)
                opening = round(random.uniform(500000, 10000000), 2)
                inflows = round(random.uniform(100000, 2000000), 2)
                outflows = round(random.uniform(50000, 1500000), 2)
                
                cursor.execute("""
                    INSERT INTO cash_forecasts 
                    (forecast_id, customer_id, forecast_date, currency, opening_balance,
                     projected_inflows, projected_outflows, closing_balance, confidence_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (f"FCST_{fake.random_int(100000, 999999)}", customer['customer_id'],
                     forecast_date.isoformat(), random.choice(['USD', 'EUR', 'GBP']),
                     opening, inflows, outflows, opening + inflows - outflows,
                     round(random.uniform(0.7, 0.95), 2)))
            
            # Risk limits
            limit_types = ['Credit Limit', 'FX Exposure', 'Counterparty Risk', 'Concentration Risk']
            for limit_type in limit_types:
                limit_amount = round(random.uniform(1000000, 50000000), 2)
                utilization = round(random.uniform(0, limit_amount * 0.8), 2)
                
                cursor.execute("""
                    INSERT INTO risk_limits 
                    (limit_id, customer_id, limit_type, limit_amount, currency, utilization,
                     utilization_percentage)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (f"LIMIT_{fake.random_int(100000, 999999)}", customer['customer_id'],
                     limit_type, limit_amount, random.choice(['USD', 'EUR', 'GBP']),
                     utilization, round((utilization / limit_amount) * 100, 2)))

# Global database instance
payment_db = PaymentDatabase()
