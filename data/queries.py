import pandas as pd
from config.settings import BASE_DE_DATOS


def get_collection_data(client, engine, collection_name, query=None):
    """Get data from either MongoDB or PostgreSQL.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine
        collection_name: Name of the collection/table
        query: Query parameters (optional)

    Returns:
        DataFrame: Data from the database
    """
    if BASE_DE_DATOS == "mongodb":
        db = client["dbmongo_sesnsp"]
        collection = db[collection_name]

        if query:
            cursor = collection.find(query)
        else:
            cursor = collection.find()

        df = pd.DataFrame(list(cursor))
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

    elif BASE_DE_DATOS == "postgresql":
        if query:
            df = pd.read_sql_query(query, engine)
        else:
            table_name = collection_name
            # Handle special cases for table names that might need quotes
            if collection_name in ["dfLugar", "dfPobExtendida", "dfDefinitivo"]:
                table_name = f'"{collection_name}"'
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", engine)

    return df


def get_crime_data(client, engine, id_ubic, id_agrup_del, aniomes_ini, aniomes_fin):
    """Get crime data for specific location, crime type and time period.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine
        id_ubic: Location ID
        id_agrup_del: Crime group ID
        aniomes_ini: Start year-month
        aniomes_fin: End year-month

    Returns:
        DataFrame: Crime data
    """
    if BASE_DE_DATOS == "mongodb":
        db = client["dbmongo_sesnsp"]
        collection = db["dfDefinitivo"]
        query = {
            "$and": [
                {"CVE_LUGAR": id_ubic},
                {"Aniomes": {"$gte": aniomes_ini}},
                {"Aniomes": {"$lte": aniomes_fin}},
                {"Id_Agrupador_Delito": id_agrup_del},
            ]
        }
        results = collection.find(query)
        df_res = pd.DataFrame(list(results))
        if "_id" in df_res.columns:
            df_res.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = f"""
            SELECT * FROM "dfDefinitivo" 
            WHERE "CVE_LUGAR" = '{id_ubic}' 
            AND "Aniomes" >= '{aniomes_ini}' 
            AND "Aniomes" <= '{aniomes_fin}' 
            AND "Id_Agrupador_Delito" = '{id_agrup_del}'
        """
        df_res = pd.read_sql_query(query, engine)

    return df_res


def get_national_crime_data(client, engine, id_agrup_del, aniomes_ini, aniomes_fin):
    """Get national crime data for specific crime type and time period.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine
        id_agrup_del: Crime group ID
        aniomes_ini: Start year-month
        aniomes_fin: End year-month

    Returns:
        DataFrame: National crime data
    """
    if BASE_DE_DATOS == "mongodb":
        db = client["dbmongo_sesnsp"]
        collection = db["dfDefinitivo"]
        query = {
            "$and": [
                {"CVE_LUGAR": "P00"},
                {"Aniomes": {"$gte": aniomes_ini}},
                {"Aniomes": {"$lte": aniomes_fin}},
                {"Id_Agrupador_Delito": id_agrup_del},
            ]
        }
        results = collection.find(query)
        df_res = pd.DataFrame(list(results))
        if "_id" in df_res.columns:
            df_res.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = f"""
            SELECT * FROM "dfDefinitivo" 
            WHERE "CVE_LUGAR" = 'P00' 
            AND "Aniomes" >= '{aniomes_ini}' 
            AND "Aniomes" <= '{aniomes_fin}' 
            AND "Id_Agrupador_Delito" = '{id_agrup_del}'
        """
        df_res = pd.read_sql_query(query, engine)

    df_res.rename(columns={"tasa": "tasa_nal"}, inplace=True)
    return df_res[["Aniomes", "tasa_nal"]]


def get_estatal_crime_data(
    client, engine, id_agrup_del, id_ent_asoc, aniomes_ini, aniomes_fin
):
    """Get estatal crime data for specific crime type and time period.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine
        id_agrup_del: Crime group ID
        id_ent_asoc: State of Mexico
        aniomes_ini: Start year-month
        aniomes_fin: End year-month

    Returns:
        DataFrame: Estatal crime data
    """
    clave_consolidada = "E" + str(id_ent_asoc)
    if BASE_DE_DATOS == "mongodb":
        db = client["dbmongo_sesnsp"]
        collection = db["dfDefinitivo"]
        query = {
            "$and": [
                {"CVE_LUGAR": clave_consolidada},
                {"Aniomes": {"$gte": aniomes_ini}},
                {"Aniomes": {"$lte": aniomes_fin}},
                {"Id_Agrupador_Delito": id_agrup_del},
            ]
        }
        results = collection.find(query)
        df_res = pd.DataFrame(list(results))
        if "_id" in df_res.columns:
            df_res.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = f"""
            SELECT * FROM "dfDefinitivo" 
            WHERE "CVE_LUGAR" = '{clave_consolidada}' 
            AND "Aniomes" >= '{aniomes_ini}' 
            AND "Aniomes" <= '{aniomes_fin}' 
            AND "Id_Agrupador_Delito" = '{id_agrup_del}'
        """
        df_res = pd.read_sql_query(query, engine)

    df_res.rename(columns={"tasa": "tasa_est"}, inplace=True)
    return df_res[["Aniomes", "tasa_est"]]
