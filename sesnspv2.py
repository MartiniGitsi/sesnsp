"""Module que será aplicación de Streamlit."""

import pandas as pd
import numpy as np
import streamlit as st
from pymongo.mongo_client import MongoClient
import psycopg2
from sqlalchemy import create_engine

import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

BASE_DE_DATOS = "postgresql"  # ['mongodb','postgresql']

# Conexión a MongoDb
uri = st.secrets["mongodb_uri"]
client = MongoClient(uri)
db = client["dbmongo_sesnsp"]  # Nombre de la BD

# Conexión a Postgresql
db_user = "postgres.ojioiftryayyihlqnitm"
db_password = "Supra.Normal1"
db_host = "aws-0-us-west-1.pooler.supabase.com"
db_port = 6543
db_name = "postgres"
DATABASE_URL = (
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)
engine = create_engine(DATABASE_URL)

# setear configuración de streamlit antes de cualquier otra sentencia st
st.set_page_config(
    page_title="Estadísticas Delictivas",  # Title shown on browser tab
    page_icon=":bar_chart:",  # Favicon (emoji or URL)
    layout="wide",  # Options: "centered" or "wide"
    initial_sidebar_state="expanded",
)  # Options: "auto", "expanded", "collapsed"


# ------------------------
# **Recuperar catálogos**
@st.cache_data
def get_aniomes():
    if BASE_DE_DATOS == "mongodb":
        collection = db["col_aniomes"]
        cursor = collection.find()
        dfAniomes = pd.DataFrame(list(cursor))
        if "_id" in dfAniomes.columns:
            dfAniomes.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM col_aniomes"
        dfAniomes = pd.read_sql_query(query, engine)
    return dfAniomes


dfAniomes = get_aniomes()
MAX_YEAR = dfAniomes["Aniomes"].max() // 100


@st.cache_data
def get_poblacion():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cat_poblacion"]
        cursor = collection.find()
        dfPob = pd.DataFrame(list(cursor))
        if "_id" in dfPob.columns:
            dfPob.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cat_poblacion"
        dfPob = pd.read_sql_query(query, engine)
    return dfPob


dfPob = get_poblacion()
dfPobYearMax = dfPob.loc[dfPob["Year"] == MAX_YEAR, ["Id_Municipio", "Num_Habs"]]
dfPobEntYearMax = (
    dfPob.query("Year == @MAX_YEAR")
    .groupby(by=["Year", "Id_Entidad"], as_index=False)["Num_Habs"]
    .sum()
)


@st.cache_data
def get_entidad():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cat_entidad"]
        cursor = collection.find()
        dfEnt = pd.DataFrame(list(cursor))
        if "_id" in dfEnt.columns:
            dfEnt.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cat_entidad"
        dfEnt = pd.read_sql_query(query, engine)
    return dfEnt


dfEnt = get_entidad()
dfEnt = pd.merge(
    dfEnt, dfPobEntYearMax, left_on="CVE_ENT", right_on="Id_Entidad", how="left"
)


@st.cache_data
def get_municipio():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cat_municipio"]
        cursor = collection.find()
        dfMun = pd.DataFrame(list(cursor))
        if "_id" in dfMun.columns:
            dfMun.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cat_municipio"
        dfMun = pd.read_sql_query(query, engine)
    return dfMun


dfMun = get_municipio()
dfMun["mun_compuesto"] = dfMun["NOM_MUN"] + ", " + dfMun["NOM_ABR"]
dfMun = pd.merge(
    dfMun, dfPobYearMax, left_on="_CVEMUN", right_on="Id_Municipio", how="left"
)


@st.cache_data
def get_delito():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cat_delito"]
        cursor = collection.find()
        dfDel = pd.DataFrame(list(cursor))
        if "_id" in dfDel.columns:
            dfDel.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cat_delito"
        dfDel = pd.read_sql_query(query, engine)
    return dfDel


dfDel = get_delito()


@st.cache_data
def get_mes():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cat_mes"]
        cursor = collection.find()
        dfMes = pd.DataFrame(list(cursor))
        if "_id" in dfMes.columns:
            dfMes.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cat_mes"
        dfMes = pd.read_sql_query(query, engine)
    return dfMes


dfMes = get_mes()


