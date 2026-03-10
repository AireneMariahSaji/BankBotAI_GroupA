"""
Cassandra Bank - Banking Library
Provides access to customer, account, loan, and card data
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class BankingLibrary:
    """Central banking database and query interface"""
    
    def __init__(self):
        """Initialize with banking data"""
        self.data = {
            "bank_info": {
                "name": "Cassandra Bank",
                "branch": "Mumbai Main Branch",
                "ifsc": "CASS0001234",
                "customer_support": "1-800-BANKBOT",
                "email": "support@cassandrabank.com"
            },
            "customers": [
                {
                    "customer_id": "CUST001",
                    "name": "Lizy Roy",
                    "phone": "9876543210",
                    "email": "lizyr@gmail.com",
                    "accounts": ["ACC001"],
                    "cards": ["CARD001"],
                    "loans": ["LOAN001"]
                },
                {
                    "customer_id": "CUST002",
                    "name": "Priya Nair",
                    "phone": "9123456780",
                    "email": "priya@gmail.com",
                    "accounts": ["ACC002"],
                    "cards": ["CARD002"],
                    "loans": []
                },
                {
                    "customer_id": "CUST003",
                    "name": "Arjun Patel",
                    "phone": "9988776655",
                    "email": "arjun@gmail.com",
                    "accounts": ["ACC003"],
                    "cards": [],
                    "loans": ["LOAN002"]
                },
                {
                    "customer_id": "CUST004",
                    "name": "Sneha Reddy",
                    "phone": "9871234560",
                    "email": "sneha@gmail.com",
                    "accounts": ["ACC004"],
                    "cards": ["CARD003"],
                    "loans": []
                },
                {
                    "customer_id": "CUST005",
                    "name": "Vikram Singh",
                    "phone": "9012345678",
                    "email": "vikram@gmail.com",
                    "accounts": ["ACC005"],
                    "cards": ["CARD004"],
                    "loans": ["LOAN003"]
                }
            ],
            "accounts": [
                {
                    "account_number": "ACC001",
                    "customer_id": "CUST001",
                    "account_type": "Savings",
                    "balance": 25000,
                    "minimum_balance": 1000,
                    "interest_rate": 4.0,
                    "status": "Active",
                    "transactions": [
                        {"type": "deposit", "amount": 5000, "date": "2026-02-10"},
                        {"type": "withdrawal", "amount": 2000, "date": "2026-02-15"}
                    ]
                },
                {
                    "account_number": "ACC002",
                    "customer_id": "CUST002",
                    "account_type": "Current",
                    "balance": 80000,
                    "minimum_balance": 5000,
                    "interest_rate": 0.0,
                    "status": "Active",
                    "transactions": [
                        {"type": "deposit", "amount": 10000, "date": "2026-02-05"},
                        {"type": "transfer", "amount": 5000, "date": "2026-02-20"}
                    ]
                },
                {
                    "account_number": "ACC003",
                    "customer_id": "CUST003",
                    "account_type": "Savings",
                    "balance": 15000,
                    "minimum_balance": 1000,
                    "interest_rate": 4.0,
                    "status": "Active",
                    "transactions": [
                        {"type": "deposit", "amount": 7000, "date": "2026-01-15"},
                        {"type": "withdrawal", "amount": 1000, "date": "2026-02-01"}
                    ]
                },
                {
                    "account_number": "ACC004",
                    "customer_id": "CUST004",
                    "account_type": "Savings",
                    "balance": 42000,
                    "minimum_balance": 1000,
                    "interest_rate": 4.0,
                    "status": "Active",
                    "transactions": [
                        {"type": "deposit", "amount": 12000, "date": "2026-01-10"},
                        {"type": "withdrawal", "amount": 3000, "date": "2026-02-18"}
                    ]
                },
                {
                    "account_number": "ACC005",
                    "customer_id": "CUST005",
                    "account_type": "Savings",
                    "balance": 67000,
                    "minimum_balance": 1000,
                    "interest_rate": 4.0,
                    "status": "Active",
                    "transactions": [
                        {"type": "deposit", "amount": 20000, "date": "2026-02-08"},
                        {"type": "transfer", "amount": 5000, "date": "2026-02-22"}
                    ]
                }
            ],
            "loans": [
                {
                    "loan_id": "LOAN001",
                    "customer_id": "CUST001",
                    "loan_type": "Personal Loan",
                    "amount": 100000,
                    "interest_rate": 10.0,
                    "tenure_years": 3,
                    "remaining_balance": 75000,
                    "status": "Active",
                    "monthly_emi": 3217
                },
                {
                    "loan_id": "LOAN002",
                    "customer_id": "CUST003",
                    "loan_type": "Education Loan",
                    "amount": 300000,
                    "interest_rate": 9.0,
                    "tenure_years": 5,
                    "remaining_balance": 250000,
                    "status": "Active",
                    "monthly_emi": 6283
                },
                {
                    "loan_id": "LOAN003",
                    "customer_id": "CUST005",
                    "loan_type": "Home Loan",
                    "amount": 2000000,
                    "interest_rate": 8.5,
                    "tenure_years": 20,
                    "remaining_balance": 1800000,
                    "status": "Active",
                    "monthly_emi": 17000
                }
            ],
            "cards": [
                {
                    "card_id": "CARD001",
                    "customer_id": "CUST001",
                    "card_type": "Debit Card",
                    "card_number": "1234-5678-1111-2222",
                    "expiry": "12/28",
                    "status": "Active",
                    "daily_limit": 50000
                },
                {
                    "card_id": "CARD002",
                    "customer_id": "CUST002",
                    "card_type": "Credit Card",
                    "card_number": "1234-5678-3333-4444",
                    "expiry": "11/27",
                    "status": "Active",
                    "credit_limit": 500000,
                    "current_balance": 125000
                },
                {
                    "card_id": "CARD003",
                    "customer_id": "CUST004",
                    "card_type": "Debit Card",
                    "card_number": "1234-5678-5555-6666",
                    "expiry": "10/29",
                    "status": "Active",
                    "daily_limit": 50000
                },
                {
                    "card_id": "CARD004",
                    "customer_id": "CUST005",
                    "card_type": "Credit Card",
                    "card_number": "1234-5678-7777-8888",
                    "expiry": "09/28",
                    "status": "Active",
                    "credit_limit": 1000000,
                    "current_balance": 350000
                }
            ],
            "services": {
                "account_services": [
                    "Balance check",
                    "Mini statement",
                    "Money transfer",
                    "Account closure",
                    "Duplicate passbook"
                ],
                "loan_services": [
                    "Apply loan",
                    "Pay EMI",
                    "Loan status check",
                    "EMI modification",
                    "Early repayment"
                ],
                "card_services": [
                    "Block card",
                    "Replace card",
                    "Change PIN",
                    "Card limit modification",
                    "Contactless payment"
                ],
                "online_services": [
                    "Net banking",
                    "Mobile banking",
                    "UPI transfer",
                    "Bill payment",
                    "Scheduled transfers"
                ]
            }
        }
    
    # ─── Customer Queries ───
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer details by ID"""
        for customer in self.data["customers"]:
            if customer["customer_id"] == customer_id:
                return customer
        return None
    
    def get_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get customer by name (case-insensitive)"""
        for customer in self.data["customers"]:
            if customer["name"].lower() == name.lower():
                return customer
        return None
    
    def search_customers(self, keyword: str) -> List[Dict]:
        """Search customers by name or email"""
        results = []
        keyword_lower = keyword.lower()
        for customer in self.data["customers"]:
            if (keyword_lower in customer["name"].lower() or 
                keyword_lower in customer["email"].lower()):
                results.append(customer)
        return results
    
    # ─── Account Queries ───
    def get_account(self, account_number: str) -> Optional[Dict]:
        """Get account details"""
        for account in self.data["accounts"]:
            if account["account_number"] == account_number:
                return account
        return None
    
    def get_customer_accounts(self, customer_id: str) -> List[Dict]:
        """Get all accounts for a customer"""
        accounts = []
        for account in self.data["accounts"]:
            if account["customer_id"] == customer_id:
                accounts.append(account)
        return accounts
    
    def get_account_balance(self, account_number: str) -> Optional[float]:
        """Get account balance"""
        account = self.get_account(account_number)
        return account["balance"] if account else None
    
    def get_account_transactions(self, account_number: str, limit: int = 10) -> List[Dict]:
        """Get recent transactions for an account"""
        account = self.get_account(account_number)
        if account:
            return account["transactions"][-limit:]
        return []
    
    def get_accounts_by_type(self, account_type: str) -> List[Dict]:
        """Get all accounts of a specific type"""
        return [acc for acc in self.data["accounts"] if acc["account_type"] == account_type]
    
    # ─── Loan Queries ───
    def get_loan(self, loan_id: str) -> Optional[Dict]:
        """Get loan details"""
        for loan in self.data["loans"]:
            if loan["loan_id"] == loan_id:
                return loan
        return None
    
    def get_customer_loans(self, customer_id: str) -> List[Dict]:
        """Get all loans for a customer"""
        loans = []
        for loan in self.data["loans"]:
            if loan["customer_id"] == customer_id:
                loans.append(loan)
        return loans
    
    def get_loans_by_type(self, loan_type: str) -> List[Dict]:
        """Get all loans of a specific type"""
        return [loan for loan in self.data["loans"] if loan["loan_type"] == loan_type]
    
    def calculate_loan_details(self, loan_id: str) -> Optional[Dict]:
        """Calculate loan EMI and repayment details"""
        loan = self.get_loan(loan_id)
        if not loan:
            return None
        
        remaining_months = loan["tenure_years"] * 12
        monthly_rate = loan["interest_rate"] / 100 / 12
        emi = loan["remaining_balance"] * monthly_rate / (1 - (1 + monthly_rate) ** -remaining_months)
        
        return {
            "loan_id": loan_id,
            "remaining_balance": loan["remaining_balance"],
            "monthly_emi": round(emi, 2),
            "remaining_months": remaining_months,
            "total_repayment": round(emi * remaining_months, 2)
        }
    
    # ─── Card Queries ───
    def get_card(self, card_id: str) -> Optional[Dict]:
        """Get card details"""
        for card in self.data["cards"]:
            if card["card_id"] == card_id:
                return card
        return None
    
    def get_customer_cards(self, customer_id: str) -> List[Dict]:
        """Get all cards for a customer"""
        cards = []
        for card in self.data["cards"]:
            if card["customer_id"] == customer_id:
                cards.append(card)
        return cards
    
    def get_cards_by_type(self, card_type: str) -> List[Dict]:
        """Get all cards of a specific type"""
        return [card for card in self.data["cards"] if card["card_type"] == card_type]
    
    # ─── Service Information ───
    def get_available_services(self, service_category: str) -> Optional[List[str]]:
        """Get available services in a category"""
        return self.data["services"].get(service_category)
    
    def get_all_services(self) -> Dict:
        """Get all available services"""
        return self.data["services"]
    
    # ─── Bank Info ───
    def get_bank_info(self) -> Dict:
        """Get bank information"""
        return self.data["bank_info"]
    
    def get_support_contact(self) -> str:
        """Get customer support contact"""
        return self.data["bank_info"]["customer_support"]
    
    # ─── Contextual Query ───
    def search_relevant_data(self, query: str) -> Dict[str, Any]:
        """
        Search for relevant data based on query keywords.
        Returns a dictionary with relevant banking information.
        """
        query_lower = query.lower()
        results = {
            "customers": [],
            "accounts": [],
            "loans": [],
            "cards": [],
            "services": [],
            "bank_info": None
        }
        
        # Search customers
        if any(word in query_lower for word in ["customer", "account holder", "name", "who is"]):
            for customer in self.data["customers"]:
                if (query_lower in customer["name"].lower() or 
                    customer["name"].lower() in query_lower):
                    results["customers"].append(customer)
        
        # Search accounts
        if any(word in query_lower for word in ["account", "balance", "savings", "current", "acc"]):
            for account in self.data["accounts"]:
                if (account["account_number"].lower() in query_lower or
                    account["account_type"].lower() in query_lower):
                    results["accounts"].append(account)
        
        # Search loans
        if any(word in query_lower for word in ["loan", "emi", "personal", "home", "education"]):
            for loan in self.data["loans"]:
                if (loan["loan_id"].lower() in query_lower or
                    loan["loan_type"].lower() in query_lower or
                    "loan" in query_lower):
                    results["loans"].append(loan)
        
        # Search cards
        if any(word in query_lower for word in ["card", "debit", "credit", "plastic"]):
            for card in self.data["cards"]:
                if (card["card_id"].lower() in query_lower or
                    card["card_type"].lower() in query_lower or
                    "card" in query_lower):
                    results["cards"].append(card)
        
        # Search services
        if any(word in query_lower for word in ["service", "transfer", "payment", "apply"]):
            for category, services in self.data["services"].items():
                for service in services:
                    if service.lower() in query_lower:
                        results["services"].append({"category": category, "service": service})
        
        # Include bank info if asking about it
        if any(word in query_lower for word in ["bank", "branch", "support", "contact", "ifsc"]):
            results["bank_info"] = self.data["bank_info"]
        
        return results
    
    def format_search_results(self, results: Dict[str, Any]) -> str:
        """Format search results into readable text"""
        output = []
        
        if results["customers"]:
            output.append("**Customers Found:**")
            for customer in results["customers"]:
                output.append(f"- {customer['name']} ({customer['customer_id']}): {customer['email']}")
        
        if results["accounts"]:
            output.append("\n**Accounts Found:**")
            for account in results["accounts"]:
                output.append(f"- {account['account_type']} Account ({account['account_number']}): ₹{account['balance']:,} (Status: {account['status']})")
        
        if results["loans"]:
            output.append("\n**Loans Found:**")
            for loan in results["loans"]:
                output.append(f"- {loan['loan_type']} ({loan['loan_id']}): ₹{loan['remaining_balance']:,} remaining @ {loan['interest_rate']}% APR")
        
        if results["cards"]:
            output.append("\n**Cards Found:**")
            for card in results["cards"]:
                output.append(f"- {card['card_type']} ({card['card_id']}): Expires {card['expiry']} (Status: {card['status']})")
        
        if results["services"]:
            output.append("\n**Services Found:**")
            for service in results["services"]:
                output.append(f"- {service['service']} ({service['category']})")
        
        if results["bank_info"]:
            info = results["bank_info"]
            output.append(f"\n**Bank Information:**\n- Name: {info['name']}\n- Branch: {info['branch']}\n- IFSC: {info['ifsc']}\n- Support: {info['customer_support']}")
        
        return "\n".join(output) if output else ""
