import mysql.connector
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import openai # type: ignore
from langchain import SQLDatabase # type: ignore
from langchain.llms import OpenAI # type: ignore
from langchain.agents import * # type: ignore
from langchain.sql_database import SQLDatabase # type: ignore
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit # type: ignore
from langchain_community.agent_toolkits import create_sql_agent # type: ignore
from langchain.chat_models import ChatOpenAI # type: ignore
from langchain.chains import create_sql_query_chain # type: ignore

load_dotenv()


# Récupérer les informations de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
db =SQLDatabase.from_uri(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
chain = create_sql_query_chain(db=db, llm=llm)
query="Quels sont les candidats pour le job JOB-2691 de plus de 3 ans d'experiences"
sql_query = chain.invoke({"question":query})
print(sql_query)
print("--------------\n")
print("la requette sql est \n")
sql_query=sql_query.replace("LIMIT 5","")
print(sql_query)

