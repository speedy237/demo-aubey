import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chat_models import ChatOpenAI
from sqlalchemy import create_engine
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

# Database connection details
db_user = "root"
db_password = ""
db_host = "localhost"
db_name = "aubey2"
database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

# Initialize database connection and LangChain components
engine = create_engine(database_url)
db = SQLDatabase.from_uri(database_url)
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=False
)

# Function to style the score column
def apply_score_color(score):
    if score >= 50:
        green_intensity = int(255 * (score - 50) / 50)
        return f"background-color: rgb(0, {green_intensity}, 0); color: white;"
    else:
        red_intensity = int(255 * (50 - score) / 50)
        return f"background-color: rgb({red_intensity}, 0, 0); color: white;"

# Main Streamlit application
def main():
    st.title("Job Application Search with Natural Language Querying")

    # User enters natural language query
    user_query = st.text_input("Posez votre question (ex: Quelles sont les candidats qui ont au moins 3 ans d'expérience pour le job JOB-2691):")
    
    if st.button("Exécuter la requête"):
        with st.spinner("Traitement de la requête..."):
            try:
                # Run the query with LangChain agent
                # Instruct agent to return raw tabular data
                structured_query = f"{user_query}. Retournez uniquement les données sous forme de table, sans explication supplémentaire."
                output = agent_executor.run(structured_query)
                st.write(output)
                #output_df = pd.DataFrame(output, columns=["first_name", "last_name", "degree", "experience"])
                
                    
            except Exception as e:
                st.error(f"Erreur lors de l'exécution de la requête : {e}")

if __name__ == "__main__":
    main()
