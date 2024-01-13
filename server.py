#Gökay Sarı - 150180727
#Even though the asynchronous operation did not work exactly as expected in the assignment, the assignment was a good tutorial.
import socket
import hashlib
import random
import threading
import struct
import time

def sendRemainingTime(client_socket):
    remaining_time = 30
    while remaining_time > 0:
        time.sleep(3) # Sleep for 3 seconds
        remaining_time -= 3
        try:
            if client_socket.fileno() != -1:
                client_socket.sendall(struct.pack('!H', remaining_time))
        except socket.error:
            break # Exit if there's a socket error

def processGuess(client_socket, guess, number_to_guess):
    correct = False
    if guess.lower() in ["even", "odd"]:
        # Check parity
        correct_parity = (number_to_guess % 2 == 0 and guess.lower() == "even") or \
                         (number_to_guess % 2 == 1 and guess.lower() == "odd")
        if correct_parity:
            response = "\nCorrect parity! Keep guessing for the exact number."
        else:
            response = "\nIncorrect parity. Try again."
        client_socket.sendall(response.encode('utf-8'))
        return False  # The game continues regardless of parity guess
    else:
        try:
            guess_number = int(guess)
            if guess_number == number_to_guess:
                response = "\nCorrect! You've guessed the number!"
                correct = True
            else:
                response = "\nWrong guess, try again."
            client_socket.sendall(response.encode('utf-8'))
        except ValueError:
            response = "\nInvalid input. Please send a valid number or 'even'/'odd'."
            client_socket.sendall(response.encode('utf-8'))

    return correct  

def clientHandler(client_socket, address, private_string):
    try:
        random_string = hashlib.sha1().hexdigest()[:32]
        client_socket.sendall(random_string.encode('utf-8'))
        client_hash = client_socket.recv(1024).decode('utf-8')
        correct_hash = hashlib.sha1((private_string + random_string).encode('utf-8')).hexdigest()

        if client_hash != correct_hash:
            client_socket.sendall("Authentication failed.".encode('utf-8'))
            return

        client_socket.sendall("Authentication successful. Do you wish to proceed? (Y/N)".encode('utf-8'))
        proceed = client_socket.recv(1024).strip().decode('utf-8').lower()

        if proceed == 'y':
            number_to_guess = random.randint(0, 36)
            print(f"The number to guess is: {number_to_guess}")

            # Start the timer in a separate thread with only the client_socket as an argument
            threading.Thread(target=sendRemainingTime, args=(client_socket,), daemon=True).start()

            while True:
                guess_data = client_socket.recv(1024).decode().strip()
                if not guess_data:
                    break  # No data received

                if processGuess(client_socket, guess_data, number_to_guess):
                    break  # Correct guess

    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        client_socket.close()

def startServer(host, port, private_string):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=clientHandler, args=(client_socket, addr, private_string)).start()

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 23456
    PRIVATE_STRING = "gok64436443ay64434364gok"
    startServer(HOST, PORT, PRIVATE_STRING)
