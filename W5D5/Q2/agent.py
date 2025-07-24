import os
import dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = "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"

# === STEP 1: Load both SQLite databases ===
zepto_db = SQLDatabase.from_uri("sqlite:///zepto.db")
blinkit_db = SQLDatabase.from_uri("sqlite:///blinkit.db")

# === STEP 2: Prepare LLM ===
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# === STEP 3: Create toolkits for both DBs ===
zepto_toolkit = SQLDatabaseToolkit(db=zepto_db, llm=llm)
blinkit_toolkit = SQLDatabaseToolkit(db=blinkit_db, llm=llm)

# === STEP 5: Build schema descriptions (RAG source) ===
def extract_schema_docs(db: SQLDatabase, db_name: str):
    schema_info = ""
    table_names = db.get_usable_table_names()  # returns a set of real table names
    # print("Tables found:", table_names)
    for table in table_names:
        schema_info += f"\n\n[{db_name}] Table: {table}\n"
        schema_info += db.get_table_info([table])  # ✅ NOTE: passing list [table], not string
    return schema_info

zepto_schema_text = extract_schema_docs(zepto_db, "Zepto")
blinkit_schema_text = extract_schema_docs(blinkit_db, "Blinkit")
combined_schema = zepto_schema_text + "\n\n" + blinkit_schema_text


# === STEP 6: RAG — Embed and create retriever ===
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
docs = text_splitter.create_documents([combined_schema])
vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# === STEP 7: Wrap question with RAG context ===
# print(retriever.get_relevant_documents("Show me Zepto items that cost more than 500."))

def add_context_to_query(query):
    related_docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in related_docs])
    return f"Use the following context to answer:\n{context}\n\nQuestion: {query}"

# === STEP 8: Create final agent ===
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=zepto_toolkit,  # Only needs one toolkit; we already provided both sets of tools
    verbose=True,
)



# === STEP 9: Run questions with RAG prepended ===
if __name__ == "__main__":
    questions = [
        "Show me top 10 products that cost more than 1k.",
    ]
    for question in questions:
        print(f"\n\n=== Question: {question} ===\n")
        enriched_query = add_context_to_query(question)
        response = agent_executor.invoke({"input": enriched_query})
        print(response)

