import streamlit as st
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

# Charger les variables d'environnement depuis le fichier .env

load_dotenv()


# Récupérer les informations de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


# Connexion à la base de données MySQL
def create_connection():
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

# Récupérer les offres d'emploi depuis MySQL
def get_jobs():
    connection = create_connection()
    query = "SELECT RoleID, Role FROM jobs"
    jobs = pd.read_sql(query, connection)
    connection.close()
    return jobs

def initialize_sql_chain():
    db =SQLDatabase.from_uri(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    chain = create_sql_query_chain(db=db, llm=llm)
  
    return chain



# Récupérer les informations d'un job spécifique
def get_job_info(RoleID):
    connection = create_connection()
    query = "SELECT * FROM jobs WHERE RoleID = %s"
    job_info = pd.read_sql(query, connection, params=(RoleID,))
    connection.close()
    return job_info
# Filtrer les applications pour un job spécifique et une plage de dates, et trier par score décroissant
def query_applications(query):
    connection = create_connection()
    applications = pd.read_sql(query, connection)
    connection.close()
    return applications

def filter_applications(RoleID, start_date, end_date):
    connection = create_connection()
    query = """
        SELECT * FROM jobapplications
        WHERE RoleID = %s AND date BETWEEN %s AND %s
        ORDER BY Score DESC
    """
    applications = pd.read_sql(query, connection, params=(RoleID, start_date, end_date))
    connection.close()
    return applications

# Fonction pour appliquer un dégradé de couleur rouge-vert en fonction du score
def apply_score_color(Score):
    if Score >= 50:
        # Interpoler le vert pour les scores entre 50 et 100
        green_intensity = int(255 * (Score - 50) / 50)  # Plus le score est élevé, plus c'est vert
        return f"background-color: rgb(0, {green_intensity}, 0); color: white;"
    else:
        # Interpoler le rouge pour les scores entre 0 et 50
        red_intensity = int(255 * (50 - Score) / 50)  # Plus le score est faible, plus c'est rouge
        return f"background-color: rgb({red_intensity}, 0, 0); color: white;"

def main():
    st.title("Job Application Interface")

    # Récupérer et afficher la liste des jobs dans un combo-box
    jobs = get_jobs()
    job_selection = st.selectbox(
        "Sélectionnez un job",
        options=jobs["RoleID"] + " - " + jobs["Role"],
        index=0
    )

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
        if "RoleID" in applications.columns:
            applications = applications.drop(columns=["RoleID"])

        # Appliquer le style de dégradé rouge-vert sur la colonne 'score'
        if not applications.empty:
            st.subheader("Candidatures filtrées")
            styled_applications = applications.style.applymap(
                lambda Score: apply_score_color(Score) if isinstance(Score, (int, float)) else "", 
                subset=["Score"]
            )
            st.dataframe(styled_applications)
        else:
            st.write("Aucune candidature trouvée pour ce filtre.")
    # Filtrer et afficher les candidatures qvec les agents SQL
    user_query = st.text_input("Posez votre question ")
    if st.button("Rechercher"):
       with st.spinner("Traitement de la requête..."):
           try:
               # Run the query with LangChain agent
               # Instruct agent to return raw tabular data
               #structured_query = f"{user_query}"
               chain=initialize_sql_chain()
               sql_query = chain.invoke({"question":user_query})
               sql_query=sql_query.replace("LIMIT 5","")
               print(sql_query)
               applications = query_applications(sql_query)
               if "RoleID" in applications.columns:
                  applications = applications.drop(columns=["RoleID"])
               if not applications.empty:
                  st.subheader("Candidatures filtrées")
                  st.dataframe(applications)
               else:
                 st.write("Aucune candidature trouvée")
               
               
                   
           except Exception as e:
               st.error(f"Erreur lors de l'exécution de la requête : {e}")

    
    # Filtrer et afficher les candidatures
   
    

if __name__ == "__main__":
    main()


