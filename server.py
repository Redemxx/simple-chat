from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from queue import Queue
import re

incoming_port = 7580
username_regex = r"(\B|\b)@.[^ ]+\b"

client_connections = {}


def client_connection(socket_conn: socket, addr):
    try:
        username = socket_conn.recv(1024).decode()
    except:
        socket_conn.close()
        print(f"Unable to establish communication with {addr}")
        return

    message_queue = Queue()
    client_connections[username] = message_queue

    outgoing_thread = Thread(target=client_outgoing, args=(socket_conn, message_queue, username,))
    outgoing_thread.start()

    try:
        while username in client_connections:
            # May need to consider multi-packet messages.
            message = socket_conn.recv(1024).decode()
            forward_message(username, message)
    finally:
        socket_conn.close()
        outgoing_thread.join()
        client_connections.pop(username)


def client_outgoing(socket_conn: socket, queue, username):
    while username in client_connections:
        item = queue.get()
        socket_conn.sendall(item.encode('utf-8'))
        queue.task_done()


def forward_message(sender, message: str):
    # Direct Message
    direct_message = re.search(username_regex, message)
    if direct_message:
        recipient = direct_message.group(0)[1:]

        try:
            client_connections[recipient].put(message)
        except:
            client_connections[sender].put(f"System: Could not find user {recipient}")
        finally:
            return

    # Message all users
    for client in client_connections:
        if client == sender:
            continue

        client_connections[client].put(message)


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

    welcomeSocket.close()
