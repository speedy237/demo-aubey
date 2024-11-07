# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:52:46 2024

@author: gaelk
"""

import os
#from langchain.agents import *
#from langchain.llms import OpenAI
#from langchain.sql_database import SQLDatabase
#from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
#from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine, text # type: ignore


#import openai 
from dotenv import load_dotenv

#load_dotenv()
#openai.api_key = os.environ['OPENAI_API_KEY']
#qdrant_key = os.environ['QDRANT_KEY']
#qdrant_url = os.environ['QDRANT_URL']


db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "aubay"

database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_engine(database_url)

# Initialize SQLDatabase in LangChain
#db = SQLDatabase(engine)
print("Connection ok......")

# db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# print("ok")


# from langchain.chat_models import ChatOpenAI
# llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# print('starting toolking ...')

# toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# print('starting agent ...')
# agent_executor = create_sql_agent(
#     llm=llm,
#     toolkit=toolkit,
#     verbose=False
# )

# output = agent_executor.run("Describe the table allergies")

# print(output)


insert_query = """
INSERT INTO job (id, name, date, experience, diplome, certification, hard, soft) 
VALUES (:id, :name, :date, :experience, :diplome, :certification, :hard, :soft);
"""

# Define the values to insert
values = {
    "id": "2364nkkkhg",
    "name": "Data Engineer",
    "date": "2025-10-24",
    "experience": 4,
    "diplome": "Master",
    "certification": '["Python", "SQL", "Machine Learning"]',
    "hard": '["Python", "SQL", "Machine Learning"]',
    "soft": '["Python", "SQL", "Machine Learning"]'
}

# Execute the insertion
with engine.connect() as connection:
    with connection.begin():

       print(connection.execute(text(insert_query), values))
       print("Insertion ok")
