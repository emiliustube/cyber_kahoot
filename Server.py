import select
import socket
from Player import Player

class my_server:
    def __init__(self, port):
        self.server_socket = socket.socket()
        self.server_socket.bind(('', port))
        self.server_socket.listen()
        self.players = []
        self.clients = []
        self.game_started = False
        self.waiting_for_answers = {}
        self.current_correct_answer = None

    def run_server(self):
        print("Kahoot Server is now listening...")

        while True:
            ready_to_read = self.clients + [self.server_socket]
            # We use select.select here to efficiently wait/until network sockets are ready for reading,
            # without blocking the whole server forever.
            # Arguments:
            #   - ready_to_read: the list of sockets we want to check for incoming data (clients + the server socket)
            #   - []: we don't care about sockets ready for writing right now
            #   - []: we don't care about sockets with errors right now
            #   - 0.1: timeout in seconds -- so the server tick loops every 0.1s if nothing happens (non-blocking)
            # select.select returns 3 lists; we only care about the first: readable sockets, so we grab [0].
            readable_sockets = select.select(ready_to_read, [], [], 0.1)[0]

            for socket_with_data in readable_sockets:
                if socket_with_data == self.server_socket:
                    self.handle_new_connection()
                else:
                    self.handle_request(socket_with_data)

        self.server_socket.close()

    def handle_new_connection(self):
        """Handle new client connections"""
        client_socket, addr = self.server_socket.accept()
        self.clients.append(client_socket)
        
        # Ask for name
        client_socket.send("NAME_REQUEST\n".encode())
        print(f"New client connected from {addr}")

    def find_player_by_socket(self, client_socket):
        """Find player by their socket"""
        for player in self.players:
            if player.client_socket == client_socket:
                return player
        return None

    def handle_request(self, client_socket):
        """Handle messages from clients"""
        try:
            data = client_socket.recv(1024).decode()
        except:
            data = None

        if not data:
            # Client disconnected
            self.remove_client(client_socket)
            return

        # Handle multiple messages separated by newlines
        messages = data.strip().split('\n') # strip - מוחק רווחים  split - מחלק לשורות את הרווחים
        
        for message in messages:
            message = message.strip()
            if not message:
                continue
            
            print(f"Received message: '{message}' from client")
                
            player = self.find_player_by_socket(client_socket)
            
            # If player doesn't exist yet, this is their name
            if player is None:
                self.register_player(client_socket, message)
                continue

            # Handle different message types
            if message.startswith("START_GAME") and player.IsAdmin():
                self.start_game()
            elif message.startswith("QUESTION:") and player.IsAdmin():
                self.send_question(message)
            elif message.startswith("STOP_GAME") and player.IsAdmin():
                self.stop_game()
            elif message.isdigit() and self.game_started:
                # Player answered a question
                print(f"Detected answer: {message} from {player.GetName()}")
                self.handle_answer(player, message)
            else:
                print(f"Unknown message type: '{message}'")

    def register_player(self, client_socket, name):
        """Register a new player with their name"""
        is_admin = len(self.players) == 0
        player = Player(name, 0, is_admin, client_socket, None)
        self.players.append(player)
        
        if is_admin:
            client_socket.send("ROLE:ADMIN\n".encode())
            print(f"Player '{name}' joined as ADMIN")
        else:
            client_socket.send("ROLE:PLAYER\n".encode())
            print(f"Player '{name}' joined as PLAYER")
            # Notify only non-admin players about new player
            self.broadcast_to_players(f"SYSTEM:{name} joined the game!")

    def start_game(self):
        """Start the game"""
        self.game_started = True
        self.broadcast("GAME_STARTED")
        non_admin_count = 0
        for p in self.players:
            if not p.IsAdmin():
                non_admin_count += 1
        print(f"Game has started! {non_admin_count} players in the game.")

    def send_question(self, message):
        """Send question to all players"""
        # Format: QUESTION:question_text|option1|option2|option3|option4|correct_answer
        # We split the message only at the first ":" using split(":", 1)
        # This handles cases where ":" may appear in the question text.
        # The result is a list: [prefix, the_rest], so [1] extracts everything after the first ":".
        question_data = message.split(":", 1)[1]
        parts = question_data.split("|")
        
        if len(parts) == 6:
            # Check how many players are in the game (excluding admin)
            non_admin_players = []
            for p in self.players:
                if not p.IsAdmin():
                    non_admin_players.append(p)
            
            if len(non_admin_players) == 0:
                print("ERROR: No players in the game! Wait for players to join.")
                # Send error message to admin
                admin = None
                for p in self.players:
                    if p.IsAdmin():
                        admin = p
                        break
                admin.client_socket.send("ROUND_OVER:\n⚠️ No players in the game! Wait for players to join first.\n\n".encode())
                return
            
            # Extract correct answer and store it
            self.current_correct_answer = parts[5]
            # Send question without the answer to players
            question_to_send = "|".join(parts[0:5])
            self.waiting_for_answers = {}
            
            # Only send to non-admin players
            for player in non_admin_players:
                try:
                    player.client_socket.send(f"QUESTION:{question_to_send}\n".encode())
                except:
                    pass
            
            print(f"Question sent to {len(non_admin_players)} players: {parts[0]}")
            print(f"Correct answer: {self.current_correct_answer}")
            waiting_names = []
            for p in non_admin_players:
                waiting_names.append(p.GetName())
            print(f"Waiting for players: {waiting_names}")


    def calculate_round_results(self):
        """Calculate results after all players answered"""
        print("\nAll players answered! Calculating results...")
        
        correct_count = 0
        wrong_count = 0
        
        # Check each player's answer
        for player in self.players:
            if player.IsAdmin():
                continue
            
            if player.client_socket in self.waiting_for_answers:
                player_answer = self.waiting_for_answers[player.client_socket]
                
                if player_answer == self.current_correct_answer:
                    player.AddPoint()
                    player.client_socket.send("RESULT:✓ Correct! +1 point\n".encode())
                    print(f"  ✓ {player.GetName()} answered correctly!")
                    correct_count += 1
                else:
                    player.client_socket.send("RESULT:✗ Wrong answer!\n".encode())
                    print(f"  ✗ {player.GetName()} answered wrong.")
                    wrong_count += 1
        
        round_summary = f"\n--- ROUND RESULTS ---\n"
        round_summary += f"Correct answers: {correct_count}\n"
        round_summary += f"Wrong answers: {wrong_count}\n\n"
        round_summary += "Current Scores:\n"
        
        # Sort players by points (from highest to lowest)
        # First, collect all non-admin players
        non_admin_players = []
        for p in self.players:
            if not p.IsAdmin():
                non_admin_players.append(p)
        
        # Sort using manual comparison - bubble sort
        sorted_players = non_admin_players.copy()
        for i in range(len(sorted_players)):
            for j in range(i + 1, len(sorted_players)):
                # If player at position i has fewer points than player at position j, swap them
                if sorted_players[i].GetPoints() < sorted_players[j].GetPoints():
                    # Swap the players
                    temp = sorted_players[i]
                    sorted_players[i] = sorted_players[j]
                    sorted_players[j] = temp
        
        for player in sorted_players:
            round_summary += f"{player.GetName()}: {player.GetPoints()} points\n"
        
        # Send round summary to everyone
        self.broadcast(f"ROUND_OVER:{round_summary}")
        
        # Clear answers for next question
        self.waiting_for_answers = {}
        self.current_correct_answer = None
        
        print("Round complete!\n")

    def handle_answer(self, player, answer):
        """Handle player's answer"""
        if not player.IsAdmin():
            self.waiting_for_answers[player.client_socket] = answer
            print(f"{player.GetName()} answered: {answer}")
            
            # Check if all players have answered
            non_admin_players = []
            for p in self.players:
                if not p.IsAdmin():
                    non_admin_players.append(p)
            answered_count = len(self.waiting_for_answers)
            total_players = len(non_admin_players)
            
            print(f"Progress: {answered_count}/{total_players} players answered")
            
            if answered_count == total_players:
                # All players answered - calculate results
                print("All players have answered! Calculating results...")
                self.calculate_round_results()
            else:
                print(f"Still waiting for {total_players - answered_count} more players...")

    def stop_game(self):
        """Stop the game and show statistics"""
        self.game_started = False
        
        # Sort players by points (from highest to lowest)
        # First, collect all non-admin players
        non_admin_players = []
        for p in self.players:
            if not p.IsAdmin():
                non_admin_players.append(p)
        
        # Sort using manual comparison - bubble sort
        sorted_players = non_admin_players.copy()
        for i in range(len(sorted_players)):
            for j in range(i + 1, len(sorted_players)):
                # If player at position i has fewer points than player at position j, swap them
                if sorted_players[i].GetPoints() < sorted_players[j].GetPoints():
                    # Swap the players
                    temp = sorted_players[i]
                    sorted_players[i] = sorted_players[j]
                    sorted_players[j] = temp
        
        # Create statistics message
        stats = "\n" + "="*50 + "\n"
        stats += "           🎮 GAME OVER 🎮\n"
        stats += "="*50 + "\n\n"
        stats += "=== FINAL SCORES ===\n"
        
        i = 1
        for player in sorted_players:
            stats += f"{i}. {player.GetName()}: {player.GetPoints()} points\n"
            i += 1
        
        if sorted_players:
            stats += f"\n🏆 WINNER: {sorted_players[0].GetName()}! 🏆\n"
        else:
            stats += "\nNo players participated.\n"
        
        stats += "\n" + "="*50
        
        # Send to everyone
        self.broadcast(f"GAME_OVER:{stats}")
        
        # Print on server
        print(stats)

    def broadcast(self, message):
        """Send message to all connected clients"""
        for client in self.clients:
            try:
                client.send((message + "\n").encode())
            except:
                pass
    
    def broadcast_to_players(self, message):
        """Send message only to non-admin players"""
        for player in self.players:
            if not player.IsAdmin():
                try:
                    player.client_socket.send((message + "\n").encode())
                except:
                    pass

    def remove_client(self, client_socket):
        """Remove disconnected client"""
        player = self.find_player_by_socket(client_socket)
        if player:
            print(f"Player '{player.GetName()}' disconnected")
            self.players.remove(player)
        
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()


if __name__ == "__main__":
    port = 12346
    server = my_server(port)
    print(f"Starting Kahoot Server on port {port}...")
    server.run_server()