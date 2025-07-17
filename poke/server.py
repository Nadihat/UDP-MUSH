import socket
import random

# Server configuration
HOST = '127.0.0.1'
PORT = 12345

# Game state
clients = set()
client_nicknames = {} # Maps address to nickname
client_locations = {}  # Maps address to room_id
client_pokemon = {} # Maps address to their pokemon
following_pokemon = {} # Maps address to the pokemon that is following them
pokemon = {
    'starters': {
        'bulbasaur': {'name': 'Bulbasaur', 'type': 'Grass/Poison', 'moves': ['Tackle', 'Growl']},
        'charmander': {'name': 'Charmander', 'type': 'Fire', 'moves': ['Scratch', 'Growl']},
        'squirtle': {'name': 'Squirtle', 'type': 'Water', 'moves': ['Tackle', 'Tail Whip']}
    },
    'wild': {
        'kanto_pass': [
            {'name': 'Pidgey', 'type': 'Normal/Flying', 'moves': ['Tackle', 'Sand Attack']},
            {'name': 'Rattata', 'type': 'Normal', 'moves': ['Tackle', 'Tail Whip']}
        ],
        'johto_trail': [
            {'name': 'Sentret', 'type': 'Normal', 'moves': ['Scratch', 'Foresight']},
            {'name': 'Hoothoot', 'type': 'Normal/Flying', 'moves': ['Tackle', 'Growl']}
        ],
        'hoenn_cave': [
            {'name': 'Zubat', 'type': 'Poison/Flying', 'moves': ['Leech Life', 'Supersonic']},
            {'name': 'Whismur', 'type': 'Normal', 'moves': ['Pound', 'Uproar']}
        ],
        'sinnoh_ruins': [
            {'name': 'Bidoof', 'type': 'Normal', 'moves': ['Tackle', 'Growl']},
            {'name': 'Starly', 'type': 'Normal/Flying', 'moves': ['Tackle', 'Quick Attack']}
        ],
        'route_201': [
            {'name': 'Bidoof', 'type': 'Normal', 'moves': ['Tackle', 'Growl']},
            {'name': 'Starly', 'type': 'Normal/Flying', 'moves': ['Tackle', 'Quick Attack']}
        ],
        'icy_sea': [
            {'name': 'Finneon', 'type': 'Water', 'moves': ['Pound', 'Water Gun']},
            {'name': 'Lumineon', 'type': 'Water', 'moves': ['Pound', 'Water Gun']},
            {'name': 'Tynamo', 'type': 'Electric', 'moves': ['Tackle', 'Thunder Wave']}
        ]
    }
}
regions = {
    'kanto': {
        'name': 'Kanto',
        'description': 'You have entered the Kanto region, a diverse land of forests, mountains, and bustling cities. The air is filled with a sense of adventure and nostalgia. To the south, you can see the path leading back to the mysterious house from which you came.',
        'exits': {'south': 'kanto_pass'}
    },
    'johto': {
        'name': 'Johto',
        'description': 'You find yourself in Johto, a region rich in tradition and history. Ancient temples and modern cities coexist in harmony. The path back to the house is to the west.',
        'exits': {'west': 'johto_trail'}
    },
    'hoenn': {
        'name': 'Hoenn',
        'description': 'You arrive in Hoenn, a region of breathtaking natural beauty. The air is thick with the scent of saltwater and tropical flowers. A mysterious cave leads back to the north.',
        'exits': {'north': 'hoenn_cave'}
    },
    'sinnoh': {
        'name': 'Sinnoh',
        'description': 'You stand in Sinnoh, a region of myths and legends. The majestic Mount Coronet looms in the distance, its peak shrouded in clouds. Ancient ruins to the south lead back to the prairie.',
        'exits': {'south': 'sinnoh_ruins'}
    }
}
rooms = {
    'living_room': {
        'name': 'Living Room',
        'description': 'Sunlight streams through a large bay window, illuminating a cozy living room. Dust motes dance in the golden rays. A comfortable-looking sofa invites you to relax, and a grand fireplace stands against the far wall, its mantlepiece adorned with curious trinkets. A hallway leads east into darkness, a heavy oak door leads north, and a worn path through tall grass is visible to the west. A pass to the northeast leads to Kanto, and a trail to the southeast leads to Johto.',
        'items': {
            "a chair": "A simple, yet elegant, wooden chair with a faded velvet cushion. It looks like it has seen many years of use.",
            "a table": "A sturdy, dark wood table. Its surface is polished to a high shine and reflects the room's light.",
            "a sofa": "A plush, oversized sofa with soft, inviting cushions. It looks like the perfect spot for a nap."
        },
        'sitting_users': {},  # Maps address to item name
        'exits': {'east': 'kitchen', 'north': 'snow_wonderland', 'west': 'prairie', 'northeast': 'kanto_pass', 'southeast': 'johto_trail'}
    },
    'kanto_pass': {
        'name': 'Kanto Pass',
        'description': 'You are on a well-trodden path. To the north lies the Kanto region. The living room is to the south.',
        'items': {},
        'sitting_users': {},
        'exits': {'north': 'kanto', 'south': 'living_room'}
    },
    'johto_trail': {
        'name': 'Johto Trail',
        'description': 'You are on a scenic trail. To the east lies the Johto region. The living room is to the west.',
        'items': {},
        'sitting_users': {},
        'exits': {'east': 'johto', 'west': 'living_room'}
    },
    'hoenn_cave': {
        'name': 'Cave to Hoenn',
        'description': 'You are in a dark, damp cave. A path to the south leads to the Hoenn region. The snowy wonderland is to the north.',
        'items': {},
        'sitting_users': {},
        'exits': {'south': 'hoenn', 'north': 'snow_wonderland'}
    },
    'sinnoh_ruins': {
        'name': 'Ruins to Sinnoh',
        'description': 'You are in a set of ancient ruins. A path to the north leads to Twinleaf Town. The prairie is to the south.',
        'items': {},
        'sitting_users': {},
        'exits': {'north': 'twinleaf_town', 'south': 'prairie'}
    },
    'twinleaf_town': {
        'name': 'Twinleaf Town',
        'description': 'You are in Twinleaf Town, a small, peaceful town where the fresh scent of leaves hangs in the air. To the south are the Sinnoh Ruins, and to the north is Route 201.',
        'items': {},
        'sitting_users': {},
        'exits': {'south': 'sinnoh_ruins', 'north': 'route_201'}
    },
    'route_201': {
        'name': 'Route 201',
        'description': 'You are on Route 201, a path that winds through the lush greenery of Sinnoh. To the south is Twinleaf Town, and to the west is Lake Verity.',
        'items': {},
        'sitting_users': {},
        'exits': {'south': 'twinleaf_town', 'west': 'lake_verity'}
    },
    'lake_verity': {
        'name': 'Lake Verity',
        'description': 'You have arrived at Lake Verity, a place of serene beauty. The crystal-clear water of the lake reflects the sky like a mirror. A path to the east leads back to Route 201.',
        'items': {},
        'sitting_users': {},
        'exits': {'east': 'route_201'}
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
        'description': 'You step into a breathtaking winter wonderland. The air is crisp and cold, and the ground is covered in a thick blanket of pristine, white snow. Towering ice sculptures glitter in the soft, magical light, and delicate snowflakes drift down from the sky. A path leads south back to the warmth of the living room, and a snowy trail continues north into the unknown. A dark cave to the east leads to Hoenn.',
        'items': {
            "a giant snowball": "A perfectly round, giant snowball, at least twice your height. It sparkles with a strange, inner light and feels surprisingly light to the touch."
        },
        'sitting_users': {},
        'exits': {'south': 'living_room', 'north': 'snowy_trail', 'east': 'hoenn_cave'}
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
        'description': 'You are standing in a vast tallgrass prairie, the golden blades swaying and rustling around you in the gentle breeze. The sun is warm on your face, and the air is filled with the sweet scent of the earth. A well-trodden path leads east, back to the comfort of the living room, while a faint trail to the north beckons you towards a sunny meadow. Some ancient ruins to the west lead to Sinnoh.',
        'items': {
            "a patch of wildflowers": "A vibrant patch of wildflowers, a riot of color in the sea of grass. Bees buzz lazily from one blossom to the next."
        },
        'sitting_users': {},
        'exits': {'east': 'living_room', 'north': 'sunny_meadow', 'west': 'sinnoh_ruins'}
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
    
    # Assign a starter pokemon
    starter_pokemon = random.choice(list(pokemon['starters'].values()))
    client_pokemon[address] = starter_pokemon
    
    room = rooms[STARTING_ROOM]
    welcome_msg = f"{room['description']}\nWelcome to the world of Pokemon! You have been given a {starter_pokemon['name']}.\nType /look to see what's around or /help for a list of commands."
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
    
    current_room = rooms.get(current_room_id) or regions.get(current_room_id)
    
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
        if current_room and 'items' in current_room:
            for item, desc in current_room['items'].items():
                sitter_name = "Someone" # Placeholder
                is_taken = any(sitting_item == item for sitting_item in current_room.get('sitting_users', {}).values())
                if is_taken:
                    item_descriptions.append(f"{item} ({sitter_name} is sitting here)")
                else:
                    item_descriptions.append(item)
        
        other_people = []
        for addr, name in client_nicknames.items():
            if client_locations.get(addr) == current_room_id and addr != address:
                player_desc = name
                if addr in following_pokemon:
                    player_desc += f" (followed by a {following_pokemon[addr]['name']})"
                other_people.append(player_desc)

        people_description = ""
        if other_people:
            people_description = f"\nPeople here: {', '.join(other_people)}."

        wild_pokemon_description = ""
        if current_room_id in pokemon['wild']:
            wild_pokemon_list = [p['name'] for p in pokemon['wild'][current_room_id]]
            if wild_pokemon_list:
                wild_pokemon_description = f"\nWild Pokemon here: {', '.join(wild_pokemon_list)}."

        item_list = ", ".join(item_descriptions)
        exit_list = ", ".join(current_room['exits'].keys())
        look_response = f"You see: {item_list}.\nExits are: {exit_list}.{people_description}{wild_pokemon_description}"
        server_socket.sendto(look_response.encode(), address)

    elif command == '/lookat':
        if args:
            target_name = " ".join(args)
            
            if target_name == 'me':
                my_pokemon = client_pokemon.get(address)
                pokemon_info = ""
                if my_pokemon:
                    pokemon_info = f" You have a {my_pokemon['name']}."
                server_socket.sendto(f"You see yourself, {nickname}. You look great!{pokemon_info}".encode(), address)
                return

            # Check if looking at an item
            target_item = f"a {target_name}"
            if current_room and 'items' in current_room and target_item in current_room['items']:
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
                    target_pokemon = client_pokemon.get(target_addr)
                    pokemon_info = ""
                    if target_pokemon:
                        pokemon_info = f" They have a {target_pokemon['name']}."
                    server_socket.sendto(f"You see {target_nickname}. They look busy.{pokemon_info}".encode(), address)
            else:
                # Check if looking at a wild pokemon
                if current_room_id in pokemon['wild']:
                    for p in pokemon['wild'][current_room_id]:
                        if p['name'].lower() == target_name.lower():
                            server_socket.sendto(f"A wild {p['name']}. It looks ready to battle.".encode(), address)
                            return
                server_socket.sendto(f"You don't see a {target_name} here.".encode(), address)
        else:
            server_socket.sendto("Look at what? Usage: /lookat <item, person, or pokemon>".encode(), address)

    elif command == '/sit':
        if args:
            target_name = " ".join(args)
            target_item = f"a {target_name}"

            if not current_room or 'items' not in current_room or target_item not in current_room['items']:
                server_socket.sendto(f"There is no {target_name} here.".encode(), address)
            elif target_item in current_room.get('sitting_users', {}).values():
                server_socket.sendto(f"Someone is already sitting on {target_item}.".encode(), address)
            else:
                # Stand up from any other item
                if address in current_room.get('sitting_users', {}):
                    del current_room['sitting_users'][address]
                
                current_room.setdefault('sitting_users', {})[address] = target_item
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
                if address in following_pokemon:
                    departure_msg += f" Your {following_pokemon[address]['name']} follows you."
                broadcast_to_room(departure_msg, current_room_id, server_socket, exclude_address=address)

                # Change room
                client_locations[address] = new_room_id
                new_room = rooms.get(new_room_id) or regions.get(new_room_id)

                # Announce arrival
                arrival_msg = f"--- {nickname} arrives. ---"
                if address in following_pokemon:
                    arrival_msg += f" A {following_pokemon[address]['name']} follows them."
                broadcast_to_room(arrival_msg, new_room_id, server_socket, exclude_address=address)

                # Describe new room to the user
                server_socket.sendto(new_room['description'].encode(), address)
                # Trigger a /look in the new room for the user
                handle_client_message(address, f"/look {nickname}", server_socket)

            else:
                server_socket.sendto("You can't go that way.".encode(), address)
        else:
            server_socket.sendto("Go where? Usage: /go <direction>".encode(), address)
    
    elif command == '/follow':
        my_pokemon = client_pokemon.get(address)
        if my_pokemon:
            following_pokemon[address] = my_pokemon
            server_socket.sendto(f"Your {my_pokemon['name']} is now following you.".encode(), address)
            broadcast_to_room(f"--- {nickname}'s {my_pokemon['name']} starts following them. ---", current_room_id, server_socket, exclude_address=address)
        else:
            server_socket.sendto("You don't have a pokemon to follow you.".encode(), address)

    elif command == '/unfollow':
        if address in following_pokemon:
            pokemon_name = following_pokemon[address]['name']
            del following_pokemon[address]
            server_socket.sendto(f"Your {pokemon_name} is no longer following you.".encode(), address)
            broadcast_to_room(f"--- {nickname}'s {pokemon_name} stops following them. ---", current_room_id, server_socket, exclude_address=address)
        else:
            server_socket.sendto("You don't have a pokemon following you.".encode(), address)

    elif command == '/pet':
        if args:
            target_name = " ".join(args)
            
            # Pet own pokemon
            my_pokemon = client_pokemon.get(address)
            if my_pokemon and my_pokemon['name'].lower() == target_name.lower():
                server_socket.sendto(f"You pet your {my_pokemon['name']}. It seems happy!".encode(), address)
                broadcast_to_room(f"--- {nickname} pets their {my_pokemon['name']}. ---", current_room_id, server_socket, exclude_address=address)
                return

            # Pet other player's pokemon
            for addr, name in client_nicknames.items():
                if client_locations.get(addr) == current_room_id and addr != address:
                    if addr in following_pokemon and following_pokemon[addr]['name'].lower() == target_name.lower():
                        server_socket.sendto(f"You pet {name}'s {following_pokemon[addr]['name']}. It seems to like it!".encode(), address)
                        broadcast_to_room(f"--- {nickname} pets {name}'s {following_pokemon[addr]['name']}. ---", current_room_id, server_socket, exclude_address=address)
                        return

            # Pet wild pokemon
            if current_room_id in pokemon['wild']:
                for p in pokemon['wild'][current_room_id]:
                    if p['name'].lower() == target_name.lower():
                        server_socket.sendto(f"You pet the wild {p['name']}. It seems friendly.".encode(), address)
                        broadcast_to_room(f"--- {nickname} pets a wild {p['name']}. ---", current_room_id, server_socket, exclude_address=address)
                        return
            
            server_socket.sendto(f"You don't see a {target_name} to pet here.".encode(), address)
        else:
            server_socket.sendto("Pet what? Usage: /pet <pokemon>".encode(), address)

    elif command == '/regions':
        region_list = "\n".join([f"- {name.capitalize()}" for name in regions.keys()])
        server_socket.sendto(f"Available regions:\n{region_list}".encode(), address)

    elif command == '/help':
        help_text = """Commands:
/look - See the room description, items, and exits.
/lookat <item or person> - Look at an item or a person to get a description.
/sit <item> - Sit on an item.
/go <direction> - Move to another room.
/follow - Have your pokemon follow you.
/unfollow - Have your pokemon stop following you.
/pet <pokemon> - Pet a pokemon.
/regions - List available Pokemon regions.
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