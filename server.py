import socket
from map_generator import generate_rooms

# Server configuration
HOST = '127.0.0.1'
PORT = 60025

# Game state
clients = set()
client_nicknames = {} # Maps address to nickname
client_locations = {}  # Maps address to room_id

# Generate map
rooms = generate_rooms(32, 24)
STARTING_ROOM = '16_12' # Center of map

def main():
    """Sets up the UDP server and runs the main loop."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((HOST, PORT))
        print(f"UDP Server started on {HOST}:{PORT}")

        while True:
            try:
                message, address = server_socket.recvfrom(1024)
                decoded_message = message.decode()
                
                if address not in clients:
                    handle_new_client(address, server_socket)

                print(f"Received from {address}: {decoded_message}")
                handle_client_message(address, decoded_message, server_socket)

            except Exception as e:
                print(f"An error occurred: {e}")
                handle_disconnect(address, f"--- A user has disconnected unexpectedly. ---", server_socket)


def handle_new_client(address, server_socket):
    """Handles a new client connection."""
    print(f"New connection from {address}")
    clients.add(address)
    client_locations[address] = STARTING_ROOM
    
    room = rooms[STARTING_ROOM]
    welcome_msg = f"{room['description']}\nType /look to see what's around or /help for a list of commands."
    server_socket.sendto(welcome_msg.encode(), address)

def handle_disconnect(address, broadcast_message, server_socket):
    """Handles a client disconnection."""
    if address in clients:
        current_room_id = client_locations.get(address)
        if current_room_id:
            # Make user stand up if they were sitting
            if address in rooms[current_room_id]['sitting_users']:
                del rooms[current_room_id]['sitting_users'][address]
            del client_locations[address]

        clients.remove(address)
        print(f"Client {address} disconnected.")
        broadcast_to_room(broadcast_message, current_room_id, server_socket)

def broadcast_to_room(message, room_id, server_socket, exclude_address=None):
    """Broadcasts a message to all clients in a specific room."""
    if not message or not room_id:
        return
        
    for addr, loc in client_locations.items():
        if loc == room_id and addr != exclude_address:
            server_socket.sendto(message.encode(), addr)

def get_map_ascii(rooms, client_location, width, height):
    """Generates an ASCII representation of the map."""
    # Determine the visible area around the player
    player_x, player_y = map(int, client_location.split('_'))
    
    # Define a smaller view radius
    view_radius_x = 5
    view_radius_y = 3

    min_x = max(0, player_x - view_radius_x)
    max_x = min(width - 1, player_x + view_radius_x)
    min_y = max(0, player_y - view_radius_y)
    max_y = min(height - 1, player_y + view_radius_y)

    map_str = "Map:\n"
    for y in range(min_y, max_y + 1):
        row = ""
        for x in range(min_x, max_x + 1):
            room_id = f"{x}_{y}"
            if room_id == client_location:
                row += "P"  # Player's position
            elif room_id in rooms:
                # Get biome from room name (simplified for ASCII representation)
                name = rooms[room_id]['name']
                if "Water" in name:
                    row += "~"
                elif "Sandy" in name:
                    row += "."
                elif "Grassland" in name:
                    row += '"'
                elif "Forest" in name:
                    row += "T"
                elif "Rocky" in name:
                    row += "#"
                else:
                    row += "?" # Unknown biome
            else:
                row += " " # Should not happen if rooms cover the whole grid
        map_str += row + "\n"
    return map_str



def handle_client_message(address, message, server_socket):
    """Processes a message from a client."""
    current_room_id = client_locations.get(address)
    if not current_room_id:
        # Should not happen for connected clients
        return
    
    current_room = rooms[current_room_id]
    
    # Improved command parsing
    parts = message.split()
    command = parts[0].lower()

    # The client sends commands in the format: /command [args...] <nickname>
    # Regular chat messages are sent as: <nickname>: <message>
    # Special case for the initial join message
    if message.endswith(" has joined the chat ---"):
        # Extract nickname from "--- <nickname> has joined the chat ---"
        nickname = message.split("--- ")[1].split(" has joined")[0]
        client_nicknames[address] = nickname
        broadcast_to_room(message, current_room_id, server_socket, exclude_address=address)
        return

    is_command = command.startswith('/')
    nickname = parts[-1] if len(parts) > 1 else ""
    args = parts[1:-1] if len(parts) > 2 else []

    if not is_command:
        # Directional shorthands (n, e, s, w)
        direction_shorthands = {'n': 'north', 'e': 'east', 's': 'south', 'w': 'west'}
        if command in direction_shorthands:
            is_command = True
            args = [direction_shorthands[command]]
            command = '/go'
        else:
            # This is a regular chat message, broadcast it to everyone in the room
            broadcast_to_room(message, current_room_id, server_socket)
            return

    if is_command and address not in client_nicknames and nickname:
        client_nicknames[address] = nickname

    broadcast_message = ""

    if command == '/look':
        item_descriptions = []
        for item, desc in current_room['items'].items():
            sitter_name = "Someone" # Placeholder
            is_taken = any(sitting_item == item for sitting_item in current_room['sitting_users'].values())
            if is_taken:
                item_descriptions.append(f"{item} ({sitter_name} is sitting here)")
            else:
                item_descriptions.append(item)
        
        other_people = [name for addr, name in client_nicknames.items() if client_locations.get(addr) == current_room_id and addr != address]
        people_description = ""
        if other_people:
            people_description = f"\nPeople here: {', '.join(other_people)}."

        item_list = ", ".join(item_descriptions)
        exit_list = ", ".join(current_room['exits'].keys())
        look_response = f"You see: {item_list}.\nExits are: {exit_list}.{people_description}"
        server_socket.sendto(look_response.encode(), address)

    elif command == '/lookat':
        if args:
            target_name = " ".join(args)
            
            if target_name == 'me':
                server_socket.sendto(f"You see yourself, {nickname}. You look great!".encode(), address)
                return

            # Check if looking at an item
            target_item = f"a {target_name}"
            if target_item in current_room['items']:
                description = current_room['items'][target_item]
                server_socket.sendto(description.encode(), address)
                return

            # Check if looking at another player
            target_addr = None
            for addr, name in client_nicknames.items():
                if name.lower() == target_name.lower() and client_locations.get(addr) == current_room_id:
                    target_addr = addr
                    break
            
            if target_addr:
                if target_addr == address: # Should be caught by 'me' but as a fallback
                    server_socket.sendto(f"You see yourself, {nickname}. You look great!".encode(), address)
                else:
                    target_nickname = client_nicknames[target_addr]
                    server_socket.sendto(f"You see {target_nickname}. They look busy.".encode(), address)
            else:
                server_socket.sendto(f"You don't see a {target_name} here.".encode(), address)
        else:
            server_socket.sendto("Look at what? Usage: /lookat <item or person>".encode(), address)

    elif command == '/sit':
        if args:
            target_name = " ".join(args)
            target_item = f"a {target_name}"

            if target_item not in current_room['items']:
                server_socket.sendto(f"There is no {target_name} here.".encode(), address)
            elif target_item in current_room['sitting_users'].values():
                server_socket.sendto(f"Someone is already sitting on {target_item}.".encode(), address)
            else:
                # Stand up from any other item
                if address in current_room['sitting_users']:
                    del current_room['sitting_users'][address]
                
                current_room['sitting_users'][address] = target_item
                server_socket.sendto(f"You sit on {target_item}.".encode(), address)
                broadcast_message = f"--- {nickname} sits on {target_item}. ---"
        else:
            # Sit on the ground
            target_item = "the ground"
            # Stand up from any other item
            if address in current_room['sitting_users']:
                del current_room['sitting_users'][address]
            
            current_room['sitting_users'][address] = target_item
            server_socket.sendto(f"You sit on {target_item}.".encode(), address)
            broadcast_message = f"--- {nickname} sits on {target_item}. ---"

    elif command == '/go':
        if args:
            direction = args[0].lower()
            if direction in current_room['exits']:
                new_room_id = current_room['exits'][direction]
                
                # Announce departure
                departure_msg = f"--- {nickname} leaves, heading {direction}. ---"
                broadcast_to_room(departure_msg, current_room_id, server_socket, exclude_address=address)

                # Change room
                client_locations[address] = new_room_id
                new_room = rooms[new_room_id]

                # Announce arrival
                arrival_msg = f"--- {nickname} arrives. ---"
                broadcast_to_room(arrival_msg, new_room_id, server_socket, exclude_address=address)

                # Describe new room to the user
                server_socket.sendto(new_room['description'].encode(), address)
                # Trigger a /look in the new room for the user
                handle_client_message(address, f"/look {nickname}", server_socket)

            else:
                server_socket.sendto("You can't go that way.".encode(), address)
        else:
            server_socket.sendto("Go where? Usage: /go <direction>".encode(), address)
    
    elif command == '/map':
        map_representation = get_map_ascii(rooms, current_room_id, 32, 24)
        server_socket.sendto(map_representation.encode(), address)

    elif command == '/help':
        help_text = """Commands:
