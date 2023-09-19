import unittest
from .fixtures.transactions import simple_transactions_all, simple_buckets, parsed_transactions_all, bucketed_transactions_all
from cc_parser.utils import parseStatements, groupTxInBuckets, mergeCardBuckets

class TestTxMerger(unittest.TestCase):
    
    def test_statement_parser(self):
        statements = {}
        for key, value in simple_transactions_all.items():
            if not statements.get(key):
                statements[key] = { 'statements': [] }
            statements[key]['statements'] = parseStatements([value], key)
        self.assertDictEqual(statements, parsed_transactions_all)

    def test_buckets_merger(self):
        statements = {}
        for key, value in simple_transactions_all.items():
            if not statements.get(key):
                statements[key] = { 'statements': [], 'buckets': {} }
            statements[key]['statements'] = parseStatements([value], key)
            statements[key]['bucket'] = groupTxInBuckets(statements[key]['statements'], simple_buckets, key)
        merged_buckets, _ = mergeCardBuckets( [ statement["bucket"] for statement in statements.values() ], filter_buckets=[], build_tuples=True )
        self.assertDictEqual(merged_buckets, bucketed_transactions_all)

if __name__ == '__main__':
    unittest.main()