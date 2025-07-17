

import socket
import threading

# Server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

def receive_messages(client_socket):
    """Target function for the receiving thread."""
    while True:
        try:
            # Receive message from the server
            message, _ = client_socket.recvfrom(1024)
            # Print the message, ensuring not to print over user input
            print(f"\r{message.decode()}\n> ", end="")
        except OSError:
            # This will happen when the socket is closed by the main thread
            break
        except Exception as e:
            print(f"An error occurred while receiving: {e}")
            break

def main():
    """Sets up the UDP client and handles sending/receiving messages."""
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        # Get a nickname from the user
        nickname = input("Enter your nickname: ")
        print(f"Welcome, {nickname}! Type '/exit' or '/quit' to disconnect.")

        # Start a separate thread for receiving messages
        receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receiver_thread.daemon = True  # Thread will close when main program exits
        receiver_thread.start()

        # Send a joining message
        client_socket.sendto(f"--- {nickname} has joined the chat ---".encode(), (SERVER_HOST, SERVER_PORT))

        # Main loop for sending messages
        while True:
            message = input("> ")
            if message.lower() in ('/exit', '/quit', 'exit', 'quit'):
                print("Disconnecting...")
                # Let the server handle the exit message formatting
                client_socket.sendto(f"/exit {nickname}".encode(), (SERVER_HOST, SERVER_PORT))
                break

            if message.lower() == '/help':                print("Commands:\n/look - See the room description, items, and exits.\n/lookat <item or person> - Look at an item or a person to get a description.\n/sit <item> - Sit on an item.\n/go <direction> - Move to another room.\n/follow - Have your pokemon follow you.\n/unfollow - Have your pokemon stop following you.\n/pet <pokemon> - Pet a pokemon.\n/regions - List available Pokemon regions.\n/emote <action> - Perform an action.\n/smile - Smile at everyone in the room.\n/exit or /quit - Disconnect from the server.")                continue
            # Send the raw message to the server
            if message.startswith('/'):
                # For commands, we send the command and nickname, and any arguments
                # e.g., /sit chair -> becomes "/sit chair nickname"
                parts = message.split(' ', 1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                full_message = f"{command} {args} {nickname}"
            else:
                full_message = f"{nickname}: {message}"

            client_socket.sendto(full_message.encode(), (SERVER_HOST, SERVER_PORT))

if __name__ == "__main__":
    main()