/look - See the room description, items, and exits.
/lookat <item or person> - Look at an item or a person to get a description.
/sit [item] - Sit on an item, or on the ground if no item is specified.
/go <direction> - Move to another room. (n, s, e, w shortcuts work)
/map - Display a small ASCII map of your surroundings.
/emote <action> - Perform an action.
/smile - Smile at everyone in the room.
/exit or /quit - Disconnect from the server."""
        server_socket.sendto(help_text.encode(), address)

    elif command == '/emote':
        if args:
            action = " ".join(args)
            server_socket.sendto(f"You {action}.".encode(), address)
            broadcast_message = f"--- {nickname} {action}. ---"
        else:
            server_socket.sendto("Emote what? Usage: /emote <action>".encode(), address)

    elif command == '/smile':
        server_socket.sendto("You smile. 😊".encode(), address)
        broadcast_message = f"--- {nickname} smiles. 😊 ---"
    
    elif command in ('/exit', '/quit'):
        handle_disconnect(address, f"--- {nickname} has left the chat ---", server_socket)

    else:
        # It's a chat message that starts with a '/', but is not a recognized command.
        # The old logic would broadcast this. The new logic should probably tell the user it's an unknown command.
        server_socket.sendto(f"Unknown command: {command}".encode(), address)


    if broadcast_message:
        broadcast_to_room(broadcast_message, current_room_id, server_socket, exclude_address=address)


if __name__ == "__main__":
    main()
