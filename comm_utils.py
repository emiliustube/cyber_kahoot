# Simple functions to send and receive messages

def send_message(client_socket, message):
    """Send a message to someone"""
    try:
        client_socket.send(message.encode())
        return True
    except:
        return False

def receive_message(client_socket):
    """Get a message from someone"""
    try:
        data = client_socket.recv(1024).decode()
        return data
    except:
        return None
