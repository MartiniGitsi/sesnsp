"""Functions to load and transform catalog data."""

import streamlit as st
import pandas as pd
from data.queries import get_collection_data
from config.settings import BASE_DE_DATOS


@st.cache_data
def get_aniomes(_client, _engine):
    """Get year-month data from database."""
    return get_collection_data(_client, _engine, "col_aniomes")


@st.cache_data
def get_poblacion(_client, _engine):
    """Get population data from database."""
    return get_collection_data(_client, _engine, "cat_poblacion")


@st.cache_data
def get_entidad(_client, _engine):
    """Get entity data from database."""
    return get_collection_data(_client, _engine, "cat_entidad")


@st.cache_data
def get_municipio(_client, _engine):
    """Get municipality data from database."""
    return get_collection_data(_client, _engine, "cat_municipio")


@st.cache_data
def get_delito(_client, _engine):
    """Get crime type data from database."""
    return get_collection_data(_client, _engine, "cat_delito")


@st.cache_data
def get_mes(_client, _engine):
    """Get month data from database."""
    return get_collection_data(_client, _engine, "cat_mes")


@st.cache_data
def get_cab_agrupador_delito(_client, _engine):
    """Get crime group header data from database."""
    return get_collection_data(_client, _engine, "cab_agrupador_delito")


@st.cache_data
def get_det_agrupador_delito(_client, _engine):
    """Get crime group detail data from database."""
    return get_collection_data(_client, _engine, "det_agrupador_delito")


@st.cache_data
def get_lugar(_client, _engine):
    """Get location data from database."""
    return get_collection_data(_client, _engine, "dfLugar")


@st.cache_data
def get_poblacion_extendida(_client, _engine):
    """Get extended population data from database."""
    return get_collection_data(_client, _engine, "dfPobExtendida")


def load_catalogs(_client, _engine):
    """Load all catalog data and prepare related dataframes.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine

    Returns:
        dict: Dictionary containing all catalog dataframes
    """
    # Load basic catalogs
    df_aniomes = get_aniomes(_client, _engine)
    df_pob = get_poblacion(_client, _engine)
    df_ent = get_entidad(_client, _engine)
    df_mun = get_municipio(_client, _engine)
    df_del = get_delito(_client, _engine)
    df_mes = get_mes(_client, _engine)
    df_cab_agrp = get_cab_agrupador_delito(_client, _engine)
    df_det_agrp = get_det_agrupador_delito(_client, _engine)
    df_lugar = get_lugar(_client, _engine)
    df_pob_extendida = get_poblacion_extendida(_client, _engine)

    # Calculate derived values
    max_year = df_aniomes["Aniomes"].max() // 100

    # Create population dataframes for the maximum year
    df_pob_year_max = df_pob.loc[
        df_pob["Year"] == max_year, ["Id_Municipio", "Num_Habs"]
    ]
    df_pob_ent_year_max = (
        df_pob.query("Year == @max_year")
        .groupby(by=["Year", "Id_Entidad"], as_index=False)["Num_Habs"]
        .sum()
    )

    # Merge entity data with population data
    df_ent = pd.merge(
        df_ent,
        df_pob_ent_year_max,
        left_on="CVE_ENT",
        right_on="Id_Entidad",
        how="left",
    )

    # Create composite municipality name and merge with population data
    df_mun["mun_compuesto"] = df_mun["NOM_MUN"] + ", " + df_mun["NOM_ABR"]
    df_mun = pd.merge(
        df_mun, df_pob_year_max, left_on="_CVEMUN", right_on="Id_Municipio", how="left"
    )

    # Return all catalog data in a dictionary
    return {
        "aniomes": df_aniomes,
        "poblacion": df_pob,
        "entidad": df_ent,
        "municipio": df_mun,
        "delito": df_del,
        "mes": df_mes,
        "cab_agrupador_delito": df_cab_agrp,
        "det_agrupador_delito": df_det_agrp,
        "lugar": df_lugar,
        "poblacion_extendida": df_pob_extendida,
        "max_year": max_year,
    }
