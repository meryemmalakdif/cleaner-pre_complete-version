from bridge import Bridge
import ipfshttpclient
import json

class Adapter:
    base_url = 'http://localhost:5001'
    from_params = ['base', 'from', 'coin']
    to_params = ['quote', 'to', 'market']

    def __init__(self, input):
        # self.id = input.get('id', '1')
        # self.request_data = input.get('data')
        self.number="Qmf2Zn9nkefD2gKeP8aDbwGYhctznhNYwX9LWTviTA9jPY"
        #if self.validate_request_data():
        self.bridge = Bridge()
            #self.set_params()
        
        # else:
        #     self.result_error('No data provided')
    async def require(self):
        await self.create_request()


    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        return True

    def set_params(self):
        print("hola")
        for param in self.from_params:
            self.from_param = self.request_data.get(param)
            if self.from_param is not None:
                break
        for param in self.to_params:
            self.to_param = self.request_data.get(param)
            if self.to_param is not None:
                break

    async def create_request(self):
        print("all good")
            # client = ipfshttpclient.connect(host='localhost', port=5001)
            # stream = client.cat(self.number)
            # data = b""
            # async for chunk in stream:
            #     data += chunk

            # try:
            #     json_data = json.loads(data.decode())
            #     print("ur result ",json_data)
            #     return json_data
            # except json.JSONDecodeError:
            #     print("Error decoding JSON")
            #     return data.decode()


            #response = self.bridge.request(self.base_url, params)
            # data = response.json()
            # print("the response is ",data)
            # self.result = data[self.to_param]
            # data['result'] = self.result
            # self.result_success(data)

    def result_success(self, data):
        self.result = {
            'jobRunID': self.id,
            'data': data,
            'result': self.result,
            'statusCode': 200,
        }

    def result_error(self, error):
        self.result = {
            'jobRunID': self.id,
            'status': 'errored',
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }