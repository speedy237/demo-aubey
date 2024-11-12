import streamlit as st
from langchain.agents import create_sql_agent
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Retrieve environment variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure OpenAI API key
os.environ["OPENAI_API_KEY"] = openai_api_key
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Initialize database connection
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
db = SQLDatabase(engine)

# Initialize LangChain SQL agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_sql_agent(llm=llm, db=db, verbose=True)

def create_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

def apply_score_color(score):
    if score >= 50:
        # Interpoler le vert pour les scores entre 50 et 100
        green_intensity = int(255 * (score - 50) / 50)  # Plus le score est élevé, plus c'est vert
        return f"background-color: rgb(0, {green_intensity}, 0); color: white;"
    else:
        # Interpoler le rouge pour les scores entre 0 et 50
        red_intensity = int(255 * (50 - score) / 50)  # Plus le score est faible, plus c'est rouge
        return f"background-color: rgb({red_intensity}, 0, 0); color: white;"
    

def get_job_info(reference):
    connection = create_connection()
    query = "SELECT * FROM job WHERE reference = %s"
    job_info = pd.read_sql(query, connection, params=(reference,))
    connection.close()
    return job_info
def get_jobs():
    connection = create_connection()
    query = "SELECT reference, name FROM job"
    jobs = pd.read_sql(query, connection)
    connection.close()
    return jobs
# Filtrer les applications pour un job spécifique et une plage de dates, et trier par score décroissant
def filter_applications(reference, start_date, end_date):
    connection = create_connection()
    query = """
        SELECT * FROM application 
        WHERE reference = %s AND date BETWEEN %s AND %s
        ORDER BY score DESC
    """
    applications = pd.read_sql(query, connection, params=(reference, start_date, end_date))
    connection.close()
    return applications

# Streamlit UI layout
st.title("LangChain SQL Query Interface")


jobs = get_jobs()
job_selection = st.selectbox("Sélectionnez un job",options=jobs["reference"] + " - " + jobs["name"],index=0)

# Extraire la référence du job sélectionné
selected_reference = job_selection.split(" - ")[0]

   

 # Sélection de la plage de dates
st.subheader("Filtrer les candidatures")
start_date = st.date_input("Date de début", datetime.now())
end_date = st.date_input("Date de fin", datetime.now())

# Filtrer et afficher les candidatures
if st.button("Filtrer les candidatures"):
    applications = filter_applications(selected_reference, start_date, end_date)
     # Afficher les informations du job sélectionné
    st.subheader("Informations du job")
    job_info = get_job_info(selected_reference)
    st.write(job_info)
        
    # Supprimer la colonne 'reference' du DataFrame
    if "reference" in applications.columns:
        applications = applications.drop(columns=["reference"])


    # Appliquer le style de dégradé rouge-vert sur la colonne 'score'
    if not applications.empty:
        st.subheader("Candidatures filtrées")
        styled_applications = applications.style.applymap(lambda score: apply_score_color(score) if isinstance(score, (int, float)) else "", 
                subset=["score"]
            )
        st.dataframe(styled_applications)
    else:
        st.write("Aucune candidature trouvée pour ce filtre.")
        # Afficher un champ de texte pour la requête en langage naturel


st.header("Enter your natural language SQL request:")
query = st.text_area("Natural Language Query", placeholder="e.g., Show me all jobs with high scores...")


# Button to trigger query execution
if st.button("Validate"):
    try:
        # Execute the natural language query
        result = agent.run(query)
        
        # Format and display result in a table
        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            st.dataframe(result)
        else:
            # In case the result is a plain text, display as message
            st.write("Result:", result)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
