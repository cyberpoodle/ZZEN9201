import socket
import socketserver
import select


BUFFER_SIZE = 1024


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        username = ""
        password = ""
        self.request.setblocking(0)
        self.request.sendall(b"ROUTER (ttyp0)\n\nlogin: ")
        state = 1
        while True:
            ready = select.select([self.request], [self.request], [], 1)
            if ready[0]:
                data = self.request.recv(BUFFER_SIZE)
                if not data:
                    print("remote hungup")
                    self.finish()
                    break
                if state == 1:
                    username = data
                    self.request.sendall(b"Password: ")
                    state += 1
                elif state == 2:
                    password = data
                    print(f"login from {self.client_address[0]} as {username}:{password}")
                    self.request.sendall(b"Login incorrect\nlogin: ")
                    state = 1
                print(f"recv: {data}")

if __name__ == "__main__":
    HOST, PORT = "localhost", 2300
    with TCPServer((HOST, PORT), Handler) as server:
        server.serve_forever()