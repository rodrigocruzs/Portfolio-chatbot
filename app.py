from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import os
import psycopg2
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
db = SQLDatabase.from_uri(
    "postgresql+psycopg2://postgres:Rcsouza24@localhost/finance",
    engine_args={
        "connect_args": {"sslmode": "disable"},
    },
)

llm = ChatOpenAI(model_name="gpt-4")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True,
)

agent_executor.run("what are the securities hold by the user k67E4xKvMlhmleEa4pg9hlwGGNnnEeixPolGm")
