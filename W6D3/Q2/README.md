# LangGraph SQL Agent

This project demonstrates a LangGraph-based SQL agent that can interpret natural language queries about student grades, generate SQL queries, and return answers from a SQLite database.

## Features

- **Natural Language to SQL**: Translates user questions into SQL queries using an OpenAI LLM.
- **SQL Validation**: Validates the generated SQL for correctness and safety using `sqlparse` and an LLM.
- **SQLite Integration**: Executes queries on an in-memory SQLite database.
- **LangGraph Workflow**: Uses a stateful graph to manage the flow from parsing to response generation.

## Project Structure

- `sql_agent.py`: The main script containing the LangGraph agent, node functions, and database setup.
- `requirements.txt`: A list of Python dependencies for the project.
- `.env.example`: An example file for setting up environment variables.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    -   Rename `.env.example` to `.env`.
    -   Add your OpenAI API and other keys to the `.env` file:
        ```
        OPENAI_API_KEY="your_openai_api_key_here"
        ```

## How to Run

Execute the `sql_agent.py` script to run the test cases:

```bash
python sql_agent.py
```

The script will output the results of several test queries, demonstrating the agent's ability to handle valid questions and reject invalid ones.

## How It Works

The agent operates based on a state machine defined with LangGraph:

1.  **Parse Query**: The user's question is passed to an LLM to generate a SQL query.
2.  **Validate SQL**: The generated query is validated. If it's invalid, the process stops and an error is reported.
3.  **Execute Query**: The valid SQL query is run against the SQLite database.
4.  **Generate Response**: The query result (or an error message) is formatted into a human-readable answer.

This workflow ensures that only safe and valid queries are executed, providing a secure way to interact with the database using natural language.
