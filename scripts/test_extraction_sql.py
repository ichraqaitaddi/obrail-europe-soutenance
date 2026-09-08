from sqlalchemy import text
from app.database.database import engine


# Lire le fichier contenant les requêtes SQL
with open("sql/extraction.sql", "r", encoding="utf-8") as file:
    sql_content = file.read()


# Séparer les différentes requêtes SQL
queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]


# Connexion à PostgreSQL
with engine.connect() as conn:

    print("\n===== TEST DES REQUÊTES SQL C2 =====\n")

    for index, query in enumerate(queries, start=1):

        print(f"\n--- Requête {index} ---")

        # Exécuter la requête SQL
        result = conn.execute(text(query))

        # Récupérer les résultats
        rows = result.fetchmany(5)

        # Afficher les premières lignes
        for row in rows:
            print(row)

        print(f"Nombre de colonnes : {len(result.keys())}")