@st.cache_data
def get_cab_agrupador_delito():
    if BASE_DE_DATOS == "mongodb":
        collection = db["cab_agrupador_delito"]
        cursor = collection.find()
        dfCabAgrp = pd.DataFrame(list(cursor))
        if "_id" in dfCabAgrp.columns:
            dfCabAgrp.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM cab_agrupador_delito"
        dfCabAgrp = pd.read_sql_query(query, engine)
    return dfCabAgrp


dfCabAgrp = get_cab_agrupador_delito()


@st.cache_data
def get_det_agrupador_delito():
    if BASE_DE_DATOS == "mongodb":
        collection = db["det_agrupador_delito"]
        cursor = collection.find()
        dfDetAgrp = pd.DataFrame(list(cursor))
        if "_id" in dfDetAgrp.columns:
            dfDetAgrp.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = "SELECT * FROM det_agrupador_delito"
        dfDetAgrp = pd.read_sql_query(query, engine)
    return dfDetAgrp


dfDetAgrp = get_det_agrupador_delito()


@st.cache_data
def get_Lugar():
    if BASE_DE_DATOS == "mongodb":
        collection = db["dfLugar"]
        cursor = collection.find()
        dfLugar = pd.DataFrame(list(cursor))
        if "_id" in dfLugar.columns:
            dfLugar.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = 'SELECT * FROM "dfLugar"'
        dfLugar = pd.read_sql_query(query, engine)
    return dfLugar


dfLugar = get_Lugar()


@st.cache_data
def get_poblacion_extendida():
    if BASE_DE_DATOS == "mongodb":
        collection = db["dfPobExtendida"]
        cursor = collection.find()
        dfPobExtendida = pd.DataFrame(list(cursor))
        if "_id" in dfPobExtendida.columns:
            dfPobExtendida.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = 'SELECT * FROM "dfPobExtendida"'
        dfPobExtendida = pd.read_sql_query(query, engine)
    return dfPobExtendida


dfPobExtendida = get_poblacion_extendida()


# ------------------------
# **Funciones**
# Función para obtener Aniomes estilo np.datetime64
def get_dt64(Aniomes) -> np.datetime64:
    year = Aniomes // 100
    mes = Aniomes % year
    dt = datetime.datetime(year, mes, 1)
    dt64 = np.datetime64(dt)
    return dt64


def get_ubicaciones(tipo_ubicacion):
    match tipo_ubicacion:
        case "Entidades":
            return dfLugar.loc[dfLugar["TIPO_LUGAR"] == "Entidad", "NOM_LUGAR"]
        case "Metrópolis":
            return dfLugar.loc[dfLugar["TIPO_LUGAR"] == "Metropoli", "NOM_LUGAR"]
        # case "Municipios 800K+":
        #    return dfMun.loc[dfMun["Num_Habs"] >= 800000, "mun_compuesto"]
        # case "Municipios 500K+":
        #    return dfMun.loc[dfMun["Num_Habs"] >= 500000, "mun_compuesto"]
        # case "Municipios 300K+":
        #    return dfMun.loc[dfMun["Num_Habs"] >= 300000, "mun_compuesto"]
        # case "Municipios 100K+":
        #    return dfMun.loc[dfMun["Num_Habs"] >= 100000, "mun_compuesto"]
        case "Todos los municipios":
            return dfLugar.loc[dfLugar["TIPO_LUGAR"] == "Municipio", "NOM_LUGAR"]


# ------------------------
# **Construcción en Streamlit**
st.title(":arrow_right: Generación de gráficas delictivas")  # Título

# Sidebar Streamlit
st.sidebar.header("🔧 Ajustes")
nom_agrupador_selecc = st.sidebar.selectbox(
    ":rotating_light: Seleccione un delito:", dfCabAgrp["Nombre_Agrupador_Delito"]
)
IdAgrupDel = list(
    dfCabAgrp.loc[
        dfCabAgrp["Nombre_Agrupador_Delito"] == nom_agrupador_selecc,
        "Id_Agrupador_Delito",
    ]
)[0]

