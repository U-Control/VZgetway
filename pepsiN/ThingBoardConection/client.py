import requests
import json


class ThingBoardUser:

    instance = None

    def __new__(cls):

        if not ThingBoardUser.instance:
            ThingBoardUser.instance = ThingBoardUser.__ThingBoardUser()
        return ThingBoardUser.instance

    class __ThingBoardUser:

        telemetry_url = '/api/v1/{}/telemetry'

        port = '9090'

        host = 'http://127.0.0.1'

        user = {
            "username": "tenant@thingsboard.org",
            "password": "tenant"
        }

        token = "Bearer "

        refreshToken = ""

        headers = {

        }

        @staticmethod
        def access_token(id_device):
            return str(id_device) + '_prex'

        def __init__(self):
            self.login()

        def set_headers(self, header_key, header_value):
            self.headers[header_key] = header_value

        def login(self, refresh=None):

            self.token = "Bearer "
            url = '/api/auth/login' if not refresh else '/api/auth/token'

            body = json.dumps(self.user) if not refresh else json.dumps({"refreshToken": self.refreshToken})

            re = self.post(url, body)

            if re.status_code == 200:
                re = json.loads(re.text)
                self.refreshToken = re.get("refreshToken")
                self.token += re.get("token")
                self.set_headers('X-Authorization', self.token)

        def get(self, path):

            re = requests.get(url=self.get_url(path), headers=self.headers)
            if re.status_code == 401 and json.loads(re.text).get("message") == "Token has expired":
                self.login(True)
                self.get(path)
            return re

        def post(self, path, body):
            return requests.post(url=self.get_url(path), data=body)

        def get_url(self, path):
            return self.host + ":" + self.port + path

        def send_telemetry(self, id_device, data):
            fi = ""
            for i in data:
                for j in i["values"]:
                    fi += str(j) + ',' + str(i["values"][j]) + ',\n'
            # print(self.all_data)
            f = open("to.csv", "w")
            f.write(fi)
            f.close()
            i = json.dumps(data)
            try:
                print("Wait for the data to be uploaded")
                re = self.post(self.telemetry_url.format(self.access_token(id_device)), i)
                print("Sending data succeeded")
            except requests.exceptions.RequestException as e:
                print(e)
                return False
            if re.status_code != 200:
                print("error sending data", re)
                return False
            # for i in data:
            #     i = json.dumps(i).encode()
            #     try:
            #         re = self.post(self.telemetry_url.format(self.access_token(id_device)), i)
            #     except requests.exceptions.RequestException as e:
            #         print(e)
            #         return False
            #     if re.status_code != 200:
            #         print("error sending data", re)
            #         return False
            # print("sending data complet")

        def __str__(self):
            return repr(self)
