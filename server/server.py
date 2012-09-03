import tornado.ioloop
import tornado.web
from tornado import websocket


GLOBALS={'sockets': []}
resources = {}

class Resource:
    def __init__(self, id):
        self.id = id
        self.value = '1'
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def write_message(self, message):
        print "Message to " + self.id + ": " + message
        if message == '':
            message = self.value
        else:
            self.value = message

        for l in self.listeners:
            l.write_message(message)


class Endpoint(websocket.WebSocketHandler):
    def open(self, id):
        print "Endpoint.open id="+id
        GLOBALS['sockets'].append(self)
        self.resource = resources.get(id)
        if self.resource is None:
            self.resource = Resource(id)
            resources[id] = self.resource
        else:
            print "Found resource"
        self.resource.add_listener(self)

    def on_message(self, message):
        self.resource.write_message(message)

    def on_close(self):
        GLOBALS['sockets'].remove(self)
        self.resource.remove_listener(self)


application = tornado.web.Application([
    (r"/r/(.*)", Endpoint),
    (r'/(.*)', tornado.web.StaticFileHandler, {'path': 'www'})
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