with st.sidebar.expander(":earth_americas: Control de ubicaciones"):
    tipo_ubicacion = st.radio(
        "Seleccione:",
        [
            "Entidades",
            "Metrópolis",
            # "Municipios 800K+",
            # "Municipios 500K+",
            # "Municipios 300K+",
            # "Municipios 100K+",
            "Todos los municipios",
        ],
    )

    nom_ubic_selecc = st.selectbox(
        ":round_pushpin: Seleccione ubicación:",
        get_ubicaciones(tipo_ubicacion).sort_values(),
    )
    if tipo_ubicacion == "Entidades":
        IdUbic = list(
            dfLugar.loc[
                (dfLugar["TIPO_LUGAR"] == "Entidad")
                & (dfLugar["NOM_LUGAR"] == nom_ubic_selecc),
                "CVE_LUGAR",
            ]
        )[0]

    elif tipo_ubicacion == "Metrópolis":
        IdUbic = list(
            dfLugar.loc[
                (dfLugar["TIPO_LUGAR"] == "Metropoli")
                & (dfLugar["NOM_LUGAR"] == nom_ubic_selecc),
                "CVE_LUGAR",
            ]
        )[0]
    else:
        IdUbic = list(
            dfLugar.loc[
                (dfLugar["TIPO_LUGAR"] == "Municipio")
                & (dfLugar["NOM_LUGAR"] == nom_ubic_selecc),
                "CVE_LUGAR",
            ]
        )[0]

    pob_ubi = int(
        list(
            dfPobExtendida.loc[
                (dfPobExtendida["CVE_LUGAR"] == IdUbic)
                & (dfPobExtendida["Year"] == MAX_YEAR),
                "Num_Habs",
            ]
        )[0]
    )

    txt_habitantes = f"{pob_ubi:,}" + " habs." + " (est. " + str(MAX_YEAR) + ")"
    st.caption(
        '<p style="text-align: right;">' + txt_habitantes + "</p>",
        unsafe_allow_html=True,
    )


with st.sidebar.expander(":chart_with_upwards_trend: Formato de la gráfica"):
    AnchoBar = st.select_slider(
        "Seleccione el ancho de barra:", options=np.arange(5, 20, 0.5), value=10.5
    )
    AnchoLinea = st.select_slider(
        "Seleccione el ancho de línea:", options=np.arange(2.5, 10, 0.5), value=4
    )
    tipo_linea = st.selectbox(
        "Seleccione tipo de línea:", ["-", "--", "-.", ":", "None"]
    )
    selected_color_barra = st.color_picker(
        "Seleccione color para barra:", "#2f4f4f"
    )  # darkslategrey
    selected_color_linea = st.color_picker(
        "Seleccione color para línea:", "#FF796C"
    )  # salmon


# Cuerpo Streamlit
tab1, tab2 = st.tabs(["Grafica general", "Perfil de riesgo"])


