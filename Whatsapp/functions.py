from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.chat_models import ChatOpenAI
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
from handler import AgentExecutorHandler


load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
db = SQLDatabase.from_uri(
    "postgresql+psycopg2://postgres:Rcsouza24@localhost/finance",
    engine_args={
        "connect_args": {"sslmode": "disable"},
        },
    )

def user_reply(user_input):

    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm) 

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
    )

    response = agent_executor.run(user_input=user_input)
   
    return response

 #agent_executor.run(**{"input":"what are the names (NOT the security_id) of the securities hold by the user k67E4xKvMlhmleEa4pg9hlwGGNnnEeixPolGm", "callbacks":[AgentExecutorHandler("asdfasdf", "asdfasdf")]})
