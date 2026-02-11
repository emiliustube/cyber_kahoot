import comm_utils
import select
import socket
from Player import Player

class my_server:
    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(5)
        self.players = []
        self.clients = []
        self.game_started = False
        self.waiting_for_answers = {}
        self.current_correct_answer = None

    def run_server(self):
        print("Kahoot Server is now listening...")

        while True:
            sockets, _, _ = select.select(self.clients + [self.server_socket], [], [], 0.1)

            for soc in sockets:
                if soc == self.server_socket:
                    self.handle_new_connection()
                else:
                    self.handle_request(soc)

        self.server_socket.close()

    def handle_new_connection(self):
        """Handle new client connections"""
        client_socket, addr = self.server_socket.accept()
        self.clients.append(client_socket)
        
        # Ask for name
        comm_utils.send_message(client_socket, "NAME_REQUEST")
        print(f"New client connected from {addr}")

    def find_player_by_socket(self, client_socket):
        """Find player by their socket"""
        for player in self.players:
            if player.client_socket == client_socket:
                return player
        return None

    def handle_request(self, client_socket):
        """Handle messages from clients"""
        message = comm_utils.receive_message(client_socket)

        if not message:
            # Client disconnected
            self.remove_client(client_socket)
            return

        player = self.find_player_by_socket(client_socket)
        
        # If player doesn't exist yet, this is their name
        if player is None:
            self.register_player(client_socket, message)
            return

        # Handle different message types
        if message.startswith("START_GAME") and player.IsAdmin():
            self.start_game()
        elif message.startswith("QUESTION:") and player.IsAdmin():
            self.send_question(message)
        elif message.startswith("ANSWER:") and player.IsAdmin():
            self.set_correct_answer(message)
        elif message.startswith("STOP_GAME") and player.IsAdmin():
            self.stop_game()
        elif message.isdigit() and self.game_started:
            # Player answered a question
            self.handle_answer(player, message)

    def register_player(self, client_socket, name):
        """Register a new player with their name"""
        is_admin = len(self.players) == 0
        player = Player(name, 0, is_admin, client_socket, None)
        self.players.append(player)
        
        if is_admin:
            comm_utils.send_message(client_socket, "ROLE:ADMIN")
            print(f"Player '{name}' joined as ADMIN")
        else:
            comm_utils.send_message(client_socket, "ROLE:PLAYER")
            print(f"Player '{name}' joined as PLAYER")
        
        # Notify all players
        self.broadcast(f"SYSTEM:{name} joined the game!")

    def start_game(self):
        """Start the game"""
        self.game_started = True
        self.broadcast("GAME_STARTED")
        print("Game has started!")

    def send_question(self, message):
        """Send question to all players"""
        # Format: QUESTION:question_text|option1|option2|option3|option4
        question_data = message.split(":", 1)[1]
        self.waiting_for_answers = {}
        self.broadcast(f"QUESTION:{question_data}")
        print(f"Question sent: {question_data}")

    def set_correct_answer(self, message):
        """Admin sets the correct answer and calculates points"""
        # Format: ANSWER:1 (where 1 is the correct answer number)
        correct = message.split(":")[1]
        self.current_correct_answer = correct
        
        # Check all answers and award points
        for player in self.players:
            if player.IsAdmin():
                continue
            
            if player.client_socket in self.waiting_for_answers:
                player_answer = self.waiting_for_answers[player.client_socket]
                if player_answer == correct:
                    player.AddPoint()
                    comm_utils.send_message(player.client_socket, "RESULT:Correct! +1 point")
                    print(f"{player.GetName()} answered correctly!")
                else:
                    comm_utils.send_message(player.client_socket, "RESULT:Wrong answer!")
                    print(f"{player.GetName()} answered wrong.")
        
        # Clear answers for next question
        self.waiting_for_answers = {}
        self.current_correct_answer = None

    def handle_answer(self, player, answer):
        """Handle player's answer"""
        if not player.IsAdmin():
            self.waiting_for_answers[player.client_socket] = answer
            print(f"{player.GetName()} answered: {answer}")
            comm_utils.send_message(player.client_socket, "ANSWER_RECEIVED")

    def stop_game(self):
        """Stop the game and show statistics"""
        self.game_started = False
        
        # Sort players by points
        sorted_players = sorted([p for p in self.players if not p.IsAdmin()], 
                                key=lambda x: x.GetPoints(), reverse=True)
        
        # Create statistics message
        stats = "GAME_OVER\n=== FINAL SCORES ===\n"
        for i, player in enumerate(sorted_players, 1):
            stats += f"{i}. {player.GetName()}: {player.GetPoints()} points\n"
        
        if sorted_players:
            stats += f"\nWINNER: {sorted_players[0].GetName()}!"
        
        self.broadcast(stats)
        print("\n" + stats)

    def broadcast(self, message):
        """Send message to all connected clients"""
        for client in self.clients:
            comm_utils.send_message(client, message)

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
    port = 12345
    server = my_server(port)
    print(f"Starting Kahoot Server on port {port}...")
    server.run_server()

            