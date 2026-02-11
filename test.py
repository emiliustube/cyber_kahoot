# Quick Test Instructions
# 
# To test the Kahoot game:
#
# 1. Open a terminal and run: python Server.py
# 2. Open another terminal and run: python KahootClient.py (this will be admin)
# 3. Open more terminals and run: python KahootClient.py (these will be players)
#
# Example game flow:
# Admin:
#   - Type: start
#   - Type: question
#   - Enter: "What is the capital of France?"
#   - Enter: "London", "Paris", "Berlin", "Madrid"
#   - Wait for players to answer
#   - Enter: 2 (correct answer)
#   - Type: stop (to end game)

print("Run Server.py first, then run KahootClient.py in multiple terminals!")
