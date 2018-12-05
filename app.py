import pymongo
import requests
import datetime
import environ

env = environ.Env()

ELK = {
    'URL': env('ELK_URL'),
    'USER': env('ELK_USER'),
    'PASSWD': env('ELK_PASSWD'),
    'TAG': {
        'application': env.str('ELK_TAG', 'vpn')
    }
}

MONGODB = {
    'URL': env.str('MONGODB_URL', 'mongodb://localhost:27017'),
    'DATABASE': env('MONGODB_NAME'),
    'COLLECTION': env('MONGODB_DB_COLLECTION')
}

client = pymongo.MongoClient(MONGODB['URL'])
collection=client[MONGODB['DATABASE']][MONGODB['COLLECTION']]
logs = collection.find({'timestamp': {'$gte': datetime.datetime.now() - datetime.timedelta(hours = 1)}}).sort('timestamp', pymongo.ASCENDING)
logging.info("Found %d new log entries." %(logs.count()))
for line in logs:
    line.update(ELK['TAG'])
    requests.put(ELK['URL'], headers = {'Content-type': 'application/json'}, auth = (ELK['USER'], ELK['PASSWD']), data = line)

logging.info("Completed updating %d new log entries." %(logs.count()))
