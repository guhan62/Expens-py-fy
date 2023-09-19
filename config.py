from cc_parser.constants import CCType
from os import getenv

class ExpenseManagerConstants:
    SPLITWISE_API_KEY = getenv("SPLITWISE_API_KEY")
    SPLITWISE_GROUP_ID = getenv("SPLITWISE_GROUP_ID")
    EXPENSE_STATEMENT_PATHS =  [
        { "type": CCType.AMEX, "path": "Statements/AMEX" },
        { "type": CCType.BOFA, "path": "Statements/BOFA" },
        { "type": CCType.DISCOVER, "path": "Statements/DISCOVER" },
        { "type": CCType.CITI, "path": "Statements/CITI" },
        { "type": CCType.CASH, "path": "Statements/CASH" }
    ]
    STATEMENT_EXTENSION = "*.csv"
    EXPENSE_DB_NAME = 'expenses.sqlite3'