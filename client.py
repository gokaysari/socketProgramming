#Gökay Sarı - 150180727

import socket
import hashlib
import struct
import threading

def authWithServer(sock, private_string):
    # Receive a random string from the server
    random_string = sock.recv(1024).decode('utf-8')

    # Hash the private string 
    hash_to_send = hashlib.sha1((private_string + random_string).encode('utf-8')).hexdigest()
    sock.sendall(hash_to_send.encode('utf-8'))

    # Wait for the server's response
    response = sock.recv(1024).decode('utf-8')
    print(response)

    return "Authentication successful" in response

def receiveTimeUpdate(sock):
    while True:
        try:
            # Wait for the next 2 bytes representing the remaining time
            data = sock.recv(2)
            if not data:
                break # No more data, exit the loop

            remaining_time = struct.unpack('!H', data)[0]
            if remaining_time == 0:
                print("Time's up!")
                break
            else:
                print(f"Remaining time: {remaining_time} seconds")
        except struct.error as e:
            print(f"Struct unpacking error: {e}")
            break
        except socket.error as e:
            print(f"Socket error: {e}")
            break


def handleServerMsg(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if message:
                print(message)
                if "Game over" in message or "Correct guess!" in message:
                    break  # End the thread and game loop when the game is over
        except socket.error as e:
            print(f"Socket error: {e}")
            break#

def playGame(sock):
    threading.Thread(target=receiveTimeUpdate, args=(sock,), daemon=True).start()
    threading.Thread(target=handleServerMsg, args=(sock,), daemon=True).start()

    # Game loop for sending guesses to the server
    while True:
        guess = input("What is your guess?Number, even, odd?").strip().lower()
        if guess.isdigit() or guess in ['even', 'odd']:
            try:
                sock.sendall(guess.encode('utf-8'))
            except socket.error as e:
                print(f"Error sending data: {e}")
                break
        else:
            print("Invalid input. Please try again.")

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 23456
    PRIVATE_STRING = "gok64436443ay64434364gok"  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        if authWithServer(sock, PRIVATE_STRING):
            # Send 'Y' to proceed with the game
            sock.sendall('Y'.encode('utf-8'))
            playGame(sock)
        else:
            print("Authentication failed. Exiting.")
