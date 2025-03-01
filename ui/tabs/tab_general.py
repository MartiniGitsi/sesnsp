"""UI components for the General tab."""

import streamlit as st
import pandas as pd
import numpy as np
from data.queries import get_crime_data, get_estatal_crime_data, get_national_crime_data
from ui.plotlyviz import create_plotly_risk_chart
from ui.visualization import create_crime_chart, calculate_variations
from utils.helpers import get_chart_parameters, get_trend


def render_general_tab(catalogs, sidebar_options, client, engine):
    """Render the General tab content.

    Args:
        catalogs: Dictionary of catalog dataframes
        sidebar_options: Dictionary of selected sidebar options
        client: MongoDB client
        engine: SQLAlchemy engine
    """
    # Get list of year-months from catalog
    df_aniomes = catalogs["aniomes"]
    list_aniomes = df_aniomes["Aniomes"].unique()
    list_aniomes.sort()

    # Year-month range selector
    aniomes_ini, aniomes_fin = st.select_slider(
        ":calendar: Seleccione los meses a considerar:",
        options=list_aniomes,
        value=(list_aniomes[-12], list_aniomes[-1]),
    )

    # Get base dataframe with all year-months in the selected range
    df = df_aniomes.loc[
        (df_aniomes["Aniomes"] >= aniomes_ini) & (df_aniomes["Aniomes"] <= aniomes_fin),
        "Aniomes",
    ]

    # Get crime data for selected location
    df_res_ubi = get_crime_data(
        client,
        engine,
        sidebar_options["id_ubic"],
        sidebar_options["id_agrup_del"],
        aniomes_ini,
        aniomes_fin,
    )

    # Check if we got results
    flag_resultados = bool(len(df_res_ubi))
    if flag_resultados:
        df = pd.merge(df, df_res_ubi, on="Aniomes", how="left").fillna(0)
    else:
        df = df.to_frame()
        df["CVE_LUGAR"] = sidebar_options["id_ubic"]
        df["Id_Agrupador_Delito"] = sidebar_options["id_agrup_del"]
        df["Num_Delitos"] = df["tasa"] = 0

    # Get regression trend data for comparison
    df_trend = get_trend(df.copy())

    # Get national data for comparison
    df_res_nal = get_national_crime_data(
        client, engine, sidebar_options["id_agrup_del"], aniomes_ini, aniomes_fin
    )

    # Get estatal data for comparison
    if sidebar_options["id_ent_asoc"] == "0":
        df["tasa_est"] = df_res_nal[["tasa_nal"]]
    else:
        df_res_est = get_estatal_crime_data(
            client,
            engine,
            sidebar_options["id_agrup_del"],
            sidebar_options["id_ent_asoc"],
            aniomes_ini,
            aniomes_fin,
        )
        df = pd.merge(df, df_res_est, how="inner", on="Aniomes")

    # Join dataframes trend y nal
    df = pd.merge(df, df_trend, how="inner", on="Aniomes")
    df = pd.merge(df, df_res_nal, how="inner", on="Aniomes")

    chart_parameteres = get_chart_parameters(sidebar_options)

    st.pyplot(
        create_crime_chart(
            df,
            chart_parameteres,
            sidebar_options,
            sidebar_options["nom_agrupador_selecc"],
            sidebar_options["nom_ubic_selecc"],
        )
    )

    with st.expander("Ver datos"):
        st.dataframe(df)

    st.plotly_chart(
        create_plotly_risk_chart(
            df,
            chart_parameteres,
            sidebar_options,
            sidebar_options["nom_agrupador_selecc"],
            sidebar_options["nom_ubic_selecc"],
        )
    )
