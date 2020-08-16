import os

COSMOS_CONNECTION_STRING = os.environ.get('CosmosConnectionString', 'None, possibly test environment')


from . import environment
