# categorization.py
from app.main.tools.utils import APICallService
import app.main.config as config
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from app.main.tools.service.transaction import get_historical_transactions
import json

def get_llm(provider="gemini"):
    """
    Initialize and return an LLM based on the provider
    
    Args:
        provider: LLM provider ("gemini", "openai", or "reasoning")
    
    Returns:
        Initialized LLM
    """
    if provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    elif provider == "openai":
        return ChatOpenAI(model="gpt-4o-2024-05-13")
    else:  # Reasoning model
        return ChatOpenAI(model="gpt-4o")  # Less expensive than 4.5

def suggest_category(req_context, transaction, llm_provider="gemini"):
    """
    Suggest a category for a transaction using an LLM
    
    Args:
        req_context: Request context containing authentication info
        transaction: Transaction data
        llm_provider: LLM provider to use
    
    Returns:
        Dict with suggested category and explanation
    """
    # Get historical data for this merchant
    merchant = transaction.get("merchant", "")
    historical_data = get_historical_transactions(req_context, merchant)
    
    # Initialize LLM
    llm = get_llm(llm_provider)
    
    # Create prompt template
    template = """
    You are an AI assistant that helps categorize financial transactions.
    
    TRANSACTION:
    Merchant: {merchant}
    Amount: ${amount}
    Date: {date}
    Description: {description}
    
    HISTORICAL DATA FOR SIMILAR TRANSACTIONS:
    {historical_data}
    
    AVAILABLE CATEGORIES:
    Office Supplies, Meals & Entertainment, Travel, Rent, Utilities, Professional Services, 
    Insurance, Marketing, Maintenance, Equipment, Software, Payroll, Other
    
    Based on the transaction details and historical data, suggest the most appropriate category.
    Provide a brief explanation for your suggestion.
    
    Format your response as:
    SUGGESTED CATEGORY: [category]
    REASON: [brief explanation]
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["merchant", "amount", "date", "description", "historical_data"]
    )
    
    # Format historical data for the prompt
    hist_str = "None" if not historical_data else "\n".join([
        f"- {h.get('merchant', 'Unknown')}: ${h.get('amount', 'N/A')} - Categorized as: {h.get('category', 'N/A')}"
        for h in historical_data[:5]  # Limit to 5 examples
    ])
    
    # Create and run LLM chain
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(
        merchant=transaction.get("merchant", ""),
        amount=transaction.get("amount", ""),
        date=transaction.get("date", ""),
        description=transaction.get("description", ""),
        historical_data=hist_str
    )
    
    # Parse the result
    category = "Uncategorized"
    reason = "No suggestion available"
    
    if "SUGGESTED CATEGORY:" in result:
        parts = result.split("SUGGESTED CATEGORY:", 1)[1].split("REASON:", 1)
        if len(parts) >= 1:
            category = parts[0].strip()
        if len(parts) >= 2:
            reason = parts[1].strip()
    
    return {
        "category": category,
        "reason": reason
    }

def batch_suggest_categories(req_context, transactions, llm_provider="gemini"):
    """
    Group similar transactions and suggest categories in batches
    
    Args:
        req_context: Request context containing authentication info
        transactions: List of transactions
        llm_provider: LLM provider to use
    
    Returns:
        Dict with batch suggestions
    """
    # Group transactions by merchant
    merchant_groups = {}
    for tx in transactions:
        merchant = tx.get("merchant", "")
        if merchant not in merchant_groups:
            merchant_groups[merchant] = []
        merchant_groups[merchant].append(tx)
    
    # Process each group
    results = []
    for merchant, txs in merchant_groups.items():
        if len(txs) > 1:
            # If multiple transactions from same merchant, suggest batch categorization
            sample_tx = txs[0]
            suggestion = suggest_category(req_context, sample_tx, llm_provider)
            results.append({
                "merchant": merchant,
                "transactions": txs,
                "suggested_category": suggestion["category"],
                "reason": suggestion["reason"],
                "is_batch": True,
                "count": len(txs)
            })
        else:
            # Single transaction
            suggestion = suggest_category(req_context, txs[0], llm_provider)
            results.append({
                "merchant": merchant,
                "transactions": txs,
                "suggested_category": suggestion["category"],
                "reason": suggestion["reason"],
                "is_batch": False,
                "count": 1
            })
    
    return results

def generate_categorization_report(req_context, date_range="This Calendar Year", llm_provider="gemini"):
    """
    Generate a comprehensive report of transaction categorization suggestions
    
    Args:
        req_context: Request context containing authentication info
        date_range: Date range for transaction search
        llm_provider: LLM provider to use
        
    Returns:
        Formatted report with categorization suggestions
    """
    from app.main.tools.service.transaction import get_uncategorized_transactions
    
    # Fetch uncategorized transactions
    transactions = get_uncategorized_transactions(req_context, date_range)
    
    # If no uncategorized transactions
    if not transactions:
        return "No uncategorized transactions found for the specified period."
    
    # Process individual transactions
    individual_results = []
    for tx in transactions:
        suggestion = suggest_category(req_context, tx, llm_provider)
        individual_results.append({
            "transaction": tx,
            "suggested_category": suggestion["category"],
            "reason": suggestion["reason"]
        })
    
    # Process transactions in batches
    batch_results = batch_suggest_categories(req_context, transactions, llm_provider)
    
    # Create report
    report = {
        "date_range": date_range,
        "total_uncategorized": len(transactions),
        "individual_suggestions": individual_results,
        "batch_suggestions": batch_results
    }
    
    return format_report_for_display(report)

def format_report_for_display(report):
    """
    Format the categorization report for display
    
    Args:
        report: Report data
    
    Returns:
        Formatted string
    """
    if isinstance(report, str):
        return report
    
    output = f"# Transaction Categorization Report\n\n"
    output += f"**Date Range:** {report['date_range']}\n"
    output += f"**Total Uncategorized Transactions:** {report['total_uncategorized']}\n\n"
    
    # Display batch suggestions first
    if report['batch_suggestions']:
        output += "## Batch Suggestions\n\n"
        for batch in report['batch_suggestions']:
            if batch['is_batch'] and batch['count'] > 1:
                output += f"### {batch['merchant']} ({batch['count']} transactions)\n"
                output += f"**Suggested Category:** {batch['suggested_category']}\n"
                output += f"**Reason:** {batch['reason']}\n"
                output += "**Transactions:**\n"
                for tx in batch['transactions']:
                    output += f"- ${tx['amount']} on {tx['date']}\n"
                output += "\n"
    
    # Display individual suggestions
    output += "## Individual Suggestions\n\n"
    for result in report['individual_suggestions']:
        tx = result['transaction']
        output += f"**Transaction:** {tx['merchant']} ${tx['amount']} on {tx['date']}\n"
        output += f"**Description:** {tx['description']}\n"
        output += f"**Suggested Category:** {result['suggested_category']}\n"
        output += f"**Reason:** {result['reason']}\n\n"
    
    return output