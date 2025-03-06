# transactions.py
from app.main.tools.utils import APICallService
import app.main.config as config
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
import json

def get_uncategorized_transactions(req_context, date_range="This Calendar Year"):
    """
    Fetch uncategorized transactions from QuickBooks
    
    Args:
        req_context: Request context containing authentication info
        date_range: Date range for transaction search (e.g., "This Calendar Year", "Last Month")
        
    Returns:
        List of uncategorized transactions
    """
    uri = "/reports/TransactionList?minorversion=" + config.API_MINORVERSION
    params = {
        "date_macro": date_range,
        # Additional filter parameters for uncategorized transactions would go here
        # This will depend on the exact QuickBooks API structure
    }
    
    response = APICallService.get_request(req_context, uri, params)
    
    # Extract and transform the transactions from the response
    transactions = []
    if response and 'Rows' in response and 'Row' in response['Rows']:
        for row in response['Rows']['Row']:
            # This structure will need adjustment based on the actual API response
            transaction = {
                "id": row.get("Id", ""),
                "date": row.get("ColData", [])[0].get("value", "") if row.get("ColData") else "",
                "merchant": row.get("ColData", [])[1].get("value", "") if row.get("ColData") else "",
                "description": row.get("ColData", [])[2].get("value", "") if row.get("ColData") else "",
                "amount": row.get("ColData", [])[3].get("value", "") if row.get("ColData") else ""
            }
            transactions.append(transaction)
    
    return transactions

def categorize_transaction(req_context, transaction_id, category):
    """
    Update a transaction's category in QuickBooks
    
    Args:
        req_context: Request context containing authentication info
        transaction_id: ID of the transaction to update
        category: Category to assign to the transaction
        
    Returns:
        Result of the API call
    """
    uri = f"/transaction/{transaction_id}?minorversion={config.API_MINORVERSION}"
    
    # Construct the payload based on QuickBooks API requirements
    payload = {
        "Id": transaction_id,
        "Category": category
        # Additional fields as required by the API
    }
    
    response = APICallService.post_request(req_context, uri, payload)
    return response

def get_historical_transactions(req_context):
    """
    Fetch historical transaction data for a specific merchant or keyword
    
    Args:
        req_context: Request context containing authentication info
        keyword: Merchant name or keyword to search for
        limit: Maximum number of records to return
        
    Returns:
        List of historical transactions
    """
    # Using the Query endpoint to search for transactions by keyword
    uri = f"/reports/TransactionList?date_macro=This Calendar Year&minorversion={config.API_MINORVERSION}"
    
    
    response = APICallService.get_request(req_context, uri, {})
    
    # Parse and return the historical transactions
    historical_data = []
    if response and 'QueryResponse' in response and 'Transaction' in response['QueryResponse']:
        for tx in response['QueryResponse']['Transaction']:
            transaction = {
                "merchant": tx.get("Description", ""),
                "amount": tx.get("Amount", ""),
                "category": tx.get("Category", "")
                # Add other relevant fields
            }
            historical_data.append(transaction)
    
    return historical_data