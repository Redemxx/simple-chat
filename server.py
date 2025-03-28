from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

incoming_port = 7580

client_threads = []


def client_connection(socket: socket, addr):
    client_active = True
    try:
        while client_active:
            pass
    finally:
        socket.close()


if __name__ == "__main__":
    print(f"Server started on port {incoming_port}")

    welcomeSocket = socket(AF_INET, SOCK_STREAM)
    welcomeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    welcomeSocket.bind(("", incoming_port))
    welcomeSocket.listen(4)

    while True:
        connectionSocket, addr = welcomeSocket.accept()
        thread = Thread(target=client_connection, args=(connectionSocket, addr,))
        thread.start()
        client_threads.append(thread)

    welcomeSocket.close()
