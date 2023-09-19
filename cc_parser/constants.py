from typing import TypedDict, Literal

# from enum import Enum
class CCType:
    AMEX = "AMEX"
    BOFA = "BOFA"
    DISCOVER = "DISCOVER"
    CITI="CITI"
    CASH="CASH"

# ExpenseInfo : Interface for config setup
class ExpenseInfo(TypedDict):
    type: CCType
    path: str

# ExpenseStatements: Interface load statements and type after setup
class ExpenseStatements(TypedDict):
    type: CCType
    statements: list[str]
    bucket: dict


class CCHeader:
    BOFA = "Posted Date,Reference Number,Payee,Address,Amount"
    AMEX = "Date,Description,Amount"
    DISCOVER = "Trans. Date,Post Date,Description,Amount,Category"
    CITI="Status,Date,Description,Debit,Credit"
    CASH = "Date,Description,Amount"
    MERGED = "Date,Description,Amount,Card,Bucket,Split,Comments"

