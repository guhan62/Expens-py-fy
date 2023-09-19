from cc_parser.constants import CCHeader, CCType
from faker import Faker
import re

# Faker Object
Faker.seed(10)
fake = Faker()

def matchStringPatterns(target: str, patterns: [str]):
    return any(list(map( lambda pattern: target.find(pattern) != -1, patterns )))




def generateMockTransactions( credit_card_type: CCType, transaction_count = 10 ):
    """Build Mock Transactions based on Credit Card Type"""
    transactions = []
    fake = Faker()
    headers = getattr(CCHeader, credit_card_type).split(',')
    for _ in range(transaction_count):
        single_tx = ''
        for header in headers:
            print(header)
            if 'date' in header.lower():
                single_tx += fake.date_between('-1y').strftime(r"%m/%d/%Y") + ','
            elif matchStringPatterns(header.lower(), ['description', 'payee']):
                single_tx += fake.company().replace(',', ' ') + ','
            elif matchStringPatterns(header.lower(), ["amount", "debit", "credit"]):
                # Bofa TX has '-{amount}' in statements
                if credit_card_type == CCType.BOFA:
                    single_tx += "-"
                # Faker pricetag generates random flaot price with `$,` ~ `$10,123.123`
                single_tx += re.sub("[$,]", '', fake.pricetag().replace('$,', '')) + ','
            elif matchStringPatterns(header.lower(), ["address"]):
                single_tx += fake.street_address().replace(',', ' ') + ','
            elif matchStringPatterns(header.lower(), ["category"]):
                single_tx += 'Merchandise,'
            elif matchStringPatterns(header.lower(), ["status"]):
                single_tx += 'Cleared,'
            elif matchStringPatterns(header.lower(), ["reference"]):
                single_tx += f'{fake.sbn9()},'
        # Remove the last column
        transactions.append(single_tx[:-1])
    return transactions


# bofa_tx = generateMockTransactions( CCType.BOFA )
# amex_tx = generateMockTransactions( CCType.AMEX )
# discover_tx = generateMockTransactions( CCType.DISCOVER )
# citi_tx = generateMockTransactions( CCType.CITI )
# cash_tx = generateMockTransactions( CCType.CASH )

simple_transactions_all = {
    'BOFA': '04/25/2023,06-790377-5,Valdez-Martin,1350 Dalton Rapids Suite 664,-372.45',
    'AMEX': '01/24/2023,Williams Campbell and Allen 3,594.59',
    'DISCOVER': '04/25/2023,09/28/2022,Olson-Smith,8742.08,Merchandise',
    'CITI': 'Cleared,04/25/2023,Patterson PLC,3.77,620.87',
    'CASH': '07/13/2023,Navarro Inc,660.75',
}

parsed_transactions_all = {
    'BOFA': {'statements': [{'date': '04/25/2023', 'name': 'Valdez-Martin', 'amount': 372.45, 'card': 'BOFA'}]}, 
    'AMEX': {'statements': [{'date': '01/24/2023', 'name': 'Williams Campbell and Allen 3', 'amount': '594.59', 'card': 'AMEX'}]}, 
    'DISCOVER': {'statements': [{'date': '09/28/2022', 'name': 'Olson-Smith', 'amount': '8742.08', 'card': 'DISCOVER'}]}, 
    'CITI': {'statements': [{'date': '04/25/2023', 'name': 'Patterson PLC', 'amount': 3.77, 'card': 'CITI'}]}, 
    'CASH': {'statements': [{'date': '07/13/2023', 'name': 'Navarro Inc', 'amount': '660.75', 'card': 'CASH'}]}
}

bucketed_transactions_all = {
    'education': {'total': 660.75, 'tx': [{'date': '07/13/2023', 'name': 'Navarro Inc', 'amount': '660.75', 'card': 'CASH'}]},
    'shopping': {'total': 8745.85, 'tx': [{'date': '09/28/2022', 'name': 'Olson-Smith', 'amount': '8742.08', 'card': 'DISCOVER'}, {'date': '04/25/2023', 'name': 'Patterson PLC', 'amount': 3.77, 'card': 'CITI'}]},
    'entertainment': {'total': 594.59, 'tx': [{'date': '01/24/2023', 'name': 'Williams Campbell and Allen 3', 'amount': '594.59', 'card': 'AMEX'}]},
    'misc': {'total': 372.45, 'tx': [{'date': '04/25/2023', 'name': 'Valdez-Martin', 'amount': 372.45, 'card': 'BOFA'}]},
    'travel': {'total': 0.0, 'tx': []}, 'eshopping': {'total': 0.0, 'tx': []}, 'market': {'total': 0.0, 'tx': []},
    'repayments': {'total': 0.0, 'tx': []}, 'fees': {'total': 0.0, 'tx': []}, 'games': {'total': 0.0, 'tx': []},
    'fuel': {'total': 0.0, 'tx': []}, 'food': {'total': 0.0, 'tx': []}, 'refund': {'total': 0.0, 'tx': []},
    'internet': {'total': 0.0, 'tx': []}, 'health': {'total': 0.0, 'tx': []}, 'personal': {'total': 0.0, 'tx': []},
    'auto': {'total': 0.0, 'tx': []}, 'insurance': {'total': 0.0, 'tx': []}, 'no-cat': {'total': 0.0, 'tx': []}
}

simple_buckets = {
    'education': ['Navarro'],
    'shopping': ['Patterson', 'Olson'],
    'entertainment': ['Williams'],
    'misc': ['Martin'],
}