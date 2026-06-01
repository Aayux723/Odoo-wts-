import xmlrpc.client
from config import *

common = xmlrpc.client.ServerProxy(
    f"{URL}/xmlrpc/2/common"
)

uid = common.authenticate(
    DB,
    USERNAME,
    PASSWORD,
    {}
)

models = xmlrpc.client.ServerProxy(
    f"{URL}/xmlrpc/2/object"
)