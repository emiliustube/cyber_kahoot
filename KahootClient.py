import socket
import time
import select
import sys
class KahootClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket()
        self.client_socket.connect((ip, port))
        self.is_admin = False
        self.running = True
        self.role_received = False
        print("Connected to Kahoot server!")
        
    def send_message(self, message):
        """Send a message to the server"""
        try:
            self.client_socket.send(message.encode())
        except:
            print("Error sending message!")
    
    def receive_message(self):
        """Receive a message from the server"""
        try:
            data = self.client_socket.recv(1024).decode()
            return data
        except:
            return None
    
    def process_server_message(self, data):
        """Process messages from the server"""
        if not data:
            print("Disconnected from server!")
            self.running = False
            return
        
        # Check for multi-line messages first (GAME_OVER and ROUND_OVER)
        if "GAME_OVER:" in data:
            # Extract everything after GAME_OVER: as a single message
            game_over_content = data.split("GAME_OVER:", 1)[1]
            print(game_over_content)
            self.running = False
            return
        
        if "ROUND_OVER:" in data:
            # Extract everything after ROUND_OVER: as a single message
            round_over_content = data.split("ROUND_OVER:", 1)[1]
            print(f"\n{round_over_content}\n")
            # Continue processing any remaining messages
            data = data.split("ROUND_OVER:", 1)[0]
        
        # Handle multiple messages that might arrive together
        messages = data.split('\n')
        
        for message in messages:
            message = message.strip()
            if not message:
                continue
            
            # Handle different message types
            if message == "NAME_REQUEST":
                name = input("Enter your name: ")
                self.send_message(name)
            
            elif message.startswith("ROLE:"):
                role = message.split(":")[1]
                if role == "ADMIN":
                    self.is_admin = True
                    print("\n*** You are the ADMIN! ***")
                    print("Commands:")
                    print("  - Type 'start' to start the game")
                    print("  - Type 'question' to ask a question")
                    print("  - Type 'stop' to end the game\n")
                else:
                    print("\n*** You are a PLAYER! Wait for admin to start the game ***\n")
                self.role_received = True
            
            elif message.startswith("SYSTEM:"):
                print(message.split(":", 1)[1])
            
            elif message == "GAME_STARTED":
                if not self.is_admin:
                    print("\n=== GAME STARTED! ===\n")
            
            elif message.startswith("QUESTION:"):
                self.handle_question(message)
            
            elif message == "ANSWER_RECEIVED":
                print("Your answer has been received!")
            
            elif message.startswith("RESULT:"):
                result = message.split(":",1)[1]
                print(f"\n{result}\n")
    
    def handle_question(self, message):
        """Handle a question from the server"""
        # Format: QUESTION:question_text|option1|option2|option3|option4
        question_data = message.split(":",1)[1]
        parts = question_data.split("|")
        
        if len(parts) == 5:
            question = parts[0]
            options = parts[1:5]
            
            print(f"\n=== QUESTION ===")
            print(question)
            i = 1
            for option in options:
                print(f"{i}. {option}")
                i += 1
            print()
    
    def handle_user_input(self, user_input):
        """Handle user input based on role"""
        if self.is_admin:
            if user_input.lower() == "start":
                self.send_message("START_GAME")
                print("\n=== GAME STARTED! ===\n")
                print("You will now enter questions for the quiz.\n")
                self.asking_questions = True
                self.question_step = 0
                
            elif user_input.lower() == "stop":
                self.send_message("STOP_GAME")
                print("Game stopped!")
                self.running = False
                
            elif self.asking_questions:
                # Handle question input step by step
                if self.question_step == 0:
                    self.current_question = user_input
                    if user_input.lower() in ['exit', 'quit', 'stop']:
                        print("\nExiting question mode...")
                        self.send_message("STOP_GAME")
                        self.running = False
                        self.asking_questions = False
                    else:
                        self.question_step = 1
                        print("Option 1: ", end='')
                elif self.question_step == 1:
                    self.opt1 = user_input
                    self.question_step = 2
                    print("Option 2: ", end='')
                elif self.question_step == 2:
                    self.opt2 = user_input
                    self.question_step = 3
                    print("Option 3: ", end='')
                elif self.question_step == 3:
                    self.opt3 = user_input
                    self.question_step = 4
                    print("Option 4: ", end='')
                elif self.question_step == 4:
                    self.opt4 = user_input
                    self.question_step = 5
                    print("Correct answer (1-4): ", end='')
                elif self.question_step == 5:
                    if user_input in ["1", "2", "3", "4"]:
                        question_msg = f"QUESTION:{self.current_question}|{self.opt1}|{self.opt2}|{self.opt3}|{self.opt4}|{user_input}"
                        self.send_message(question_msg)
                        print("\n✓ Question sent! Waiting for players to answer...")
                        print("(Results will appear automatically)\n")
                        self.question_step = 6
                        print("\nDo you want to ask another question?")
                        print("Type 'yes' to continue, or 'no' to end game: ", end='', flush=True)
                    else:
                        print("Invalid answer! Must be 1, 2, 3, or 4. Question not sent.")
                        self.question_step = 0
                        print("\n--- Enter Question ---")
                        print("Question: ", end='', flush=True)
                elif self.question_step == 6:
                    if user_input.lower() in ['yes', 'y']:
                        self.question_step = 0
                        print("\n--- Enter Question ---")
                        print("Question: ", end='', flush=True)
                    else:
                        print("\nEnding game...")
                        self.send_message("STOP_GAME")
                        self.running = False
                        self.asking_questions = False
            else:
                print("Unknown command! Type 'start' to begin or 'stop' to quit.")
        else:
            # Player mode
            if user_input in ["1", "2", "3", "4"]:
                self.send_message(user_input)
            elif user_input.strip() == "":
                pass  # Ignore empty input
            else:
                print("Invalid input! Enter 1, 2, 3, or 4 to answer questions.")
    
    def start(self):
        """Start the client without threading"""
        self.asking_questions = False
        self.question_step = 0
        
        # Wait until role is received
        print("Waiting for role assignment...")
        while not self.role_received and self.running:
            # Check for server messages
            readable = select.select([self.client_socket], [], [], 0.1)[0]
            if readable:
                data = self.receive_message()
                self.process_server_message(data)
        
        # Show initial prompt based on role
        if self.is_admin:
            print("Type 'start' to begin the game, or 'stop' to quit:")
            print("> ", end='', flush=True)
        else:
            print("Waiting for questions... (Enter 1-4 when you see a question)\n")
        
        # Main loop - check both server messages and user input
        while self.running:
            # Check if there's data from server or user input
            readable = select.select([self.client_socket, sys.stdin], [], [], 0.1)[0]
            
            for ready in readable:
                if ready == self.client_socket:
                    # Message from server
                    data = self.receive_message()
                    self.process_server_message(data)
                    
                elif ready == sys.stdin:
                    # User input
                    user_input = sys.stdin.readline().strip()
                    self.handle_user_input(user_input)
                    
                    # Show prompt again if needed
                    if self.running and self.is_admin and not self.asking_questions:
                        print("> ", end='', flush=True)
        
        self.client_socket.close()


if __name__ == "__main__":
    ip = input("Enter server IP (press Enter for localhost): ")
    if not ip:
        ip = "127.0.0.1"
    
    port = input("Enter server port (press Enter for 12345): ")
    if not port:
        port = 12346
    else:
        port = int(port)
    
    client = KahootClient(ip, port)
    client.start()
