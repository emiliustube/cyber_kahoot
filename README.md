# Cyber Kahoot Game

A simple Kahoot-like quiz game for multiple players using Python sockets.

## How to Play

### Step 1: Start the Server
Run the server first:
```
python Server.py
```

The server will start listening on port 12345.

### Step 2: Connect Players
Open multiple terminal windows (one for each player) and run:
```
python KahootClient.py
```

When prompted:
- Press Enter to use localhost (127.0.0.1)
- Press Enter to use default port (12345)
- Enter your name

### Step 3: Admin Controls
The **first player** to connect becomes the **ADMIN**.

Admin commands:
- Type `start` - Start the game
- Type `stop` - End the game and show final scores

### Step 4: Player Controls
Regular players wait for questions and type their answer (1-4).

## Game Flow Example

1. Admin types: `start`
2. Admin types: `question`
   - Question: "What is 2+2?"
   - Option 1: "3"
   - Option 2: "4"
   - Option 3: "5"
   - Option 4: "6"
   - Correct answer: "2"
3. Players see the question and type their answers (1, 2, 3, or 4)
4. Players get points for correct answers
5. Admin can ask more questions or type `stop` to end the game
6. Final scores are shown to everyone

## Files
- `Server.py` - The game server
- `KahootClient.py` - The client that players use
- `Player.py` - Player data class

## Requirements
- Python 3.x
- No external packages needed (uses only standard library)
