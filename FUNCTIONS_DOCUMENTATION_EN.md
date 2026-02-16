# Cyber Kahoot - Functions Documentation (English)

## Table of Contents
- [Server.py - my_server Class](#serverpy---my_server-class)
- [KahootClient.py - KahootClient Class](#kahootclientpy---kahootclient-class)
- [Player.py - Player Class](#playerpy---player-class)

---

## Server.py - my_server Class

### `__init__(self, port)`
**Description:** Constructor that initializes the Kahoot server.
- Creates a server socket and binds it to the specified port
- Initializes empty lists for players and clients
- Sets up game state variables (game_started, waiting_for_answers, current_correct_answer)

**Parameters:**
- `port` - The port number on which the server will listen for connections

---

### `run_server(self)`
**Description:** Main server loop that handles all client connections and messages.
- Uses select.select() to monitor multiple sockets efficiently without blocking
- Checks for new connections and incoming messages every 0.1 seconds
- Routes new connections to handle_new_connection()
- Routes client messages to handle_request()

**Returns:** None (runs indefinitely until stopped)

---

### `handle_new_connection(self)`
**Description:** Handles new client connections to the server.
- Accepts new client socket connections
- Adds the client socket to the clients list
- Sends a "NAME_REQUEST" message to ask for the player's name
- Prints connection confirmation to server console

**Returns:** None

---

### `find_player_by_socket(self, client_socket)`
**Description:** Searches for a player object using their socket connection.
- Iterates through the players list to find a matching socket
- Used to identify which player sent a message

**Parameters:**
- `client_socket` - The socket connection to search for

**Returns:** Player object if found, None if not found

---

### `handle_request(self, client_socket)`
**Description:** Processes incoming messages from clients.
- Receives and decodes messages from client sockets
- Handles multiple messages separated by newlines
- Routes messages based on type: START_GAME, QUESTION, STOP_GAME, or numeric answers
- Calls register_player() for new players
- Handles client disconnections

**Parameters:**
- `client_socket` - The socket that sent the message

**Returns:** None

---

### `register_player(self, client_socket, name)`
**Description:** Registers a new player in the game.
- Creates a new Player object with the provided name
- Assigns ADMIN role to the first player, PLAYER role to others
- Sends role confirmation to the client
- Broadcasts a system message announcing the new player

**Parameters:**
- `client_socket` - The socket connection of the new player
- `name` - The name chosen by the player

**Returns:** None

---

### `start_game(self)`
**Description:** Starts the game session.
- Sets game_started flag to True
- Broadcasts "GAME_STARTED" message to all connected clients
- Counts and displays the number of non-admin players
- Prints confirmation to server console

**Returns:** None

---

### `send_question(self, message)`
**Description:** Sends a question to all players (except admin).
- Parses the question message format: QUESTION:text|opt1|opt2|opt3|opt4|correct_answer
- Checks if there are players in the game
- Stores the correct answer internally
- Sends question without the correct answer to all non-admin players
- Initializes the waiting_for_answers dictionary

**Parameters:**
- `message` - The complete question string with format QUESTION:text|options|correct_answer

**Returns:** None

---

### `calculate_round_results(self)`
**Description:** Calculates and distributes results after all players have answered.
- Compares each player's answer with the correct answer
- Awards points to players who answered correctly
- Sends individual result messages (correct/wrong) to each player
- Creates a round summary with scores
- Sorts players by points and broadcasts the leaderboard
- Clears the waiting_for_answers dictionary for the next round

**Returns:** None

---

### `handle_answer(self, player, answer)`
**Description:** Processes a player's answer to a question.
- Stores the player's answer in the waiting_for_answers dictionary
- Tracks how many players have answered
- Checks if all players have answered
- Calls calculate_round_results() when all answers are received

**Parameters:**
- `player` - The Player object who submitted the answer
- `answer` - The answer string (typically "1", "2", "3", or "4")

**Returns:** None

---

### `stop_game(self)`
**Description:** Stops the game and displays final statistics.
- Sets game_started flag to False
- Collects all non-admin players
- Sorts players by points (highest to lowest)
- Creates a formatted game over message with final scores
- Announces the winner
- Broadcasts the final statistics to all clients

**Returns:** None

---

### `broadcast(self, message)`
**Description:** Sends a message to all connected clients.
- Iterates through all client sockets
- Encodes and sends the message to each client
- Handles send errors silently (skips failed sends)

**Parameters:**
- `message` - The text message to broadcast

**Returns:** None

---

### `remove_client(self, client_socket)`
**Description:** Removes a disconnected client from the server.
- Finds the associated Player object
- Removes the player from the players list
- Removes the socket from the clients list
- Closes the socket connection
- Prints disconnection message to server console

**Parameters:**
- `client_socket` - The socket connection to remove

**Returns:** None

---

## KahootClient.py - KahootClient Class

### `__init__(self, ip, port)`
**Description:** Constructor that initializes the Kahoot client and connects to the server.
- Creates a socket connection
- Connects to the server at the specified IP and port
- Initializes client state variables (is_admin, running, role_received)
- Prints connection confirmation

**Parameters:**
- `ip` - Server IP address to connect to
- `port` - Server port number to connect to

---

### `send_message(self, message)`
**Description:** Sends a message to the server.
- Encodes the message string to bytes
- Sends it through the client socket
- Handles errors with error message printing

**Parameters:**
- `message` - The text message to send to the server

**Returns:** None

---

### `receive_message(self)`
**Description:** Receives a message from the server.
- Receives up to 1024 bytes from the server
- Decodes the bytes to a string
- Returns None if an error occurs

**Returns:** The received message string, or None on error

---

### `listen_to_server(self)`
**Description:** Continuously listens for messages from the server (runs in a thread).
- Receives messages in a loop
- Handles disconnections
- Routes messages based on type: NAME_REQUEST, ROLE, SYSTEM, GAME_STARTED, QUESTION, RESULT, GAME_OVER
- Manages the client's state based on server messages

**Returns:** None (runs until client disconnects)

---

### `handle_question(self, message)`
**Description:** Processes and displays a question received from the server.
- Parses the question format: QUESTION:text|option1|option2|option3|option4
- Displays the question text
- Displays numbered options (1-4)
- Formats output for user readability

**Parameters:**
- `message` - The question message from the server

**Returns:** None

---

### `admin_control(self)`
**Description:** Admin interface for managing the game.
- Accepts admin commands: start, question, stop
- Sends START_GAME command to begin the game
- Allows admin to create and send questions with 4 options
- Prompts for the correct answer after sending a question
- Sends STOP_GAME command to end the game

**Returns:** None

---

### `player_control(self)`
**Description:** Player interface for answering questions.
- Waits for user input
- Validates answers (must be 1, 2, 3, or 4)
- Sends valid answers to the server
- Ignores empty input
- Shows error for invalid input

**Returns:** None

---

### `start(self)`
**Description:** Starts the client application.
- Creates and starts a daemon thread for listening to the server
- Waits for role assignment from the server
- Routes to admin_control() if the user is admin
- Routes to player_control() if the user is a regular player
- Closes the socket when finished

**Returns:** None

---

## Player.py - Player Class

### `__init__(self, name, points, admin, client_socket, addr)`
**Description:** Constructor that creates a new Player object.
- Stores player's name, points, and admin status
- Stores the client's socket connection and address

**Parameters:**
- `name` - Player's name
- `points` - Initial points (usually 0)
- `admin` - Boolean indicating if player is admin
- `client_socket` - The socket connection for this player
- `addr` - The network address of the player

---

### `GetPoints(self)`
**Description:** Returns the player's current point total.

**Returns:** Integer representing the player's points

---

### `SetPoints(self, num)`
**Description:** Sets the player's points to a specific value.

**Parameters:**
- `num` - The new point value

**Returns:** None

---

### `AddPoint(self)`
**Description:** Adds one point to the player's score.
- Used when a player answers a question correctly

**Returns:** None

---

### `RemPoint(self)`
**Description:** Removes one point from the player's score.
- Can be used for penalties (currently not used in the game)

**Returns:** None

---

### `GetName(self)`
**Description:** Returns the player's name.

**Returns:** String containing the player's name

---

### `SetName(self, name)`
**Description:** Changes the player's name.

**Parameters:**
- `name` - The new name for the player

**Returns:** None

---

### `IsAdmin(self)`
**Description:** Checks if the player has admin privileges.

**Returns:** Boolean - True if admin, False if regular player

---

## Project Structure Summary

- **Server.py** - Main server application that manages the game
- **KahootClient.py** - Client application for both admin and players
- **Player.py** - Data class representing a player in the game

## Message Protocol

The application uses a text-based protocol with the following message types:

- `NAME_REQUEST` - Server asks client for name
- `ROLE:ADMIN` / `ROLE:PLAYER` - Server assigns role
- `START_GAME` - Admin starts the game
- `QUESTION:text|opt1|opt2|opt3|opt4` - Question with options
- `RESULT:message` - Result of answer (correct/wrong)
- `ROUND_OVER:summary` - End of round with scores
- `GAME_OVER:stats` - Game ended with final statistics
- `SYSTEM:message` - System announcements
