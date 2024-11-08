import sqlite3
import random
from datetime import date, timedelta
from typing import Annotated, Literal, Optional, Any, List, Tuple
from autogen import ConversableAgent,GroupChat,GroupChatManager,register_function
import autogen
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

        def add_transaction(rn_data, category, amount, description, expense):
            cursor.execute('''
            INSERT INTO transactions (date, category, amount, description, expense)
            VALUES (?, ?, ?, ?, ?)
            ''', (rn_data, category, amount, description, expense))

        for _ in range(100):
            rn_data = random_date()
            category = random.choice(categories)
            
            if category == "Salary":
                amount = round(random.uniform(2000, 5000), 2)
                expense = 0
                description = "Monthly salary"
            else:
                amount = round(random.uniform(5, 500), 2)
                expense = 1
                description = f"{category} expense"

            add_transaction(rn_data, category, amount, description, expense)
        conn.commit()
        conn.close()
        print("100 random transactions have been added to the database.")

    create_sqlite_database(database_name)
    add_table(database_name)
    # insert_random_data(database_name)

llm_config ={"config_list":[
    {"api_type":'ollama',
     "model":'qwen2.5:72b',
     "base_url":'http://localhost:11434/v1',
     "seed":42,
     "stream":False,
     "temperature":0.5,
    #  "top_p":0.9,
    #  "top_k":10,
     }
]}
Available_Categories = Literal["Clothes", "Eating Out", "Entertainment", "Fuel", "General", "Gifts", "Holidays", "Kids", "Shopping", "Sports", "Travel", "Salary"]

# Store transaction agent setup
storage_assistant = ConversableAgent(
    name="Assistant",
    system_message=f"""You are a helpful AI assistant. You help in adding expense/income information into the database. 
    Today's date is {date.today()}. Try to automatically figure out the fields required to store based on the provided context, 
    ask follow-up queries only if you can't make it yourself. Before termination ask user if they want to add any other transaction. 
    Say TERMINATE when you think the other agent has done the task.""",
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
    )
    List of available categories: {Available_Categories},
    provide the right operation.
    Say FINISH when the task is completed.""",
    llm_config=llm_config,
    human_input_mode="NEVER",
)

user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    # is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

# Store data function
@user_proxy.register_for_execution()
@storage_assistant.register_for_llm(name="store_data", description="It helps to save the expense/income in the database")
def store_data(expense: Annotated[bool,"Whether its an expense or income"],
               rn_data: str, 
               category: Annotated[Available_Categories, "The category name"],
               amount: float,
               description: Annotated[str,'A short summary about the transaction']) -> str:
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO transactions (date, category, amount, description, expense)
    VALUES (?, ?, ?, ?, ?)''', (rn_data, category, amount, description, expense))
    conn.commit()
    conn.close()
    return "Transaction added successfully."

@user_proxy.register_for_execution()
@analysis_assistant.register_for_llm(name="execute_sql", description="Function for executing SQL query and returning a response.")
def execute_sql(query: Annotated[str, 'SQL query']) -> Optional[List[Tuple[Any, ...]]]:
    # 这一个函数就可以实现增删改查功能，
    try:
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        # print(query)
        cursor.execute(query)

        all_transactions = cursor.fetchall()
        conn.close()
        return all_transactions
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
################################################## 有两个工具execute_sql和calculator，以及能执行本地代码   ############################
def calculator(a:float, b:float, operator:str) -> float:  # 被用于LLM的tool的函数，必须声明参数类型
    if operator=="+":
        return a+b
    elif operator=="-":
        return a-b
    elif operator=='*':
        return a*b
    elif operator=="/":
        return a/b  # 移除了 int() 转换，直接返回浮点数结果
    else:
        return ValueError("Invalid operator!")
# 先创建一个assistant和proxy
preference_assiatant=ConversableAgent(
    name='Pre_assistant',
    llm_config=llm_config,
    system_message=f""""You are a helpful AI assistant. You help in analyzing  and visualizing user transactions and provide the user's preference about Consumption Habits and Preference. Today's date is {date.today()}.
    You have a tool execute right SQL query sentence and you have no limit times to use this tool .
    Also ,you have a tool for calculating the result of a mathematical operation, include +,-,*,/..
    Rember You can use the stastics to visualize the user's consumption habits and preference and give right python code block to visualize only the user want to see a figure!
    Return 'TERMINATE' when the task is completed. 
    Below is the schema for the SQL database:

    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL (in rs),
        description TEXT,
        expense BOOLEAN NOT NULL
    )
    List of available categories: {Available_Categories},
    When providing the executable python code block or other tools , must give the right format.
    Do not ask any requirement from user!
    Say TERMINATE when you think the other agent has done the task!
     """
)
# Rember You can use the stastics to visualize the user's consumption habits and preference and give right python code block to visualize only the user want to see a figure!
preference_proxy=ConversableAgent(
    name="Pre_proxy",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding_personal_finance")},
    human_input_mode="NEVER"
)
# 注册查询工具，
@preference_proxy.register_for_execution()
@preference_assiatant.register_for_llm(name="execute_sql", description="Function for executing SQL query and returning a response.")
def execute_sql(query: Annotated[str, 'SQL query']) -> Optional[List[Tuple[Any, ...]]]:
    # 这一个函数就可以实现增删改查功能，不用改动，直接拿来用
    try:
        conn = sqlite3.connect("transactions.db")
        cursor = conn.cursor()
        # print(query)
        cursor.execute(query)

        all_transactions = cursor.fetchall()
        conn.close()
        return all_transactions
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
register_function(calculator,
                  caller=preference_assiatant,
                  executor=preference_proxy,
                  name='calculator',
                  description="Function for calculating the result of a mathematical operation, include +,-,*,/."
                  )
# register_function(store_data,
#                   caller=preference_assiatant,
#                   executor=preference_proxy,
#                   name='store_data',
#                   description="Function for saving the expense/income in the database"
#                   )
group_chat_pre=GroupChat(
    agents=[preference_assiatant,preference_proxy],
    messages=[],
    max_round=8,    # 6
    speaker_selection_method="round_robin",
)
group_chat_manager=GroupChatManager(
    groupchat=group_chat_pre,
    llm_config=llm_config,
    # silent=True,
    human_input_mode="NEVER"
)

nested_chats=[
    {"recipient":group_chat_manager,
     "summary_method":"reflection_with_llm",
     "summary_args":{
        "summary_prompt":"""Based the task and reference answer, sumarize and give the detailed answer. You must Keep detailed data when it occurs.""",
        }
     }
]
preference=ConversableAgent(
    name="Pre",
    llm_config=llm_config,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
)
preference.register_nested_chats(nested_chats,trigger=lambda sender: sender not in [group_chat_manager])

def main():
    while True:
        print("\nPersonal Finance Management System")
        print("1. Create/Reset Database")
        print("2. Store Transaction")
        print("3. Analyze Transactions")
        print("4. Exit")
        print("5: preference analysis")
        
        choice = input("Enter your choice (1-5): ")
        
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
        elif choice=='5':
            preference.initiate_chat(
                user_proxy,
                message="Hey there, I'm here to help you analyze and provide your consumption habite and preference. Let me know what you need to know?"
            )
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
