
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import json
import logging

from TcpServer.sensorDataProcessing import SensorDataProcess

#from Cmd.CmdControler import CmdControler
#from properties.PropertiesReader import ConfParams
# from pepsiN.Cmd.CmdView import CmdView

# Sample blog post data similar to
# https://ordina-jworks.github.io/frontend/2019/03/04/vue-with-typescript.html#4-how-to-write-your-first-component

#params = ConfParams()
_g_posts = [
    {
        'title': 'My first blogpost ever!',
        'body': 'Lorem ipsum dolor sit amet.',
        'author': 'Elke',
        'date_ms': 1593607500000,  # 2020 July 1 8:45 AM Eastern
    }
]


class _RequestHandler(BaseHTTPRequestHandler):
    # Borrowing from https://gist.github.com/nitaku/10d0662536f37a087e1b
    def _set_headers(self):
        self.send_response(HTTPStatus.OK.value)
        self.send_header('Content-type', 'application/json')
        # Allow requests from any origin, so CORS policies don't
        # prevent local development.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_headers()
        # self.wfile.write(json.dumps(_g_posts).encode('utf-8'))
        #print(self.path)
        path = self.path.split('/')
        #print(path)
        if path[1] == 'Reset':
            ids = path[2]
            #cmd = CmdControler()
            #cmd.cmd_view.reset_device(ids)
            # print("in TurnLaserOnOff")
            _g_posts = {'hello': 'Reset', 'device': ids, 'received': 'ok'}
        elif path[1] == 'TurnLaserOnOff':
            ids = path[2]
            #cmd = CmdControler()
            data = {'pointer_leaser': 1, 'id': ids}
            is_plc = False
            error_message = None
            #cmd.handel_data(data, is_plc, error_message)
            print("in TurnLaserOnOff")
            _g_posts = {'hello': 'TurnLaserOnOff', 'device': ids, 'received': 'ok'}
        # handle AVT API v1/avt/values
        elif path[1] == 'v1' and path[2] == 'avt' and path[3] == 'values':
            #print("in AVT")
            sensor_data = SensorDataProcess()
            last_data = {"Timestamp": str(sensor_data.algo_8_data["TS"]),
                         "AccumulatedDistance": str(sensor_data.algo_8_data["AccDistHigh"]),
                         "CurrentVelocity": str(sensor_data.algo_8_data["MedVel"]),
                         "StatusFlag": str(sensor_data.algo_8_data["StatusFlag"])
                        }
            _g_posts = last_data
            #_g_posts = last_algo_8_value
            #_g_posts = {'hello': 'TurnLaserOnOff', 'device': ids, 'received': 'ok'}
            #return last_algo_8_value
        elif path[1] == 'one':
            _g_posts = {'hello': 'there', 'received': 'ok'}
        else:
            _g_posts = {'hello': 'there', 'received': 'default'}
        self.wfile.write(json.dumps(_g_posts).encode('utf-8'))

    def do_POST(self):
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))
        #message['date_ms'] = int(time.time()) * 1000
        _g_posts.append(message)
        self._set_headers()
        self.wfile.write(json.dumps({'success': True}).encode('utf-8'))

    def do_OPTIONS(self):
        # Send allow-origin header for preflight POST XHRs.
        self.send_response(HTTPStatus.NO_CONTENT.value)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()


def run_server():
    #PORT = params.getParam('REST_PORT')
    PORT = 8089
    server_address = ('', int(PORT))
    httpd = HTTPServer(server_address, _RequestHandler)
    print('serving at %s:%d' % server_address)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    run_server()