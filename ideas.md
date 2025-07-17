# Project Ideas and Future Features

This document outlines potential features and improvements for the multi-user chat adventure game.

## Core Gameplay Mechanics
- **Inventory System:**
    - `/take <item>`: Allow users to pick up items from a room and add them to a personal inventory.
    - `/drop <item>`: Allow users to drop items from their inventory into the current room.
    - `/inventory`: Display the items the user is currently carrying.
- **Item Interaction:**
    - `/use <item>`: Implement a system for using items, either on their own or on other items/features in the room (e.g., `/use key on door`).
    - `/give <player> <item>`: Allow users to give items from their inventory to another player in the same room.
- **Dynamic World:**
    - **Puzzles:** Introduce simple puzzles, like locked doors that require a key found in another room.
    - **Movable Items:** Allow certain items to be pushed or pulled.
    - **Stateful Items:** Items that can be changed, e.g., a light that can be turned on or off.

## Social and Communication
- **Enhanced Chat:**
    - `/whisper <player> <message>`: Send a private message to a specific user, regardless of the room they are in.
    - `/emote <action>`: Allow users to perform custom actions (e.g., `/emote waves.` -> "--- User waves. ---").
    - `/yell <message>`: Shout a message that can be heard in adjacent rooms.
- **User Profiles:**
    - `/set-description <description>`: Allow users to set a personal description that others can see.
    - `/examine <player>`: Look at another player to see their description.

## World and Content
- **More Rooms and Areas:**
    - Expand the world with more interconnected rooms and distinct areas (e.g., a forest, a castle, a cave system).
- **Non-Player Characters (NPCs):**
    - Add simple, non-interactive NPCs to rooms to make the world feel more alive.
    - Later, add interactive NPCs that users can talk to or get quests from.
- **Quests:**
    - A simple quest system where users can be given a task (e.g., "find the lost sword") and be rewarded upon completion.

## Technical Enhancements
- **Persistence:**
    - Save the state of the world (room items, player locations, etc.) to a file periodically and on shutdown.
    - Save player inventories and locations so they can disconnect and reconnect without losing progress.
- **Refined Command Parser:**
    - Improve the command parser to handle more complex sentences and variations in commands.
- **User Authentication:**
    - A simple system for users to register a username and password.
- **Configuration File:**
    - Move server settings (HOST, PORT) and world data (rooms, items) into a separate configuration file (e.g., a JSON or YAML file) to make it easier to modify the world without changing the code.
