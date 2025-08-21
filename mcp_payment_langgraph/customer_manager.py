#!/usr/bin/env python3
"""
Customer management module for MCP Payment Transaction Server
Handles customer context switching and session management
"""

import logging
from typing import Optional, Dict, Any, List
from database import payment_db

logger = logging.getLogger(__name__)

class CustomerManager:
    """Manages customer context and switching for personalized experiences"""
    
    def __init__(self):
        self.current_customer_id: Optional[str] = None
        self.customer_cache: Dict[str, Dict[str, Any]] = {}
        self._load_default_customer()
    
    def _load_default_customer(self):
        """Load the first customer as default"""
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT customer_id, customer_name, customer_type 
                    FROM customers 
                    ORDER BY created_at 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                
                if result:
                    self.current_customer_id = result['customer_id']
                    self.customer_cache[result['customer_id']] = {
                        'customer_id': result['customer_id'],
                        'customer_name': result['customer_name'],
                        'customer_type': result['customer_type']
                    }
                    logger.info(f"Default customer set to: {result['customer_name']} ({result['customer_id']})")
                else:
                    logger.warning("No customers found in database")
                    
        except Exception as e:
            logger.error(f"Error loading default customer: {e}")
    
    def get_current_customer(self) -> Optional[Dict[str, Any]]:
        """Get current customer details"""
        if self.current_customer_id and self.current_customer_id in self.customer_cache:
            return self.customer_cache[self.current_customer_id]
        return None
    
    def switch_customer(self, identifier: str) -> bool:
        """
        Switch to a different customer based on identifier
        Identifier can be customer_id, customer_name, or partial name match
        """
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Try exact customer_id match first
                cursor.execute("""
                    SELECT customer_id, customer_name, customer_type 
                    FROM customers 
                    WHERE customer_id = ?
                """, (identifier,))
                result = cursor.fetchone()
                
                # If not found, try name-based search
                if not result:
                    cursor.execute("""
                        SELECT customer_id, customer_name, customer_type 
                        FROM customers 
                        WHERE LOWER(customer_name) LIKE LOWER(?)
                        ORDER BY customer_name
                        LIMIT 1
                    """, (f"%{identifier}%",))
                    result = cursor.fetchone()
                
                if result:
                    old_customer = self.get_current_customer()
                    self.current_customer_id = result['customer_id']
                    self.customer_cache[result['customer_id']] = {
                        'customer_id': result['customer_id'],
                        'customer_name': result['customer_name'],
                        'customer_type': result['customer_type']
                    }
                    
                    logger.info(f"Customer switched from {old_customer['customer_name'] if old_customer else 'None'} "
                              f"to {result['customer_name']} ({result['customer_id']})")
                    return True
                else:
                    logger.warning(f"Customer not found with identifier: {identifier}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error switching customer: {e}")
            return False
    
    def list_customers(self) -> List[Dict[str, Any]]:
        """Get list of all customers"""
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT customer_id, customer_name, customer_type,
                           (SELECT COUNT(*) FROM high_value_transactions 
                            WHERE customer_id = c.customer_id) as transaction_count
                    FROM customers c
                    ORDER BY customer_name
                """)
                
                customers = []
                for row in cursor.fetchall():
                    customers.append({
                        'customer_id': row['customer_id'],
                        'customer_name': row['customer_name'],
                        'customer_type': row['customer_type'],
                        'transaction_count': row['transaction_count'],
                        'is_current': row['customer_id'] == self.current_customer_id
                    })
                
                return customers
                
        except Exception as e:
            logger.error(f"Error listing customers: {e}")
            return []
    
    def detect_customer_switch_request(self, user_input: str) -> Optional[str]:
        """
        Detect if user is requesting to switch customer context
        Returns customer identifier if detected, None otherwise
        """
        user_input_lower = user_input.lower()
        
        # Common patterns for customer switching
        switch_patterns = [
            "switch to customer",
            "change to customer", 
            "for customer",
            "customer:",
            "switch customer",
            "change customer"
        ]
        
        for pattern in switch_patterns:
            if pattern in user_input_lower:
                # Extract potential customer identifier after the pattern
                start_idx = user_input_lower.find(pattern) + len(pattern)
                remaining_text = user_input[start_idx:].strip()
                
                # Remove common words and get the identifier
                words = remaining_text.split()
                if words:
                    # Take the first word/phrase as customer identifier
                    identifier = words[0].strip('":,')
                    return identifier
        
        # Check if customer ID pattern is mentioned
        words = user_input.split()
        for word in words:
            if word.startswith('CUST_') and len(word) > 5:
                return word
                
        return None

# Global customer manager instance
customer_manager = CustomerManager()
