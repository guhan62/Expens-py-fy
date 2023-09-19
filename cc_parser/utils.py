from .buckets import ALL_BUCKETS
from .constants import *
import glob, datetime, csv
from datetime import datetime as dt
from config import ExpenseManagerConstants
import hashlib

# _CCType : Return receiver for CCType
_CCType = Literal["AMEX", "BOFA", "DISCOVER", "CITI", "CASH"]

def get_hash(message :str):
    return hashlib.sha256(message.encode("utf-8")).hexdigest()

def findTxBucket(tx, bucket = ALL_BUCKETS) -> str:
    """Find Bucket for TX name """
    try:
        for bucket_name, entries in bucket.items():
            for entry in entries:
                if entry in tx['name']:
                    return bucket_name
    except Exception as e:
        return 'no-cat'
    else:
        return 'no-cat'

def groupTxInBuckets(tx_list, bucket = ALL_BUCKETS, cc_type: CCType = None):
    """Parse TX and group the list to buckets"""
    tx_bucket = { key : { 'total': 0.0, 'tx': [] } for key in bucket.keys() }
    tx_bucket['no-cat'] = { 'total': 0.0, 'tx': [] }
    
    for tx in tx_list:
        bucket_name = findTxBucket(tx, bucket)
        amount = float(tx['amount'])
        tx_bucket[bucket_name]['total'] += amount
        tx_bucket[bucket_name]['tx'].append( tx )
    return tx_bucket
    

def sort_tx_by_date(tx_list, date_field_idx = 0, reverse = False):
    """Sort TX dd/mm/yyyy Transaction list in Ascending order"""
    if type(tx_list[0]) == str:
        return sorted(tx_list, \
                  reverse = reverse,
                  key = lambda tx : \
                  (lambda dt : datetime.date(int(dt[2]), int(dt[0]), int(dt[1])))(tx.split(',')[date_field_idx].split("/")))
    return sorted(tx_list, \
                  reverse = reverse,
                  key = lambda tx : tx[date_field_idx] )


def sort_tx_by_cost(tx_list, cost_field_idx = 2, reverse = False):
    """Sort by Cost"""
    return sorted(tx_list, \
                  reverse = reverse,
                  key = lambda tx : float(tx.split(',')[cost_field_idx])
                )

# def dump_tx_to_csv(tx_list, header_column, final_path = f"TX_${datetime.datetime.now()}.csv"):
#     """Write TX to CSV"""
#     with open(final_path, 'w') as f:
#         writer = csv.writer(f)
#         writer.writerow(CCHeader.BOFA.split(","))
#         for tx in tx_list:
#             writer.writerow(tx.replace("\n","").replace("\"","").split(","))

def loadBankStatements(statement_path, slug = '*.csv') -> list[str]:
    """ Load Statements from folder """
    try:
        merged_tx = []    
        for filename in glob.glob(f"{statement_path}/{slug}", recursive=True):
            with open(filename, 'r') as f:
                filename = filename.lower()
                # print(f"Loading Filename ... {filename}")
                merged_tx.extend(f.readlines()[1:])
        return merged_tx
    except Exception as e:
        raise(e)

def loadStatements( all_expense_info : list[ExpenseInfo]) -> dict[_CCType, ExpenseStatements]:
    expenses = {}
    try:
        for expense_info in all_expense_info:
            expenses[expense_info['type']] = {
                'type': expense_info['type'],
                'statements': loadBankStatements(expense_info['path'])
            }
        return expenses
    except Exception as e:
        raise(e)


def parseDateString( date_string, formats = [r"%m/%d/%Y", r"%m/%d/%y"] ):
    for fmt in formats:
        try:
            parsed_dt = dt.strptime(date_string, fmt)
        except ValueError:
            pass
        else:
            return parsed_dt
    else:
        raise Exception(f"{date_string} do not match in {formats}")

