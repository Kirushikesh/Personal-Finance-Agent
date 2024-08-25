# Personal Finance Management System

## The Aunty's Scolding

"Arre, beta! Why are you always spending money like water? Don't you know how hard it is to earn? In my time, we used to keep track of every paisa in a notebook. What's this newfangled system you're showing me? An 'agent' to track expenses? Another one to analyze them? What's next, a robot to count your money? But... wait, it can tell you where all your money is going without flipping through pages? Accha, maybe this computer thing isn't so bad after all. But remember, no matter how smart your 'agents' are, spending wisely is still your job!"

## About The Project

This Personal Finance Management System is designed to help you track and analyze your financial transactions, bringing modern technology to the age-old wisdom of careful money management. It provides an interactive way to store your income and expenses, and offers insightful analysis of your spending habits using conversational AI agents.

## Features

- **Database Management**: Create and reset a SQLite database to store your transactions.
- **Transaction Storage**: Add new income or expense entries through a conversational interface.
- **Financial Analysis**: Get insights about your spending patterns using natural language queries.
- **User-Friendly Interface**: Simple menu-driven system for easy navigation.

## Technology Stack

- Python 3.x
- SQLite
- Autogen library for conversational AI
- GPT-4 for natural language processing

![image](https://github.com/user-attachments/assets/f963ca65-2ff9-407c-950e-57ed6e3a10b2)

![Screenshot 2024-08-25 at 8 56 31 PM](https://github.com/user-attachments/assets/dfe25700-b4e3-400b-93a9-c33568d74668)

## Installation

1. Clone the repository:
2. Navigate to the project directory:
```python
cd personal-finance-management
```
3. Install the required dependencies:
```python
pip install -r requirements.txt
```
4. Create a .env file in the current folder
```
OPENAI_API_KEY=...
```
## Usage

Run the main script to start the application:
```python
python main.py
```

Follow the on-screen prompts to:
1. Create or reset the database
2. Store new transactions
3. Analyze your financial data
4. Exit the application

## Project Structure

- `main.py`: The main script that runs the application
- `transactions.db`: SQLite database file (created when you run the application)
- `requirements.txt`: List of Python dependencies

## How It Works

1. **Database Setup**: The system uses SQLite to create and manage a local database for storing transaction data.

2. **Conversational Agents**: 
   - Storage Assistant: Helps users add new transactions using natural language.
   - Analysis Assistant: Provides insights on spending habits based on user queries.

3. **Data Storage**: Transactions are stored with details like date, category, amount, description, and whether it's an expense or income.

4. **Data Analysis**: Users can query their financial data using natural language, which is then translated into SQL queries for analysis.

## Future Directions

1. **User Interface Development**: We plan to create a graphical user interface (UI) for the project, making it more accessible and user-friendly for those who prefer visual interactions over command-line interfaces.

2. **Enhanced Visual Analytics**: We aim to implement charts and dashboard-based analysis using AI agents. This will provide users with visual representations of their financial data, making it easier to understand spending patterns and financial health at a glance.

## Contributing

Contributions to improve the Personal Finance Management System are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License file for details.

## Acknowledgments

- Thanks to all the aunties out there for inspiring us to manage our finances better!
- Autogen library for providing the conversational AI capabilities.
- GPT-4 for powering our natural language processing.

## Contact

For any queries or suggestions, please open an issue in the GitHub repository.

Remember, as our aunties would say, "A rupee saved is a rupee earned!" Happy budgeting!
