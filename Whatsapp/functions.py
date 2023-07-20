import json
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent_types import AgentType
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Read environment variables
host = os.environ.get("DB_HOST")
dbname = os.environ.get("DB_NAME")
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Build the connection string
connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{dbname}"
# Connect to the database
db = SQLDatabase.from_uri(
    connection_string,
    engine_args={
        "connect_args": {"sslmode": "require"},
    },
)


def user_reply(user_input: dict) -> str:
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    prefix = "You are an experienced financial advisor and your goal is the help your client to better understand about investments and their portfolio."

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type = AgentType.OPENAI_FUNCTIONS,
        prefix = prefix,
        handle_parsing_errors=True,
    )

    response = agent_executor.run(user_input)

    return response
