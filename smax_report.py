import json
import configparser
import requests
import urllib.parse
#from smax import Run
#from smax import SmaxAdmin

config = configparser.ConfigParser()
config.read('conf.ini')
#print(config.sections())

print({**config['DEFAULT']})
print('\n')

class SmaxTenant(object):
    def __init__(self, base_url, user_name, password, tenant_id):
        """
        Initiate main wrapper class and connection details
        :param base_url: Base url of your SMAX instance
        :param user_name: user name of user/integration user
        :param password: password of user/integration user
        :param tenant_id: tenant ID of your instance
        """
        self.base_url = base_url
        self.user_name = user_name
        self.password = password
        self.tenant_id = str(tenant_id)
        self.headers = {'Content-Type': 'application/json'}
        
    @staticmethod
    def fix_url_encode(url) -> str:
        """
        Change brackets back to normal brackets since SMAX API
        refuses to accept properly URL encoded string
        :param url: Encoded url to fix
        :return: fixed URL
        """
        return str(url).replace('%28', '(').replace('%2C', ',').replace('%29', ')')
    
    def get_cookie(self):
        """
        Authenticate calls against authentication endpoint
        :return: cookie to pass with each subsequent request
        """
        SMAX_AUTH = '{}/auth/authentication-endpoint/authenticate/login?TENANTID={}'. \
            format(self.base_url, self.tenant_id)
        payload = {'Login': '{}'.format(self.user_name), 'Password': '{}'.format(self.password)}
        payload = json.dumps(payload)
        smax_token = requests.post(SMAX_AUTH, data=payload)
        auth_c = str(smax_token.content.decode("utf-8"))
        cookie_smax = {'LWSSO_COOKIE_KEY': '{0}'.format(auth_c)}
        return cookie_smax

class Run(SmaxTenant):
    def __init__(self, base_url, user_name, password, tenant_id):
        super().__init__(base_url, user_name, password, tenant_id)

    def get_Devices(self, query_params, filters=None):
        """
        Get Devices based on params passed
        :param query_params: FieldIDs you want to query, encased in quotes, comma separated
        :param filters: Filters you'd like to apply, comma separated and encased in quotes, default is None
        :return: Returns JSON result of incident query
        """
        assert type(query_params) == str, 'Query params must be in string form'
        query_params = str(query_params).replace(' ', '')
        if filters:
            assert type(filters) == str, 'Filter params must be in string form'
            filters = SmaxTenant.fix_url_encode(urllib.parse.quote_plus(filters))
            query_endpoint = requests.get('{}/rest/{}/ems/Device?layout={}&filter={}'
                                          .format(self.base_url, self.tenant_id, query_params, filters),
                                          cookies=self.get_cookie()).json()
            print('{}/rest/{}/ems/Device?layout={}&filter={}'
                                          .format(self.base_url, self.tenant_id, query_params, filters))
            return query_endpoint
        query_endpoint = requests.get('{}/rest/{}/ems/Device?layout={}'
                                      .format(self.base_url, self.tenant_id, query_params),
                                      cookies=self.get_cookie()).json()
        print('{}/rest/{}/ems/Device?layout={}'
                                      .format(self.base_url, self.tenant_id, query_params))
        return query_endpoint

class SmaxClass ():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.smax = Run(user_name=config['DEFAULT']['user'],
           password=config['DEFAULT']['password'],
           base_url=config['DEFAULT']['base_url'],
           tenant_id=config['DEFAULT']['tenant_id'])
        
    def get_smax_Devices(self):
        smaxobj = self.smax.get_Devices("Id,DisplayLabel",
                                         "SubType='Server'")
        return smaxobj

smaxClassUser = SmaxClass()
a = smaxClassUser.get_smax_Devices()

print('\n')

for item in a['entities']:
    print(item)
    #print(item + ': ' + str(a[item]))

'''        smaxobj = self.smax.get_Devices("Id,DisplayLabel,SubType,OsType,OsName,AssetModel",
                                         "(SubType='Server' and OsType='Unix')")'''

'''
print(dir(SmaxAdmin))
print(SmaxAdmin.get_help(Run.create_entity))
for key in config['DEFAULT']: print(key + ":" +config['DEFAULT'][key])
'''