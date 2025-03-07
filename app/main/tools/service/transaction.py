# transactions.py
from app.main.tools.utils import api_call
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
    
    response = api_call.get_request(req_context, uri, {})
    data = response.json()
    
    historical_data = []

    # Check if the response has the expected structure
    if data and 'Rows' in data and 'Row' in data['Rows']:
        for row in data['Rows']['Row']:
            col_data = row.get('ColData', [])
            print(col_data)
            # Only process rows with the expected 9 columns
            if len(col_data) < 9:
                continue

            transaction = {
                "date": col_data[0].get("value", ""),
                "transaction_type": col_data[1].get("value", ""),
                "doc_num": col_data[2].get("value", ""),
                "posting": col_data[3].get("value", ""),
                "name": col_data[4].get("value", ""),
                "description": col_data[5].get("value", ""),
                "account": col_data[6].get("value", ""),
                "category": col_data[7].get("value", ""),
                "amount": col_data[8].get("value", "")
            }
            historical_data.append(transaction)

    return historical_data


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
    
    response = api_call.post_request(req_context, uri, payload)
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
    
    
    response = api_call.get_request(req_context, uri, {})
    data = response.json()
    historical_data = []

    # Check if the response has the expected structure
    if data and 'Rows' in data and 'Row' in data['Rows']:
        for row in data['Rows']['Row']:
            col_data = row.get('ColData', [])
            print(col_data)
            # Only process rows with the expected 9 columns
            if len(col_data) < 9:
                continue

            transaction = {
                "date": col_data[0].get("value", ""),
                "transaction_type": col_data[1].get("value", ""),
                "doc_num": col_data[2].get("value", ""),
                "posting": col_data[3].get("value", ""),
                "name": col_data[4].get("value", ""),
                "description": col_data[5].get("value", ""),
                "account": col_data[6].get("value", ""),
                "category": col_data[7].get("value", ""),
                "amount": col_data[8].get("value", "")
            }
            historical_data.append(transaction)

    return historical_data
