from os import getenv
import requests, pprint
from config import ExpenseManagerConstants
from datetime import datetime as dt

BASE_URL = "https://secure.splitwise.com/api/v3.0"
class SplitwiseSDK:
    def __init__(self):
        self.__API_KEY = ExpenseManagerConstants.SPLITWISE_API_KEY
        self.__headers = {
            "Authorization": f"Bearer {self.__API_KEY}"
        }
        self.groupId = ExpenseManagerConstants.SPLITWISE_GROUP_ID
        if not self.__API_KEY:
            raise Exception('SPLITWISE_API_KEY required!')
    
    def getGroups(self):
        r = requests.post(url=f"{BASE_URL}/get_groups",
                      headers=self.__headers)
        return r.json()
    
    def getGroup(self,group_id):
        r = requests.post(url=f"{BASE_URL}/get_group/{group_id}",
                      headers=self.__headers)
        return r.json()
    
    def getCategories(self, flattened = True):
        r = requests.post(url=f"{BASE_URL}/get_categories",
                      headers=self.__headers)
        categories = r.json()["categories"]
        cat, _cat = {}, {}
        for category in categories:
            cat[category["name"].lower()] = {}
            for subcat in category["subcategories"]:
                cat[category["name"].lower()][subcat['name'].lower()] = subcat['id']
                _cat[subcat['name'].lower()] = subcat['id']
                if subcat['name'] == 'Other':
                    _cat[category['name'].lower()] = subcat['id']
        return _cat if flattened else cat
    
    def setGroupId(self, group_id):
        self.groupId = group_id
        r = self.getGroup(group_id)
        if not r:
            raise Exception('Invalid Group Id')
        return
        
    def createExpense(self, _title, _cost, _date, _splitwise_category_id):
        if not self.groupId:
            raise Exception('No GroupId set, setGroupId() before creating an Expense')
        r = requests.post(
            url=f"{BASE_URL}/create_expense",
            headers=self.__headers,
            json={
                "cost": _cost,
                "description": _title,
                "details": "string",
                "date": dt.strptime(_date, "%Y-%m-%d").isoformat(),
                "repeat_interval": "never",
                "currency_code": "USD",
                "category_id": _splitwise_category_id,
                "group_id": self.groupId,
                "split_equally": True
            }
        )
        r = r.json()
        if r['errors']:
            raise Exception(r['errors'])
        return r
    
    def deleteExpense(self, expense_id):
        r = requests.post(
            url=f"{BASE_URL}/delete_expense/{expense_id}",
            headers=self.__headers
        )
        return r.json()
