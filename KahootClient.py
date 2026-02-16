import socket
import threading
import time
class KahootClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
    
    def listen_to_server(self):
        """Listen for messages from the server"""
        while self.running:
            message = self.receive_message()
            
            if not message:
                print("Disconnected from server!")
                self.running = False
                break
            
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
                print("\n=== GAME STARTED! ===\n")
            
            elif message.startswith("QUESTION:"):
                self.handle_question(message)
            
            elif message == "ANSWER_RECEIVED":
                print("Your answer has been received!")
            
            elif message.startswith("RESULT:"):
                result = message.split(":",1)[1]
                print(f"\n{result}\n")
            
            elif message.startswith("GAME_OVER"):
                print("\n" + message)
                self.running = False
                break
    
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
    
    def admin_control(self):
        """Admin controls for managing the game"""
        print("Type a command (start/question/stop):")
        while self.running:
            command = input("> ")
            
            if command.lower() == "start":
                self.send_message("START_GAME")
                print("Game started! Now you can ask questions.\n")
            
            elif command.lower() == "question":
                print("\n--- Enter Question ---")
                question = input("Question: ")
                opt1 = input("Option 1: ")
                opt2 = input("Option 2: ")
                opt3 = input("Option 3: ")
                opt4 = input("Option 4: ")
                
                # Send question
                question_msg = f"QUESTION:{question}|{opt1}|{opt2}|{opt3}|{opt4}"
                self.send_message(question_msg)
                
                print("\n✓ Question sent! Wait a few seconds for players to answer...")
                print("Enter the correct answer number (1-4):")
                correct = input("Correct answer: ")
                
                # Send correct answer
                self.send_message(f"ANSWER:{correct}")
                print("✓ Points awarded!\n")
            
            elif command.lower() == "stop":
                self.send_message("STOP_GAME")
                print("Game stopped!")
                self.running = False
                break
            
            else:
                print("Unknown command! Use: start, question, or stop")
    
    def player_control(self):
        """Player controls for answering questions"""
        print("Waiting for questions... (Enter 1-4 when you see a question)\n")
        while self.running:
            answer = input()
            if answer in ["1", "2", "3", "4"]:
                self.send_message(answer)
            elif answer.strip() == "":
                continue  # Ignore empty input
            else:
                print("Invalid input! Enter 1, 2, 3, or 4 to answer questions.")
    
    def start(self):
        """Start the client"""
        # Start listening thread
        listen_thread = threading.Thread(target=self.listen_to_server)
        listen_thread.daemon = True
        listen_thread.start()
        
        # Wait until role is received
        print("Waiting for role assignment...")
        while not self.role_received and self.running:
            time.sleep(0.1)
        
        # Start control based on role
        if self.is_admin:
            self.admin_control()
        else:
            self.player_control()
        
        self.client_socket.close()


if __name__ == "__main__":
    ip = input("Enter server IP (press Enter for localhost): ")
    if not ip:
        ip = "127.0.0.1"
    
    port = input("Enter server port (press Enter for 12345): ")
    if not port:
        port = 12345
    else:
        port = int(port)
    
    client = KahootClient(ip, port)
    client.start()
