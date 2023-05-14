from omspy_brokers.angel_one import AngelOne
from toolkit.fileutils import Fileutils

f = Fileutils()
y = f.get_lst_fm_yml("../../../confid/angel.yaml")
ao = AngelOne(api_key=y['api_key'], user_id=y['user_id'], 
              password=y['password'], totp=y['totp'])
ao.authenticate()

print(ao.client_name)

