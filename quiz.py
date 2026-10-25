
import json
import random
import sqlite3
import time
from datetime import datetime
from pathlib import Path

QUESTIONS_FILE = Path("questions.json")
DB_FILE = "highscores.db"
TIME_LIMIT = 15  

DEFAULT_QUESTIONS = [
    {"question": "What is the capital of France?", "options": ["Berlin", "Paris", "Madrid", "Rome"],
     "answer": "Paris", "category": "Geography", "difficulty": "easy"},
    {"question": "Which is the longest river in Africa?", "options": ["Congo", "Niger", "Nile", "Zambezi"],
     "answer": "Nile", "category": "Geography", "difficulty": "medium"},
    {"question": "Which language is this quiz written in?", "options": ["Java", "C++", "Python", "Ruby"],
     "answer": "Python", "category": "Programming", "difficulty": "easy"},
    {"question": "What does len([1, 2, 3]) return?", "options": ["2", "3", "4", "Error"],
     "answer": "3", "category": "Programming", "difficulty": "easy"},
    {"question": "What is the time complexity of binary search?", "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
     "answer": "O(log n)", "category": "Programming", "difficulty": "hard"},
    {"question": "What is 7 x 8?", "options": ["54", "56", "64", "49"],
     "answer": "56", "category": "Math", "difficulty": "easy"},
]

def load_questions():
    if not QUESTIONS_FILE.exists():
        QUESTIONS_FILE.write_text(json.dumps(DEFAULT_QUESTIONS, indent=2))
    return json.loads(QUESTIONS_FILE.read_text())

def init_db():
    with sqlite3.connect(DB_FILE) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS scores
                      (name TEXT, score INTEGER, total INTEGER, played_at TEXT)""")


def save_score(name, score, total):
    with sqlite3.connect(DB_FILE) as db:
        db.execute("INSERT INTO scores VALUES (?, ?, ?, ?)",
                   (name, score, total, datetime.now().strftime("%Y-%m-%d %H:%M")))


def show_high_scores(limit=5):
    with sqlite3.connect(DB_FILE) as db:
        rows = db.execute("SELECT name, score, total, played_at FROM scores "
                          "ORDER BY score * 1.0 / total DESC, played_at DESC LIMIT ?",
                          (limit,)).fetchall()
    print("\n--- High Scores ---")
    if not rows:
        print("No scores yet.")
    for i, (name, score, total, when) in enumerate(rows, 1):
        print(f"{i}. {name}: {score}/{total}  ({when})")

def get_choice(prompt, valid):
    """Keep asking until the user enters one of the valid choices."""
    while True:
        value = input(prompt).strip().upper()
        if value in valid:
            return value
        print(f"  Invalid input. Choose from: {', '.join(sorted(valid))}")


def pick_filters(questions):
    categories = sorted({q["category"] for q in questions})
    print("\nCategories:", ", ".join(categories), "| ALL")
    cat = get_choice("Pick a category: ", {c.upper() for c in categories} | {"ALL"})

    print("Difficulty: EASY, MEDIUM, HARD | ALL")
    diff = get_choice("Pick a difficulty: ", {"EASY", "MEDIUM", "HARD", "ALL"})

    return [q for q in questions
            if (cat == "ALL" or q["category"].upper() == cat)
            and (diff == "ALL" or q["difficulty"].upper() == diff)]

def run_quiz(questions):
    score = 0
    random.shuffle(questions)

    for i, q in enumerate(questions, 1):
        options = q["options"][:]
        random.shuffle(options)
        letters = [chr(65 + n) for n in range(len(options))]

        print(f"\nQ{i}. [{q['category']} / {q['difficulty']}] {q['question']}")
        for letter, opt in zip(letters, options):
            print(f"  {letter}. {opt}")

        start = time.time()
        choice = get_choice(f"Your answer ({TIME_LIMIT}s): ", set(letters))
        elapsed = time.time() - start

        correct_letter = letters[options.index(q["answer"])]
        if elapsed > TIME_LIMIT:
            print(f"Too slow ({elapsed:.1f}s). Correct answer: {correct_letter}. {q['answer']}")
        elif choice == correct_letter:
            print("Correct!")
            score += 1
        else:
            print(f"Wrong. Correct answer: {correct_letter}. {q['answer']}")

    return score


def main():
    init_db()
    all_questions = load_questions()
    name = input("Enter your name: ").strip() or "Player"

    while True:
        questions = pick_filters(all_questions)
        if not questions:
            print("No questions match that selection. Try again.")
            continue

        score = run_quiz(questions)
        print(f"\nFinal score: {score}/{len(questions)}")
        save_score(name, score, len(questions))
        show_high_scores()

        if get_choice("\nPlay again? (Y/N): ", {"Y", "N"}) == "N":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