def parseStatements( tx_list, credit_card_name: CCType ):
    """ Read Statements and group the transactions to a proccesable format """
    parsed_tx_list = []
    for tx in tx_list:
        tx = tx.replace("\n","")
        tx_date = tx_name = tx_amount = group = None
        if credit_card_name in [CCType.AMEX, CCType.CASH]:
            # Date,Description,Amount
            tx_date, tx_name, tx_amount = tx.split(",")
        elif credit_card_name == CCType.DISCOVER:
            # Trans. Date,Post Date,Description,Amount,Category
            _,tx_date,tx_name, tx_amount, group = tx.split(",")
        elif credit_card_name == CCType.BOFA:
            # Posted Date,Reference Number,Payee,Address,Amount
            tx_date,_,tx_name, _, tx_amount = tx.split(",")
            tx_amount = -float(tx_amount)
        elif credit_card_name == CCType.CITI:
            # Status,Date,Description,Debit,Credit
            _,tx_date,tx_name, debit_amount, credit_amount = tx.split(",")
            tx_amount = float(debit_amount if debit_amount else credit_amount)

        parsed_tx_list.append({ 'date': tx_date, 'name': tx_name, "amount": tx_amount, "card": credit_card_name })
    return parsed_tx_list

def mergeCardBuckets(card_buckets: list[dict], filter_buckets = [], build_tuples = False):
    """Pass all buckets in List"""
    merged_tx = []
    merged_buckets = { key : { 'total': 0.0, 'tx': [] } for key in ALL_BUCKETS.keys() }
    merged_buckets['no-cat'] = { 'total': 0.0, 'tx': [] }
    for card_bucket in card_buckets:
        for bucket_name, bucket  in card_bucket.items():
            if bucket_name in filter_buckets:
                continue
            if build_tuples:
                merged_tx.extend( list(map(lambda tx: [*tx.values(), bucket_name], bucket['tx'])) )
            else:
                merged_tx.extend( list(map(lambda tx: "{date},{name},{amount},{card},".format(**tx) + bucket_name, bucket['tx'])) )
            merged_buckets[bucket_name]['total'] += bucket['total']
            merged_buckets[bucket_name]['tx'].extend( bucket['tx'] )
    
    if build_tuples:
        for i in range(len(merged_tx)):
            merged_tx[i][0] = parseDateString(merged_tx[i][0])
            merged_tx[i][2] = float(merged_tx[i][2])
    return merged_buckets, merged_tx
    
def sliceTxByDate(merged_tx: list[list], filter_date: str):
    filter_date = parseDateString(filter_date)
    return list(filter(lambda tx: tx[0] >= filter_date,merged_tx))

def formatTxTuples(merged_tx: list[list]):
    """Format Tx Tuples to Merged format"""
    # MERGED = "Date,Description,Amount,Card,Bucket,Split,Comments"
    for i in range(len(merged_tx)):
        merged_tx[i][0] = dt.strftime(merged_tx[i][0], "%m/%d/%Y")
        merged_tx[i][1] = merged_tx[i][1].replace('"', '')
        merged_tx[i][2] = str(merged_tx[i][2])
        # Default Personal Statement : Refer migrations SPLIT_LABEL schema for Values
        merged_tx[i].append('1')
        # Default Comment
        merged_tx[i].append('NULL')
        # merged_tx[i] = ','.join(merged_tx[i])
    return merged_tx

def generateHashes(tx_list: list[list[any]]):
    for tx in tx_list:
        if type(tx) == str:
            tx = tx.split(',')
        tx.append(get_hash(','.join(tx[:4])))
    return tx_list

def removeWindowsDelimeter(csv_lines: list[str]):
    return [tx.replace('\r\n','').split(',') for tx in csv_lines]

def readCSV(filename = 'tx.csv', add_hashes = False):
    # Create File if file does not exist
    try:
        with open(filename, 'x'):
            print(f"{filename} created")
    except FileExistsError:
        pass
    # Replace Windows Delims
    with open(filename, 'r', newline='',encoding='utf-8') as csvfile:
        if not add_hashes:
            return removeWindowsDelimeter(csvfile.readlines())
        return generateHashes( removeWindowsDelimeter(csvfile.readlines()) )


def saveToCSV(tx_list: list[str], filename = f"tx_{dt.today().date().strftime(r'%m_%d')}.csv"):
    # Find Existing Hashes from the CSV
    tx_hashes = set()
    # Read Existing Files with Hashes
    saved_tx_list = readCSV(filename, True)
    # Store Hashes to prevent Dupes
    tx_hashes = set([ tx[-1] for tx in saved_tx_list ])
    # Write New Tuples to CSV
    with open(filename, 'a', newline='',encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        for tx in tx_list:
            if not get_hash(','.join(tx[:4])) in tx_hashes:
                writer.writerow(tx)