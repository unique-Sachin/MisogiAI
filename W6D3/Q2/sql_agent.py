import sqlite3
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field
import sqlparse
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

# Set up OpenAI API key
# Make sure to set your OPENAI_API_KEY environment variable
# os.environ["OPENAI_API_KEY"] = "your_key_here"

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


# 1. Define a State Class
class SQLAgentState(BaseModel):
    user_question: str
    sql_query: Optional[str] = Field(None, description="SQL query generated from the user question")
    query_result: Optional[List[Tuple]] = Field(None, description="Result of the SQL query")
    final_answer: Optional[str] = Field(None, description="The final human-readable answer")
    error: Optional[str] = Field(None, description="Any error that occurred during the process")

# 4. Example Data and Database Setup
def setup_database():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE students (
        id INTEGER,
        name TEXT,
        subject TEXT,
        grade INTEGER
    );
    """)
    students_data = [
        (1, 'Alice', 'Math', 85),
        (2, 'Alice', 'Science', 78),
        (3, 'Bob', 'Math', 92),
        (4, 'Bob', 'History', 88)
    ]
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?)", students_data)
    conn.commit()
    return conn

db_connection = setup_database()

# 2. Implement the Nodes as Functions
def parse_query(state: SQLAgentState) -> SQLAgentState:
    """Generate a SQL query from the user's natural language question using an LLM."""
    state.error = None  # Clear previous errors
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that translates natural language questions into SQL queries. The table name is 'students' and it has columns: id, name, subject, grade. Only generate SELECT queries."),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        sql_query = chain.invoke({"question": state.user_question})
        state.sql_query = sql_query.strip()
    except Exception as e:
        state.error = f"LLM Error: {e}"
        state.sql_query = None

    return state

def validate_sql(state: SQLAgentState) -> SQLAgentState:
    """Validate the generated SQL query using sqlparse and an LLM."""
    if state.sql_query:
        # First, basic validation with sqlparse
        try:
            parsed = sqlparse.parse(state.sql_query)
            if not parsed:
                state.error = "Invalid SQL: Empty query"
                return state
            if not any(stmt.get_type() == 'SELECT' for stmt in parsed):
                state.error = "Invalid SQL: Only SELECT statements are allowed."
                return state
        except Exception as e:
            state.error = f"SQL Parse Error: {e}"
            return state

        # Second, advanced validation with LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a SQL validation expert. Check if the following SQL query is valid and safe. The table is 'students' with columns: id, name, subject, grade. Respond with 'yes' if it is valid, or with a short error message if it is not."),
            ("human", "{sql_query}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        
        try:
            validation_result = chain.invoke({"sql_query": state.sql_query}).lower()
            if 'yes' not in validation_result:
                state.error = f"LLM Validation Error: {validation_result}"
        except Exception as e:
            state.error = f"LLM Validation Error: {e}"
    
    return state

def execute_query(state: SQLAgentState) -> SQLAgentState:
    """Execute the SQL query on the database."""
    if state.sql_query and not state.error:
        try:
            cursor = db_connection.cursor()
            cursor.execute(state.sql_query)
            state.query_result = cursor.fetchall()
        except sqlite3.Error as e:
            state.error = f"Execution Error: {e}"
    return state

def generate_response(state: SQLAgentState) -> SQLAgentState:
    """Generate a human-readable response from the query result or error."""
    if state.error:
        state.final_answer = f"Error: {state.error}"
    elif state.query_result:
        answer = f"Query Result for '{state.user_question}':\n"
        for row in state.query_result:
            answer += str(row) + "\n"
        state.final_answer = answer
    else:
        state.final_answer = "No results found."
    return state

# 3. Graph Structure (Edges)
workflow = StateGraph(SQLAgentState)

workflow.add_node("parse_query", parse_query)
workflow.add_node("validate_sql", validate_sql)
workflow.add_node("execute_query", execute_query)
workflow.add_node("generate_response", generate_response)

workflow.set_entry_point("parse_query")

def after_parse_query(state):
    if state.error:
        return "generate_response"
    return "validate_sql"

def after_validate_sql(state):
    if state.error:
        # This will now go to generate_response to report the validation error
        return "generate_response"
    return "execute_query"

workflow.add_conditional_edges(
    "parse_query",
    after_parse_query,
    {"validate_sql": "validate_sql", "generate_response": "generate_response"}
)

workflow.add_conditional_edges(
    "validate_sql",
    after_validate_sql,
    {"execute_query": "execute_query", "generate_response": "generate_response"}
)

workflow.add_edge("execute_query", "generate_response")
workflow.add_edge("generate_response", END)

app = workflow.compile()

# # 5. Test Cases
# def run_test_case(question):
#     inputs = {"user_question": question}
#     result = app.invoke(inputs)
#     print(result['final_answer'])

# if __name__ == "__main__":
#     print("--- Test Case 1: 'What grades did Alice get?' ---")
#     run_test_case("What grades did Alice get?")
    
#     print("\n--- Test Case 2: 'Show me Bob's scores' ---")
#     run_test_case("Show me Bob's scores")

#     print("\n--- Test Case 3: 'What did Alice get in Science?' ---")
#     run_test_case("What did Alice get in Science?")

#     print("\n--- Test Case 4: Invalid Query ---")
#     run_test_case("Update students set grade = 100")
