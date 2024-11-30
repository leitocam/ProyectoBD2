from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['tienda_ropa_alpaca']

