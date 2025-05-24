import random
import time
import os
import threading
from datetime import datetime

try:
    import winsound  # Windows-only
    sound_available = True
except ImportError:
    sound_available = False

high_score_file = "highscore.txt"
history_file = "game_history.txt"

def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            return int(file.read())
    return 0

def save_high_score(score):
    with open(high_score_file, "w") as file:
        file.write(str(score))

def play_sound(win):
    if sound_available:
        if win:
            winsound.Beep(1000, 300)
        else:
            winsound.Beep(400, 300)

def get_difficulty():
    print("\nChoose difficulty level:")
    print("1. Easy (1–10)")
    print("2. Medium (1–100)")
    print("3. Hard (1–1000)")
    choice = input("Enter 1, 2, or 3: ")
    if choice == '1':
        return 10
    elif choice == '2':
        return 100
    elif choice == '3':
        return 1000
    else:
        print("Invalid choice, defaulting to Medium.")
        return 100

def input_with_timeout(prompt, timeout=10):
    guess = [None]

    def get_input():
        guess[0] = input(prompt)

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print("\nTime's up! You took too long.\n")
        return None
    return guess[0]

def log_history(name, score, max_number, new_high):
    difficulty = {
        10: "Easy",
        100: "Medium",
        1000: "Hard"
    }.get(max_number, "Unknown")

    with open(history_file, "a") as log:
        log.write(f"{datetime.now()} | Player: {name} | Difficulty: {difficulty} | Score: {score} | New High Score: {'Yes' if new_high else 'No'}\n")

def view_history():
    if os.path.exists(history_file):
        print("\n--- Game History ---")
        with open(history_file, "r") as file:
            print(file.read())
    else:
        print("\nNo history found.")

def get_leaderboard():
    leaderboard = {}

    # Reading the game history and calculating top scores for each player
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            history_lines = file.readlines()
            for line in history_lines:
                data = line.strip().split(" | ")
                player_name = data[1].split(': ')[1]
                score = int(data[3].split(': ')[1])

                if player_name not in leaderboard:
                    leaderboard[player_name] = score
                else:
                    leaderboard[player_name] = max(leaderboard[player_name], score)

    return leaderboard

def export_history_to_html():
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            history_lines = file.readlines()

        leaderboard = get_leaderboard()

        html_content = """
        <html>
        <head>
            <title>Game History and Leaderboard</title>
            <style>
                table {width: 100%; border-collapse: collapse; margin-bottom: 20px;}
                th, td {border: 1px solid black; padding: 8px; text-align: left;}
                th {background-color: #f2f2f2;}
                .leaderboard {margin-top: 30px;}
            </style>
        </head>
        <body>
            <h1>Game History</h1>
            <table>
                <tr><th>Date & Time</th><th>Player</th><th>Difficulty</th><th>Score</th><th>New High Score</th></tr>
        """

        for line in history_lines:
            data = line.strip().split(" | ")
            html_content += f"<tr><td>{data[0]}</td><td>{data[1].split(': ')[1]}</td><td>{data[2].split(': ')[1]}</td><td>{data[3].split(': ')[1]}</td><td>{data[4].split(': ')[1]}</td></tr>"

        html_content += """
            </table>

            <div class="leaderboard">
                <h2>Leaderboard</h2>
                <table>
                    <tr><th>Player</th><th>High Score</th></tr>
        """

        # Sorting leaderboard by score in descending order
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
        for player, score in sorted_leaderboard:
            html_content += f"<tr><td>{player}</td><td>{score}</td></tr>"

        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        with open("game_history_and_leaderboard.html", "w") as html_file:
            html_file.write(html_content)
        print("\nHistory and Leaderboard have been exported to game_history_and_leaderboard.html")
    else:
        print("\nNo history found to export.")

def play_game(name, high_score):
    max_number = get_difficulty()
    lives = 5
    score = 0

    print(f"\n{name}, you have {lives} lives. Guess the number between 1 and {max_number}. You have 10 seconds each round!\n")

    while lives > 0:
        number = random.randint(1, max_number)
        user_input = input_with_timeout("Enter your guess: ", timeout=10)

        if user_input is None:
            lives -= 1
            continue

        try:
            guess = int(user_input)
        except ValueError:
            print("Invalid input! Enter a number.\n")
            continue

        if 1 <= guess <= max_number:
            if guess == number:
                print("Correct!\n")
                play_sound(True)
                score += 1
            else:
                print(f"Wrong! The number was {number}. Hint: Try {'higher' if guess < number else 'lower'} next time.\n")
                play_sound(False)
                lives -= 1
        else:
            print(f"Out of range! Guess between 1 and {max_number}.\n")

    print(f"Game Over, {name}! Final score: {score}")

    new_high = False
    if score > high_score:
        print("New high score!")
        save_high_score(score)
        high_score = score
        new_high = True
    else:
        print(f"Current high score to beat: {high_score}\n")

    log_history(name, score, max_number, new_high)
    return high_score

def main():
    print("Welcome to the  Roulette Number Game!")
    name = input("Enter your name: ")

    while True:
        print("\nMenu:")
        print("1. Play Game")
        print("2. View History")
        print("3.  Leaderboard ")
        print("4. Quit")
        choice = input("Choose an option (1–4): ")

        if choice == '1':
            high_score = load_high_score()
            high_score = play_game(name, high_score)
        elif choice == '2':
            view_history()
        elif choice == '3':
            leaderboard = get_leaderboard()
            if leaderboard:
                print("\n--- Leaderboard ---")
                print(f"{'Player':<20}{'High Score':<10}")
                print("-" * 30)
                sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
                for player, score in sorted_leaderboard:
                    print(f"{player:<20}{score:<10}")
            else:
                print("\nNo leaderboard data found.")
        elif choice == '4':
            print(f"Goodbye, {name}! See you next time.")
            break
        else:
            print("Invalid choice. Try again.")

main()
