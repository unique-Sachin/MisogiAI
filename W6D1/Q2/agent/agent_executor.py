# from langchain.agents import initialize_agent
# from langchain.agents import (
#     AgentExecutor,
#     create_react_agent,
# )
# from langchain_openai import OpenAI
from langchain import hub
# from google_api.gsheet_connector import read_sheet
# # from agent.tools import read_worksheet, filter_data, pivot_table, write_results
# from agent.tools import get_tools
# import pandas as pd
import os   
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)


def run_agent(query: str, spreadsheet_id: str, sheet_name: str):
    
    # tools = get_tools()
    # llm = OpenAI(temperature=0, api_key=api_key)
    
    # # agent = initialize_agent(
    # #     tools,
    # #     llm,
    # #     agent_type="zero-shot-react-description",
    # #     verbose=True
    # # )
    # prompt = hub.pull("hwchase17/react")

    # # Create the ReAct agent using the create_react_agent function
    # agent = create_react_agent(
    #     llm=llm,
    #     tools=tools,
    #     stop_sequence=True,
    #     prompt=prompt,
    # )

    # # Create an agent executor from the agent and tools
    # agent_executor = AgentExecutor.from_agent_and_tools(
    #     agent=agent,
    #     tools=tools,
    #     verbose=True,
    # )

    # # Inject context to give the agent info
    # # df = read_sheet(spreadsheet_id, sheet_name)
    # context = f"The sheet with spreadsheet_id={spreadsheet_id} and sheet_name={sheet_name}"
    # full_query = f"{context}\n{query}"
    # result = agent_executor.invoke({
    #     "input": full_query,
    # })
    # print(f"Agent response: {result}")
    # return df if not isinstance(result, pd.DataFrame) else result
    
        
    # print(f"Agent response: {result}")
    class ReadSheetArgs(BaseModel):
        spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
        sheet_name: str = Field(..., description="Name of the worksheet")

    @tool(args_schema=ReadSheetArgs)
    def read_worksheet(spreadsheet_id: str, sheet_name: str) -> str:
        """Load a worksheet from Google Sheets."""
        print(f"Loading worksheet: {sheet_name} from spreadsheet ID: {spreadsheet_id}")
        return f"Loaded sheet {sheet_name} from {spreadsheet_id}"

    tools = [read_worksheet]

    llm = ChatOpenAI(temperature=0, model="gpt-4-0613", openai_api_key=api_key)
    prompt = hub.pull("hwchase17/react")

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke({"input": "what is the value of magic_function(3)?"})

  
    # print(response)






