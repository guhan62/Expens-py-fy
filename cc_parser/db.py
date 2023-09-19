from contextlib import closing
import sqlite3, json
from os import path as os_path
from datetime import datetime as dt
from cc_parser.utils import *
from splitwise.categorizer import BUCKET_2_SPLIT
from config import ExpenseManagerConstants

class DBLite:
    def __init__(self, DB_NAME = ExpenseManagerConstants.EXPENSE_DB_NAME):
        self.DB_NAME = DB_NAME
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.DB_NAME)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            raise(e)

    def migrationsUp(self):
        try:
            with open('./migrations/create.sql') as create_sql:
                with closing(self.conn.cursor()) as cursor:
                    queries = create_sql.read().split(';')
                    for query in queries:
                        cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            raise(e)

    def runQuery(self, query: str, callback = None, to_json = False):
        try:
            with closing(self.conn.cursor()) as cursor:
                raw_result = cursor.execute(query)
                result = getattr(raw_result, callback)() if callback else raw_result
                if to_json:
                    return json.dumps([ dict(row) for row in result ])
                return result
        except Exception as e:
            raise(e)

    @staticmethod
    def buildSplitComment(total, amount_to_split):
        return f" ; Original:{total}$ > AmountToBeSplit:{amount_to_split}$"

    def insertTxList(self, tx_list = []):
        if type(tx_list) != list:
            raise Exception('Parameter Error: Pass list<list<str>>')
        with closing(self.conn.cursor()) as cursor:
            for tx in tx_list:
                _hash = get_hash(','.join(tx[:4]))
                payId = self.getPayType(tx[3])
                _date = parseDateString(tx[0]).strftime('%Y-%m-%d')
                _title = tx[1].replace('\'', '')
                _comment = '' if tx[6] in [None, 'NULL'] else tx[6]
                _split_amount = float(tx[2])
                _total_amount = float(tx[2])
                if tx[5] == '5':
                    if(len(tx) != 8):
                        raise Exception('Split Amount not entered after comments in CSV; Expect 8 values in CSV')
                    _total_amount = float(tx[-1])
                    _comment += f"{DBLite.buildSplitComment(_total_amount, _split_amount)}"
                if self.isTxSaved(_hash) == 0:
                    insert_prepare_stmt = f"""
                        insert into EXPENSES(
                            HASH, Date, Description,
                            Amount, Original_Amount, Pay_Id,
                            Category,Split_Id,Splitwise_Label,
                            Comments
                        )
                        VALUES('{_hash}', '{_date}', '{_title}', 
                        {_split_amount}, {_total_amount}, {payId}, 
                        '{tx[4]}', {tx[5]}, {BUCKET_2_SPLIT[tx[4]]},
                        '{_comment}')
                    """      
                    try:
                        cursor.execute(insert_prepare_stmt)
                    except Exception as e:
                        raise(e)
            cursor.close()
        self.conn.commit()
        
    def getPayType(self, pay_label):
        with closing(self.conn.cursor()) as cursor:
            try:
                [pay_id] = cursor.execute(f"select PL.Id from PAY_LABEL PL where PL.Description = '{pay_label}'").fetchone()
                return pay_id
            except:
                return 1
    
    def isTxSaved(self, _hash):
        with closing(self.conn.cursor()) as cursor:
            [count] = cursor.execute(f"select count(*) as count from EXPENSES E where E.HASH = '{_hash}'").fetchone()
            cursor.close()
            return count
    
    def getNonSplitPayments(self):
        with closing(self.conn.cursor()) as cursor:
            payments = cursor.execute("""
            select e.Id, e.HASH , e.Date, e.Description , e.Category, e.Amount, e.Original_Amount, e.Comments ,pl.Description, sl.Description, e.Splitwise_Label
	            from EXPENSES e 
	            INNER join SPLIT_LABEL sl on e.Split_Id = sl.Id
	            INNER join  PAY_LABEL pl on e.Pay_Id = pl.Id
            where e.Split_Id NOT IN ('1','2') ORDER BY e.Date;
            """).fetchall()
            cursor.close()
            return payments
        
    def getPaymentsBySplitLabel(self, split_description: str, to_json = False):
        return self.runQuery(f"""
            select e.Id, e.HASH , e.Date, e.Description , e.Category, e.Amount, e.Original_Amount, e.Comments ,pl.Description, sl.Description, e.Splitwise_Label
	            from EXPENSES e 
	            INNER join SPLIT_LABEL sl on e.Split_Id = sl.Id
	            INNER join PAY_LABEL pl on e.Pay_Id = pl.Id
            where sl.Id = (select Id from SPLIT_LABEL where Description = "{split_description}") ORDER BY e.Date;
        """, "fetchall", to_json)
        
    def getAllTransactions(self):
        with closing(self.conn.cursor()) as cursor:
            payments = cursor.execute("""
            select e.Id, e.HASH , e.Date, e.Description , e.Category, e.Amount, e.Original_Amount, e.Comments ,pl.Description, sl.Description, e.Splitwise_Label
	            from EXPENSES e 
	            INNER join SPLIT_LABEL sl on e.Split_Id = sl.Id
	            INNER join  PAY_LABEL pl on e.Pay_Id = pl.Id
            ORDER BY e.Date;
            """).fetchall()
            cursor.close()
            return payments
    
    def updateTx(self, id, _hash, splitwise_id):
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute(f"""
                    UPDATE EXPENSES SET 
                        Splitwise_Id={splitwise_id},
                        Split_Id='2'
                    where
                        HASH='{_hash}'
                    and
                        Id={id};
                """)
                cursor.close()
            self.conn.commit()
        except Exception as e:
            raise(e)

    
    def close(self):
        self.conn.close()