#!/usr/bin/env python3
"""
Request/Response logging module for MCP Payment Transaction Server
Provides audit trail and debugging capabilities
"""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from database import payment_db
from customer_manager import customer_manager

# Configure file logger
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [Customer: %(customer_id)s] - %(message)s'
)

file_handler = logging.FileHandler('mcp_server.log')
file_handler.setFormatter(log_formatter)

# Create logger
server_logger = logging.getLogger('mcp_server')
server_logger.setLevel(logging.INFO)
server_logger.addHandler(file_handler)

# Also log to console for debugging
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
server_logger.addHandler(console_handler)

class RequestLogger:
    """Handles request/response logging with database persistence"""
    
    @staticmethod
    def log_request_response(
        request_type: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        execution_time_ms: int,
        customer_id: Optional[str] = None
    ):
        """Log request and response to both file and database"""
        
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            customer_id = current_customer['customer_id'] if current_customer else 'unknown'
        
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'customer_id': customer_id,
            'request_type': request_type,
            'request_data': request_data,
            'response_data': response_data,
            'execution_time_ms': execution_time_ms
        }
        
        # Log to file with customer context
        extra = {'customer_id': customer_id}
        server_logger.info(
            f"REQUEST: {request_type} | "
            f"EXECUTION_TIME: {execution_time_ms}ms | "
            f"REQUEST: {json.dumps(request_data, default=str)} | "
            f"RESPONSE: {json.dumps(response_data, default=str)}",
            extra=extra
        )
        
        # Log to database
        try:
            with payment_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO request_logs 
                    (customer_id, request_type, request_data, response_data, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    customer_id,
                    request_type,
                    json.dumps(request_data, default=str),
                    json.dumps(response_data, default=str),
                    execution_time_ms
                ))
                conn.commit()
                
        except Exception as e:
            server_logger.error(f"Failed to log to database: {e}", extra=extra)
    
    @staticmethod
    def log_error(
        request_type: str,
        error_message: str,
        request_data: Optional[Dict[str, Any]] = None,
        customer_id: Optional[str] = None
    ):
        """Log error occurrences"""
        
        if not customer_id:
            current_customer = customer_manager.get_current_customer()
            customer_id = current_customer['customer_id'] if current_customer else 'unknown'
        
        extra = {'customer_id': customer_id}
        server_logger.error(
            f"ERROR in {request_type}: {error_message} | "
            f"REQUEST: {json.dumps(request_data or {}, default=str)}",
            extra=extra
        )
    
    @staticmethod
    def log_customer_switch(old_customer: Optional[str], new_customer: str):
        """Log customer context switches"""
        extra = {'customer_id': new_customer}
        server_logger.info(
            f"CUSTOMER_SWITCH: From {old_customer or 'None'} to {new_customer}",
            extra=extra
        )

def log_execution_time(func):
    """Decorator to automatically log execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Extract function name and basic info
            func_name = func.__name__
            current_customer = customer_manager.get_current_customer()
            customer_id = current_customer['customer_id'] if current_customer else 'unknown'
            
            extra = {'customer_id': customer_id}
            server_logger.info(
                f"EXECUTION: {func_name} completed in {execution_time}ms",
                extra=extra
            )
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            current_customer = customer_manager.get_current_customer()
            customer_id = current_customer['customer_id'] if current_customer else 'unknown'
            
            RequestLogger.log_error(func.__name__, str(e), customer_id=customer_id)
            raise
            
    return wrapper

# Global logger instance
request_logger = RequestLogger()
