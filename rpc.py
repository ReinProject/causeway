import requests
import json


class RPC(object):
    def __init__(self, username, password, server, port):
        self.url = "http://%s:%s@%s:%s/" % (username, password, server, port)
        self.headers = {'content-type': 'application/json'}

    def get(self, command, params=None):
        if params is None:
            params = []
        payload = {
            "method": command,
	        "params": params,
            "jsonrpc": "2.0",
            "id": 0}
        out = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()

        try:
            res = json.loads(out)
        except:
            res = {"output": out}
        res['result'] = 'success'
        return res

if __name__ == '__main__':
    from settings import *
    rpc = RPC(RPCUSER, RPCPASS, SERVER, RPCPORT)
    print(rpc.get('getaccountaddress',['test']))
