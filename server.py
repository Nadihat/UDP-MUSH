import socket

# Server configuration
HOST = '127.0.0.1'
PORT = 12345

# Game state
clients = set()
client_nicknames = {} # Maps address to nickname
client_locations = {}  # Maps address to room_id
rooms = {
    'living_room': {
        'name': 'Living Room',
        'description': 'Sunlight streams through a large bay window, illuminating a cozy living room. Dust motes dance in the golden rays. A comfortable-looking sofa invites you to relax, and a grand fireplace stands against the far wall, its mantlepiece adorned with curious trinkets. A hallway leads east into darkness, a heavy oak door leads north, and a worn path through tall grass is visible to the west.',
        'items': {
            "a chair": "A simple, yet elegant, wooden chair with a faded velvet cushion. It looks like it has seen many years of use.",
            "a table": "A sturdy, dark wood table. Its surface is polished to a high shine and reflects the room's light.",
            "a sofa": "A plush, oversized sofa with soft, inviting cushions. It looks like the perfect spot for a nap."
        },
        'sitting_users': {},  # Maps address to item name
        'exits': {'east': 'kitchen', 'north': 'snow_wonderland', 'west': 'prairie'}
    },
    'kitchen': {
        'name': 'Kitchen',
        'description': 'You find yourself in a spacious kitchen, filled with the faint, pleasant aroma of baked bread. Polished copper pots and pans hang from a rack overhead, gleaming in the dim light. The living room is to the west, from where you can hear the faint crackling of a fire.',
        'items': {
            "a stove": "A large, modern electric stove with a smooth, black ceramic top. It looks powerful and efficient.",
            "a refrigerator": "A massive, stainless steel refrigerator. It hums a quiet, steady tune, promising delicious treasures within."
        },
        'sitting_users': {},
        'exits': {'west': 'living_room'}
    },
    'snow_wonderland': {
        'name': 'Snow Wonderland',
        'description': 'You step into a breathtaking winter wonderland. The air is crisp and cold, and the ground is covered in a thick blanket of pristine, white snow. Towering ice sculptures glitter in the soft, magical light, and delicate snowflakes drift down from the sky. A path leads south back to the warmth of the living room, and a snowy trail continues north into the unknown.',
        'items': {
            "a giant snowball": "A perfectly round, giant snowball, at least twice your height. It sparkles with a strange, inner light and feels surprisingly light to the touch."
        },
        'sitting_users': {},
        'exits': {'south': 'living_room', 'north': 'snowy_trail'}
    },
    'snowy_trail': {
        'name': 'Snowy Trail',
        'description': 'You are on a narrow, winding trail, flanked by tall, snow-laden pine trees. The snow is deep here, muffling all sound and creating a sense of peaceful isolation. The trail continues north towards a distant, shimmering sea and south back to the magical wonderland.',
        'items': {},
        'sitting_users': {},
        'exits': {'south': 'snow_wonderland', 'north': 'icy_sea'}
    },
    'icy_sea': {
        'name': 'Icy Sea',
        'description': 'You have arrived at the shore of a vast, frozen sea. The ice stretches out to the horizon, a seemingly endless expanse of white and blue. The water beneath is dark and mysterious, and the air is filled with the sound of the wind whistling over the ice. A snowy trail leads south, away from the chilling beauty of the sea.',
        'items': {},
        'sitting_users': {},
        'exits': {'south': 'snowy_trail'}
    },
    'prairie': {
        'name': 'Tallgrass Prairie',
        'description': 'You are standing in a vast tallgrass prairie, the golden blades swaying and rustling around you in the gentle breeze. The sun is warm on your face, and the air is filled with the sweet scent of the earth. A well-trodden path leads east, back to the comfort of the living room, while a faint trail to the north beckons you towards a sunny meadow.',
        'items': {
            "a patch of wildflowers": "A vibrant patch of wildflowers, a riot of color in the sea of grass. Bees buzz lazily from one blossom to the next."
        },
        'sitting_users': {},
        'exits': {'east': 'living_room', 'north': 'sunny_meadow'}
    },
    'sunny_meadow': {
        'name': 'Sunny Meadow',
        'description': 'You have entered a peaceful, sunny meadow, alive with the gentle buzzing of bees and the fluttering of colorful butterflies. The air is warm and fragrant with the scent of clover and daisies. The tallgrass prairie from which you came lies to the south.',
        'items': {
            "a lone oak tree": "A majestic old oak tree stands in the center of the meadow, its sprawling branches providing a cool, shady respite from the sun."
        },
        'sitting_users': {},
        'exits': {'south': 'prairie'}
    }
}
STARTING_ROOM = 'living_room'

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

    if command.startswith('/'):
        # For commands, the nickname is the last element
        nickname = parts[-1]
        args = parts[1:-1]
        if address not in client_nicknames:
             client_nicknames[address] = nickname
    else:
        # This is a regular chat message, broadcast it to everyone in the room
        broadcast_to_room(message, current_room_id, server_socket)
        return

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
            server_socket.sendto("Sit on what? Usage: /sit <item>".encode(), address)

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
    
    elif command == '/help':
        help_text = """Commands:
/look - See the room description, items, and exits.
/lookat <item or person> - Look at an item or a person to get a description.
/sit <item> - Sit on an item.
/go <direction> - Move to another room.
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