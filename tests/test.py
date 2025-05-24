import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.history import ChatHistory
from config.config import LOG_FILE_NAME

def print_all_database_rows():
    chat_history = ChatHistory()
    rows = chat_history.get_all_history()
    
    print("\n=== Database Contents ===")
    print("Total rows:", len(rows))
    print("-" * 80)
    
    for row in rows:
        question, answer, timestamp = row
        print(f"Timestamp: {timestamp}")
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print("-" * 80)

def clear_database():
    chat_history = ChatHistory()
    if chat_history.clear_history():
        print("\n=== Database Cleared Successfully ===")
        print("All records have been deleted.")
    else:
        print("\n=== Error Clearing Database ===")
        print("Failed to clear the database.")

def clear_log_file():
    try:
        with open(LOG_FILE_NAME, 'w') as file:
            file.truncate(0)
        print("Đã làm sạch file log thành công!")
    except Exception as e:
        print(f"Lỗi khi làm sạch file log: {e}")

if __name__ == "__main__":
    # Add a menu for user interaction
    print("\n1. View history questions and answers")
    print("2. Clear history questions and answers")
    print("3. Clear log file")
    choice = input("Enter your choice (1, 2 or 3): ")
    
    if choice == "1":
        print_all_database_rows()
    elif choice == "2":
        clear_database()
    elif choice == "3":
        clear_log_file()
    else:
        print("Invalid choice!")