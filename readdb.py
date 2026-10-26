import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Charger les identifiants masqués
load_dotenv()

try:
    # Connexion au serveur MySQL de XAMPP
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    if connection.is_connected():
        cursor = connection.cursor()
        print(" Connecté avec succès à la base MySQL collective !")
        
        # Exemple de requête
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"Base de données active : {db_name[0]}")

except Error as e:
    print(f"Erreur lors de la connexion à MySQL : {e}")

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Connexion MySQL fermée.")
