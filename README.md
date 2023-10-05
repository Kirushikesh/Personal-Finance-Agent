# Personal-Finance-Agent
A typical Indian Mother who doesn't scold you, but instead take a note on all your expense and profits. Its a chatbot like LLM Agent which stores the finance information using conversations, which can be used later for querying, analysis and the summarization and even the recommended actions/advice. 

With PF Agent, you don't need to manually maintain the expense notes, which is tedious to entry each of the expense in the UI. As the Agent has NLU capability it can understand the conversational financial update like "Today i spend 50rs on my bicycle repair." with the capability it stores the information in a vector datastore, and using the RAG you can retrieve those information during querying.

Approaches to start with,

1. Similar problem statement:
- https://github.com/pablovazquezg/expense-manager

2. The System Design:
- Using LLM Agent,
- Storing the data as an excel sheet,
- Using RAG to retrieve the data.

3. Model Selection
- For now lets work on LLama-2-80b model.
- If needed pay for the OpenAI Api.

4. Typical Usecase
- How usefull it is compared to the Existing apps.
- What are the possibilities and usage types.


