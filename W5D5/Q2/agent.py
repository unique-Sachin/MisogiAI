import os
import dotenv
dotenv.load_dotenv()  # Loads̄ .env first
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def get_sql_agent():
    # === STEP 2: Load two SQLite databases ===
    zepto_db = SQLDatabase.from_uri("sqlite:///zepto.db")         # Adjust file names
    blinkit_db = SQLDatabase.from_uri("sqlite:///blinkit.db")

    # === Step 2: Load LLM ===
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    # === STEP 4: Create SQL Toolkits ===
    zepto_toolkit = SQLDatabaseToolkit(db=zepto_db, llm=llm)
    blinkit_toolkit = SQLDatabaseToolkit(db=blinkit_db, llm=llm)

    # === STEP 5: Combine tools from both toolkits ===
    tools = []
    for tool in zepto_toolkit.get_tools():
        tool.name = f"Zepto_{tool.name}"
        tools.append(tool)

    for tool in blinkit_toolkit.get_tools():
        tool.name = f"Blinkit_{tool.name}"
        tools.append(tool)

    print(tools)
    # === STEP 6: Create the agent with all tools ===
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,  # or AgentType.ZERO_SHOT_REACT_DESCRIPTION
        verbose=True
    )
    return agent

if __name__ == "__main__":
    agent = get_sql_agent()
    questions = [
        # "List all products in the Dairy category from Zepto.",
        "Show me products above ₹500 in Blinkit.",
    ]
    for question in questions:
        print(f"\n\n=== Question: {question} ===\n")
        result = agent.invoke({"input": question})
        print(result)