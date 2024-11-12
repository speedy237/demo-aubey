# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:52:46 2024

@author: gaelk
"""

import os
from langchain.agents import *
from langchain.llms import OpenAI
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine, text


import openai 
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']



db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "aubey2"

database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(database_url)


print("Connection ok......")

db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

print("ok")


from langchain.chat_models import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

print('starting toolking ...')

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

print('starting agent ...')
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

output = agent_executor.run("Quelles sont les candidats qui ont au moins 3 ans d'experience pour le job JOB-2691")

print(output)