# Primera Tab
with tab1:

    list_aniomes = dfAniomes["Aniomes"].unique()
    list_aniomes.sort()
    Aniomes_Ini, Aniomes_Fin = st.select_slider(
        ":calendar: Seleccione los meses a considerar:",
        options=list_aniomes,
        value=(list_aniomes[-12], list_aniomes[-1]),
    )

    # ---------------------------------------------------------------
    # Empezar a construir el Dataframe deseado con todos los Aniomes
    df = dfAniomes.loc[
        (dfAniomes["Aniomes"] >= Aniomes_Ini) & (dfAniomes["Aniomes"] <= Aniomes_Fin),
        "Aniomes",
    ]

    # ---------------------------------------------------
    # Contruir la consulta

    if BASE_DE_DATOS == "mongodb":
        collection = db["dfDefinitivo"]
        query = {
            "$and": [
                {"CVE_LUGAR": IdUbic},
                {"Aniomes": {"$gte": Aniomes_Ini}},
                {"Aniomes": {"$lte": Aniomes_Fin}},
                {"Id_Agrupador_Delito": IdAgrupDel},
            ]
        }
        results = collection.find(query)
        dfResUbi = pd.DataFrame(list(results))
    elif BASE_DE_DATOS == "postgresql":
        query = f'SELECT * FROM "dfDefinitivo" WHERE  "CVE_LUGAR" = \'{IdUbic}\' AND "Aniomes" >= \'{Aniomes_Ini}\' AND "Aniomes" <= \'{Aniomes_Fin}\' AND "Id_Agrupador_Delito" = \'{IdAgrupDel}\''
        dfResUbi = pd.read_sql_query(query, engine)

    if "_id" in dfResUbi.columns:  # solo aplica si el dataframe vino de Mongodb
        dfResUbi.drop(columns=["_id"], inplace=True)

    flag_resultados = bool(len(dfResUbi))
    if (
        flag_resultados
    ):  # si no hay recuperación de resultados se queda el dataframe original solo con Aniomes
        df = pd.merge(df, dfResUbi, on="Aniomes", how="left").fillna(0)

    # Recuperar los datos nacionales
    if BASE_DE_DATOS == "mongodb":
        collection = db["dfDefinitivo"]
        query_nal = {
            "$and": [
                {"CVE_LUGAR": "P00"},
                {"Aniomes": {"$gte": Aniomes_Ini}},
                {"Aniomes": {"$lte": Aniomes_Fin}},
                {"Id_Agrupador_Delito": IdAgrupDel},
            ]
        }
        results_nal = collection.find(query_nal)
        dfResNal = pd.DataFrame(list(results_nal))
        if "_id" in dfResNal.columns:
            dfResNal.drop(columns=["_id"], inplace=True)
    elif BASE_DE_DATOS == "postgresql":
        query = f'SELECT * FROM "dfDefinitivo" WHERE "CVE_LUGAR" = \'P00\' AND "Aniomes" >= \'{Aniomes_Ini}\' AND "Aniomes" <= \'{Aniomes_Fin}\' AND "Id_Agrupador_Delito" = \'{IdAgrupDel}\''
        dfResNal = pd.read_sql_query(query, engine)
    dfResNal.rename(columns={"tasa": "tasa_nal"}, inplace=True)

    # Aquí se fusionan los datos de ubicación con los nacionales
    df = pd.merge(df, dfResNal, on="Aniomes")
    df.sort_values(by="Aniomes", inplace=True)

    # ---------------------------------------------------
    # Contruir la gráfica
    dftemp = df.copy()
    dftemp["dt64"] = dftemp["Aniomes"].apply(get_dt64)

    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter("%Y")
    months_fmt = mdates.DateFormatter("%b")
    fmt = mdates.DateFormatter("%Y-%m")

    fig, ax = plt.subplots(1, 1, figsize=(16.0, 10.0), layout="constrained")
    fig.set_constrained_layout_pads(
        w_pad=2.0 / 12.0, h_pad=8.0 / 12.0, hspace=0.0, wspace=0.0
    )

    ax.bar(
        "dt64",
        "tasa",
        data=dftemp,
        width=AnchoBar,
        color=selected_color_barra,
        label="tasa municipal",
    )
    ax.plot(
        "dt64",
        "tasa_nal",
        data=dftemp,
        linewidth=AnchoLinea,
        linestyle=tipo_linea,
        color=selected_color_linea,
        label="tasa nacional",
    )

    ax.bar_label(ax.containers[0], label_type="edge", fontsize=10, color="black")

    # ax.xaxis.set_major_locator(years)
    # ax.xaxis.set_major_locator(months)
    # ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_major_formatter(fmt)

    ax.xaxis.set_minor_locator(months)
    # ax.xaxis.set_minor_formatter(months_fmt)

    ax.set_xlabel("Periodo", fontsize=14, color="black")
    ax.set_ylabel("Tasa delictiva", fontsize=14, color="black")

    titulo_grafica = (
        "Tasa delictiva mensual de " + nom_agrupador_selecc + " \n" + nom_ubic_selecc
    )
    ax.set_title(titulo_grafica, fontsize=26, color="darkslategrey")

    ax.grid(which="major", alpha=0.2)
    fig.legend(loc="lower right", fontsize="10", shadow=True)

    st.pyplot(fig)

    # ---------------------------------------------------
    # Columnas de variación
    dftemp["Variacion"] = dftemp["tasa"].pct_change() * 100
    dftemp.replace([np.inf, -np.inf], np.nan, inplace=True)
    variacion_promedio = round(dftemp["Variacion"].mean(skipna=True), 1)
    txt_variacion = str(variacion_promedio) + "%"
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label=":triangular_ruler: Variación mensual promedio",
            value="_",
            delta=txt_variacion,
            delta_color="inverse",
        )
    # with col2:
    #    st.metric(label="Variación últimos tres meses", value="_", delta="-2%", delta_color= "inverse")

    # ---------------------------------------------------
    # Tabla de datos
    with st.expander(":page_with_curl: Ver tabla de datos"):
        # st.table(dftemp[['Aniomes','tasa','tasa_nal']])
        st.dataframe(dftemp[["Aniomes", "tasa", "tasa_nal"]])

with tab2:
    st.write("Hola Mundo")
# ---------------------------------------------------
# Cierre de conexión
client.close()
engine.dispose()
