import unittest
from csv import writer as csv_writer
from os import remove as os_remove
from cc_parser.constants import CCHeader
from cc_parser.utils import saveToCSV, readCSV, get_hash
from cc_parser.db import DBLite
import json


class TestTxReadWrite(unittest.TestCase):

    def setUp(self) -> None:
        self.test_file_name = 'test_tx.csv'
        self.test_db_name = 'test_expenses.sqlite3'
        # Formatted Transaction
        self.merged_tx = [
            ['04/25/2023', 'Valdez-Martin', '372.45', 'BOFA', 'misc', '1', 'NULL'],
            ['01/24/2023', 'Williams Campbell and Allen 3', '594.59', 'AMEX', 'entertainment', '2', 'NULL'],
            ['09/28/2022', 'Olson-Smith', '8742.08', 'DISCOVER', 'shopping', '3', 'NULL'],
            ['04/25/2023', 'Patterson PLC', '3.77', 'CITI', 'shopping', '4', 'NULL'],
            ['07/13/2023', 'Navarro Inc', '660.75', 'CASH', 'education', '5', 'NULL', '620.45']
        ]
        self.db = DBLite(self.test_db_name)
        file = open(self.test_file_name, 'w+')
        writer = csv_writer(file)
        # Write First ROW to CSV
        writer.writerows( self.merged_tx[:2] )
        file.close()
        # DB Seed
        self.db.migrationsUp()
        # CleanUp files after Test
        self.addCleanup(os_remove, self.test_file_name)
        self.addCleanup(os_remove, self.test_db_name)

    def test_tx_hash(self):
        tx = ['04/25/2023', 'Valdez-Martin', '372.45', 'BOFA', 'misc', '1', 'NULL']
        self.assertEqual( get_hash(','.join(tx[:4])) , '69842b8eba775b9d4bca249e13dd484e0af0b4081c5169e6cd181a07654835c1' )

    def test_tx_no_dupe_to_csv(self):
        saveToCSV(self.merged_tx, self.test_file_name)
        merged_tx = readCSV(self.test_file_name)
        self.assertEqual(len(self.merged_tx), len(merged_tx))
    
    def test_db_new(self):
        # New DB
        tx_result = self.db.getAllTransactions()
        self.assertEqual(tx_result, [])
    
    def test_db_dupe_tx(self):
        # Single TX, dupes are blocked by _hash
        self.db.insertTxList([self.merged_tx[0]])
        self.db.insertTxList([self.merged_tx[0]])
        tx_result = self.db.getAllTransactions()
        self.assertEqual(len(tx_result), 1)
    
    def test_db_partial_split(self):
        bad_split_tx = ['07/13/2023', 'Navarro Inc', '660.75', 'CASH', 'education', '5', 'NULL']
        self.assertRaisesRegex(Exception, 'Split Amount not entered after comments in CSV; Expect 8 values in CSV',  self.db.insertTxList, [bad_split_tx])
        # tx = self.db.runQuery("SELECT * from SPLIT_LABEL", 'fetchall')
        good_split_tx = ['07/13/2023', 'Navarro Inc', '660.75', 'CASH', 'education', '5', 'NULL', '620.45']
        self.db.insertTxList([ good_split_tx ])
        tx_dict = dict(zip(CCHeader.MERGED.split(',') + ['Original_Amount'] , good_split_tx))
        tx = self.db.getPaymentsBySplitLabel('PARTIAL_SPLIT', False)
        self.assertEqual(len(tx), 1)
        tx = tx[0]
        self.assertEqual(str(tx['Original_Amount']), tx_dict['Original_Amount'])
        self.assertEqual(str(tx['Amount']), tx_dict['Amount'])
        self.assertEqual(str(tx['Description']), tx_dict['Description'])
        # Date Validation
        from datetime import datetime as dt
        self.assertEqual(tx['Date'], dt.strptime(tx_dict['Date'], r'%m/%d/%Y').strftime('%Y-%m-%d'))
        # Comments
        self.assertEqual(tx['Comments'], DBLite.buildSplitComment(tx_dict['Original_Amount'], tx_dict['Amount']))

    def test_db_non_split(self):
        self.db.insertTxList(self.merged_tx)
        tx_result = self.db.getAllTransactions()
        self.assertEqual(len(tx_result), len(self.merged_tx))
        tx_result = self.db.getNonSplitPayments()
        non_split_count = len(list(filter(lambda tx: ['1', '2'].count(tx[-2]) == 0  ,self.merged_tx)))
        self.assertEqual( non_split_count, 3 )
        self.assertEqual( len(tx_result), non_split_count )
        tx_dict = dict(zip(CCHeader.MERGED.split(',') , self.merged_tx[2]))
        for key in ['Amount', 'Description']:
            self.assertEqual( tx_dict[key],  str(tx_result[0][key]) )

if __name__ == '__main__':
    unittest.main()