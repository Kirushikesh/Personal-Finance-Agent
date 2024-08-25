import sqlite3
import random
from datetime import date, timedelta
from typing import Annotated, Literal, Optional, Any, List, Tuple
from autogen import ConversableAgent

from dotenv import load_dotenv

load_dotenv()

# Database setup function
def create_sample_database(database_name):
    def create_sqlite_database(filename):
        conn = None
        try:
            conn = sqlite3.connect(filename)
            print('Database Created Successfully')
        except sqlite3.Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def add_table(filename):
        try:
            conn = sqlite3.connect(filename)
            cursor = conn.cursor()
            cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        expense BOOLEAN NOT NULL
    )
    ''')
            conn.commit()
            conn.close()
            print('Table Created Successfully')
        except sqlite3.Error as e:
            print(e)
    
    def insert_random_data(filename):
        categories = ["Clothes", "Eating Out", "Entertainment", "Fuel", "General", "Gifts", "Holidays", "Kids", "Shopping", "Sports", "Travel", "Salary"]
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        def random_date():
            today = date.today()
            days_ago = random.randint(0, 365)
            return (today - timedelta(days=days_ago)).isoformat()

        def add_transaction(date, category, amount, description, expense):
            cursor.execute('''
            INSERT INTO transactions (date, category, amount, description, expense)
            VALUES (?, ?, ?, ?, ?)
            ''', (date, category, amount, description, expense))

        for _ in range(100):
            date = random_date()
            category = random.choice(categories)
            
            if category == "Salary":
                amount = round(random.uniform(2000, 5000), 2)
                expense = 0
                description = "Monthly salary"
            else:
                amount = round(random.uniform(5, 500), 2)
                expense = 1
                description = f"{category} expense"

            add_transaction(date, category, amount, description, expense)

        conn.commit()
        conn.close()
        print("100 random transactions have been added to the database.")

    create_sqlite_database(database_name)
    add_table(database_name)
    insert_random_data(database_name)

llm_config = {"model": "gpt-4o-mini"}
Available_Categories = Literal["Clothes", "Eating Out", "Entertainment", "Fuel", "General", "Gifts", "Holidays", "Kids", "Shopping", "Sports", "Travel", "Salary"]

# Store transaction agent setup
storage_assistant = ConversableAgent(
    name="Assistant",
    system_message=f"You are a helpful AI assistant. You help in adding expense/income information into the database. Today's date is {date.today()}. Try to automatically figure out the fields required to store based on the provided context, ask follow-up queries only if you can't make it yourself. Before termination ask user if they want to add any other transaction. Return 'TERMINATE' when the task is completed.",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

# Analyze agent setup
analysis_assistant = ConversableAgent(
    name="Assistant",
    system_message=f"""You are a helpful AI assistant. You help in analyzing user transactions and present useful insights back to the user. Today's date is {date.today()}. You should only use SELECT-based queries and not other types. If asked to enter, create, delete or perform other operations, let the user know it's not supported. Before termination ask user if they want to know any other information. Return 'TERMINATE' when the task is completed. 

    Below is the schema for the SQL database:

    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL (in rs),
        description TEXT,
        expense BOOLEAN NOT NULL
    )""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

# Store data function
@user_proxy.register_for_execution()
@storage_assistant.register_for_llm(name="store_data", description="It helps to save the expense/income in the database")
def store_data(expense: Annotated[bool,"Whether its an expense or income"],
               date: str, 
               category: Annotated[Available_Categories, "The category name"],
               amount: float,
               description: Annotated[str,'A short summary about the transaction']) -> str:
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (date, category, amount, description, expense)
    VALUES (?, ?, ?, ?, ?)''', (date, category, amount, description, expense))
    conn.commit()
    conn.close()
    return "Transaction added successfully."

@user_proxy.register_for_execution()
@analysis_assistant.register_for_llm(name="execute_sql", description="Function for executing SQL query and returning a response")
def execute_sql(query: Annotated[str, 'SQL query']) -> Optional[List[Tuple[Any, ...]]]:
    try:
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        cursor.execute(query)
        all_transactions = cursor.fetchall()
        conn.close()
        return all_transactions
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
# Main function to run the system
def main():
    while True:
        print("\nPersonal Finance Management System")
        print("1. Create/Reset Database")
        print("2. Store Transaction")
        print("3. Analyze Transactions")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            create_sample_database("transactions.db")
        elif choice == '2':
            storage_assistant.initiate_chat(
                user_proxy,
                message="Hey there, I'm here to help you store your transactions. Let me know what you earned or spent."
            )
        elif choice == '3':
            analysis_assistant.initiate_chat(
                user_proxy,
                message="Hey there, I'm here to help you analyze and provide insights on your spending. Let me know what you need to know?"
            )
        elif choice == '4':
            print("Thank you for using the Personal Finance Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()