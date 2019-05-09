from spyne import Application, ServiceBase, rpc
from spyne import String, Integer
from spyne import Mandatory as M
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

class SOAPWsgiApplication(WsgiApplication):

    def __call__(self, req_env, start_response, wsgi_url=None):
        """Only match URL requests starting with '/soap/'."""
        if req_env['PATH_INFO'].startswith('/soap/'):
            return super(SOAPWsgiApplication, self).__call__(
                req_env, start_response, wsgi_url)


class MyService(ServiceBase):
    @rpc(M(String), _returns=M(Integer))
    def get_stock_quantity(self, product_code):
        # TODO
        print "PRODUCT:", product_code
        return 0

# Spyne application
application = Application(
    [MyService],
    'http://localhost:9680/soap/',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11())


# WSGI application
# wsgi_application = WsgiApplication(application)
# wsgi_application = WsgiApplication(application)
wsgi_application = SOAPWsgiApplication(application)
# WSGI application



from wsgiref.simple_server import make_server
# from my_service import wsgi_application

server = make_server('0.0.0.0', 9680, wsgi_application)
server.serve_forever()
