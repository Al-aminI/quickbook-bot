# chat_handler.py
from app.main.tools.service.transaction import get_uncategorized_transactions, categorize_transaction, get_historical_transactions
from app.main.tools.service.categorization import suggest_category, batch_suggest_categories
import json

class QBCategorizationChatHandler:
    """
    Chat handler for QuickBooks transaction categorization
    
    This class manages the conversation flow for categorizing transactions,
    including suggesting categories, handling user confirmations, and applying
    changes to QuickBooks.
    """
    
    def __init__(self):
        self.pending_transactions = []
        self.current_tx = None
        self.current_batch = None
        self.llm_provider = "gemini"  # Default LLM
    
    def handle_message(self, req_context, user_message):
        """
        Process user message and generate response
        
        Args:
            req_context: Request context containing authentication info
            user_message: Message from the user
            
        Returns:
            Response to the user
        """
        # If we have pending transactions and user is responding to a suggestion
        if (self.current_tx or self.current_batch) and self._is_confirmation_response(user_message):
            return self._process_confirmation(req_context, user_message)
        
        # Check if user is asking for uncategorized transactions
        if self._is_asking_for_transactions(user_message):
            return self._fetch_and_suggest_transactions(req_context)
        
        # Check if user wants to switch LLM
        if self._is_switching_llm(user_message):
            return self._switch_llm(user_message)
        
        # Default response for other queries
        return self._handle_general_query(user_message)
    
    def _is_asking_for_transactions(self, message):
        """Check if user is asking for uncategorized transactions"""
        keywords = ["uncategorized", "new transaction", "categorize", "any transactions"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _is_confirmation_response(self, message):
        """Check if user is confirming or changing a category suggestion"""
        confirmation_words = ["yes", "ok", "correct", "accept", "good", "apply"]
        if any(word == message.lower() for word in confirmation_words):
            return True
        
        # Check if user is specifying a different category
        if "change" in message.lower() or "different" in message.lower() or "not " in message.lower():
            return True
        
        # Look for category names in the response
        common_categories = ["office", "meal", "travel", "rent", "utility", "service", "insurance", "marketing"]
        return any(category in message.lower() for category in common_categories)
    
    def _is_switching_llm(self, message):
        """Check if user wants to switch LLM"""
        keywords = ["use gemini", "use openai", "switch to gemini", "switch to openai", "reasoning model"]
        return any(keyword in message.lower() for keyword in keywords)
    
    def _switch_llm(self, message):
        """Switch LLM based on user request"""
        if "gemini" in message.lower():
            self.llm_provider = "gemini"
            return "I'll use Gemini for transaction categorization suggestions."
        elif "openai" in message.lower() or "gpt" in message.lower():
            self.llm_provider = "openai"
            return "I'll use OpenAI for transaction categorization suggestions."
        elif "reasoning" in message.lower():
            self.llm_provider = "reasoning"
            return "I'll use a reasoning model for transaction categorization suggestions."
        else:
            return f"I'm currently using {self.llm_provider}. Would you like to switch to a different model?"
    
    def _handle_general_query(self, message):
        """Handle general queries about the categorization process"""
        if "help" in message.lower():
            return (
                "I can help you categorize your QuickBooks transactions. Here's what you can do:\n\n"
                "- Ask for uncategorized transactions (e.g., 'Show me uncategorized transactions')\n"
                "- Accept suggested categories (e.g., 'Yes' or 'Accept')\n"
                "- Suggest different categories (e.g., 'Change to Office Supplies')\n"
                "- Switch LLM models (e.g., 'Use Gemini' or 'Use OpenAI')\n\n"
                "Would you like to see your uncategorized transactions now?"
            )
        elif any(word in message.lower() for word in ["how", "what", "process", "workflow"]):
            return (
                "The transaction categorization process works like this:\n\n"
                "1. I fetch uncategorized transactions from your QuickBooks account\n"
                "2. For each transaction, I suggest a category based on historical data\n"
                "3. Similar transactions are grouped together for batch categorization\n"
                "4. You can accept suggestions or provide different categories\n"
                "5. I update QuickBooks with your confirmed categories\n\n"
                "This helps reduce manual effort in your bookkeeping process. Would you like to start categorizing transactions now?"
            )
        else:
            return (
                "I'm your QuickBooks categorization assistant. I can help you categorize uncategorized transactions "
                "in your QuickBooks account. Type 'Any uncategorized transactions?' to get started or 'help' for more information."
            )
    
    def _fetch_and_suggest_transactions(self, req_context):
        """
        Fetch uncategorized transactions and suggest categories
        
        Args:
            req_context: Request context with authentication info
            
        Returns:
            Response with categorization suggestions
        """
        # Fetch uncategorized transactions
        self.pending_transactions = get_uncategorized_transactions(req_context, "This Calendar Year")
        
        if not self.pending_transactions:
            return "No uncategorized transactions found. Your books are up to date!"
        
        # Check for similar transactions for batch processing
        merchant_counts = {}
        for tx in self.pending_transactions:
            merchant = tx["merchant"]
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
        
        # If we have groups of similar transactions, suggest batch categorization
        batch_merchants = [m for m, count in merchant_counts.items() if count > 1]
        
        if batch_merchants:
            # Process the first batch
            merchant = batch_merchants[0]
            batch_txs = [tx for tx in self.pending_transactions if tx["merchant"] == merchant]
            
            # Get suggestion for this batch
            sample_tx = batch_txs[0]
            suggestion = suggest_category(req_context, sample_tx, self.llm_provider)
            
            # Format response with checkboxes for batch
            response = f"I found {len(batch_txs)} transactions from {merchant}.\n\n"
            response += f"Suggested category: **{suggestion['category']}**\n"
            response += f"Reason: {suggestion['reason']}\n\n"
            response += "Transactions:\n"
            
            for i, tx in enumerate(batch_txs):
                response += f"- [x] ${tx['amount']} on {tx['date']}\n"
            
            response += f"\nWould you like to categorize all these as **{suggestion['category']}**? Or suggest a different category."
            
            # Store pending batch
            self.current_batch = {
                "merchant": merchant,
                "transactions": batch_txs,
                "suggested_category": suggestion["category"]
            }
            
            return response
        else:
            # Process a single transaction
            tx = self.pending_transactions[0]
            
            # Get suggestion
            suggestion = suggest_category(req_context, tx, self.llm_provider)
            
            response = f"Transaction: {tx['merchant']} ${tx['amount']} on {tx['date']}\n"
            response += f"Suggested category: **{suggestion['category']}**\n"
            response += f"Reason: {suggestion['reason']}\n\n"
            response += "Accept this category or suggest a different one?"
            
            # Store current transaction
            self.current_tx = {
                "transaction": tx,
                "suggested_category": suggestion["category"]
            }
            
            return response
    
    def _process_confirmation(self, req_context, user_message):
        """
        Process user confirmation or category change
        
        Args:
            req_context: Request context with authentication info
            user_message: User message confirming or changing category
            
        Returns:
            Response after processing the confirmation
        """
        # Check if we're processing a batch or single transaction
        if self.current_batch:
            return self._process_batch_confirmation(req_context, user_message)
        elif self.current_tx:
            return self._process_single_confirmation(req_context, user_message)
        else:
            return "I'm not sure which transaction you're referring to. Can you ask about uncategorized transactions?"
    
    def _process_batch_confirmation(self, req_context, user_message):
        """Process batch confirmation"""
        batch = self.current_batch
        category = batch["suggested_category"]
        
        # Check if user is accepting the suggestion
        if self._is_accepting(user_message):
            # Apply category to all transactions in the batch
            for tx in batch["transactions"]:
                # Update each transaction
                categorize_transaction(req_context, tx["id"], category)
                
                # Remove from pending transactions
                self.pending_transactions = [p for p in self.pending_transactions if p["id"] != tx["id"]]
            
            response = f"Great! I've categorized all {len(batch['transactions'])} transactions from {batch['merchant']} as **{category}**."
            
            # Check if there are more transactions
            if self.pending_transactions:
                response += f"\n\nYou have {len(self.pending_transactions)} more transactions to categorize. Would you like to continue?"
            else:
                response += "\n\nAll transactions have been categorized. Is there anything else you'd like help with?"
            
            # Clear current batch
            self.current_batch = None
            
            return response
        else:
            # User wants a different category
            new_category = self._extract_category(user_message)
            
            if new_category:
                # Apply the new category to all transactions
                for tx in batch["transactions"]:
                    # Update each transaction
                    categorize_transaction(req_context, tx["id"], new_category)
                    
                    # Remove from pending transactions
                    self.pending_transactions = [p for p in self.pending_transactions if p["id"] != tx["id"]]
                
                response = f"I've categorized all {len(batch['transactions'])} transactions from {batch['merchant']} as **{new_category}**."
                
                # Check if there are more transactions
                if self.pending_transactions:
                    response += f"\n\nYou have {len(self.pending_transactions)} more transactions to categorize. Would you like to continue?"
                else:
                    response += "\n\nAll transactions have been categorized. Is there anything else you'd like help with?"
                
                # Clear current batch
                self.current_batch = None
                
                return response
            else:
                return "I didn't understand which category you want to use. Please specify a category from the available list or accept the suggested one."
    
    def _process_single_confirmation(self, req_context, user_message):
        """Process single transaction confirmation"""
        tx = self.current_tx["transaction"]
        suggested_category = self.current_tx["suggested_category"]
        
        # Check if user is accepting the suggestion
        if self._is_accepting(user_message):
            category = suggested_category
        else:
            # User wants a different category
            new_category = self._extract_category(user_message)
            
            if not new_category:
                return "I didn't understand which category you want to use. Please specify a category from the available list or accept the suggested one."
            
            category = new_category
        
        # Apply the category
        categorize_transaction(req_context, tx["id"], category)
        
        # Remove from pending transactions
        self.pending_transactions = [p for p in self.pending_transactions if p["id"] != tx["id"]]
        
        response = f"Transaction from {tx['merchant']} for ${tx['amount']} has been categorized as **{category}**."
        
        # Check if there are more transactions
        if self.pending_transactions:
            response += f"\n\nYou have {len(self.pending_transactions)} more transactions to categorize. Would you like to continue?"
        else:
            response += "\n\nAll transactions have been categorized. Is there anything else you'd like help with?"
        
        # Clear current transaction
        self.current_tx = None
        
        return response
    
    def _is_accepting(self, message):
        """Check if user is accepting the suggested category"""
        accept_words = ["yes", "ok", "sure", "accept", "good", "correct", "right", "that's right"]
        return any(word == message.lower() for word in accept_words)
    
    def _extract_category(self, message):
        """Extract category from user message"""
        # Common categories in QuickBooks
        categories = [
            "Office Supplies", "Meals & Entertainment", "Travel", "Rent",
            "Utilities", "Professional Services", "Insurance", "Marketing",
            "Maintenance", "Equipment", "Software", "Payroll", "Other"
        ]
        
        # Check for phrases like "change to X" or "use X"
        for phrase in ["change to", "use", "make it", "should be", "categorize as"]:
            if phrase in message.lower():
                remainder = message.lower().split(phrase, 1)[1].strip()
                for category in categories:
                    if category.lower() in remainder:
                        return category
        
        # Check for direct category mentions
        for category in categories:
            if category.lower() in message.lower():
                return category
            
            # Check for partial matches (e.g., "meals" for "Meals & Entertainment")
            key_term = category.split(" ")[0].lower()
            if key_term in message.lower():
                return category
        
        return None