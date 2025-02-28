"""Helper functions for the application."""

import pandas as pd
import numpy as np
import datetime
from sklearn.linear_model import LinearRegression


def get_dt64(aniomes) -> np.datetime64:
    """Convert Aniomes (YYYYMM) to numpy.datetime64 format.

    Args:
        aniomes: Year and month in YYYYMM format

    Returns:
        np.datetime64: Datetime representation
    """
    year = aniomes // 100
    mes = aniomes % 100  # Fixed from original code which used "% year"
    dt = datetime.datetime(year, mes, 1)
    dt64 = np.datetime64(dt)
    return dt64


def get_ubicaciones(catalogs, tipo_ubicacion, max_year):
    """Get list of locations based on selected location type.

    Args:
        catalogs: Dictionary of catalog dataframes
        tipo_ubicacion: Type of location to filter
        max_year : Año más reciente

    Returns:
        Series: List of location names
    """
    df_lugar = catalogs["lugar"]
    df_poblacion_extendida = catalogs["poblacion_extendida"]

    match tipo_ubicacion:
        case "Nacional":
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Pais", ["NOM_LUGAR", "CVE_LOCAL"]
            ]
        case "Entidades":
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Entidad", ["NOM_LUGAR", "CVE_LOCAL"]
            ]
        case "Metrópolis":
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Metropoli", ["NOM_LUGAR", "CVE_LOCAL"]
            ]
        case "Municipios 800K+":
            df_poblacion_extendida = df_poblacion_extendida.loc[
                (df_poblacion_extendida["Year"] == max_year)
                & (df_poblacion_extendida["TIPO_LUGAR"] == "Municipio")
                & (df_poblacion_extendida["Num_Habs"] >= 800_000),
                "CVE_LUGAR",
            ]
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Municipio",
                ["CVE_LUGAR", "NOM_LUGAR", "CVE_LOCAL"],
            ]
            df_lugar_sel = pd.merge(
                df_lugar_sel, df_poblacion_extendida, how="inner", on="CVE_LUGAR"
            )
            df_lugar_sel = df_lugar_sel[["NOM_LUGAR", "CVE_LOCAL"]]
        case "Municipios 400K+":
            df_poblacion_extendida = df_poblacion_extendida.loc[
                (df_poblacion_extendida["Year"] == max_year)
                & (df_poblacion_extendida["TIPO_LUGAR"] == "Municipio")
                & (df_poblacion_extendida["Num_Habs"] >= 400_000),
                "CVE_LUGAR",
            ]
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Municipio",
                ["CVE_LUGAR", "NOM_LUGAR", "CVE_LOCAL"],
            ]
            df_lugar_sel = pd.merge(
                df_lugar_sel, df_poblacion_extendida, how="inner", on="CVE_LUGAR"
            )
            df_lugar_sel = df_lugar_sel[["NOM_LUGAR", "CVE_LOCAL"]]
        case "Municipios 100K+":
            df_poblacion_extendida = df_poblacion_extendida.loc[
                (df_poblacion_extendida["Year"] == max_year)
                & (df_poblacion_extendida["TIPO_LUGAR"] == "Municipio")
                & (df_poblacion_extendida["Num_Habs"] >= 100_000),
                "CVE_LUGAR",
            ]
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Municipio",
                ["CVE_LUGAR", "NOM_LUGAR", "CVE_LOCAL"],
            ]
            df_lugar_sel = pd.merge(
                df_lugar_sel, df_poblacion_extendida, how="inner", on="CVE_LUGAR"
            )
            df_lugar_sel = df_lugar_sel[["NOM_LUGAR", "CVE_LOCAL"]]
        case "Todos los municipios":
            df_lugar_sel = df_lugar.loc[
                df_lugar["TIPO_LUGAR"] == "Municipio", ["NOM_LUGAR", "CVE_LOCAL"]
            ]
    return df_lugar_sel


def get_trend(df):
    """Conseguir la regresión lineal del campo de tasa

    Args:
        df: Dataframe con la cifra delictiva

    Returns:
        Series: Dataframe con los resultados de la regresión
    """
    # Create X (independent variable) - using row indices
    X = np.array(range(len(df))).reshape(-1, 1)

    # Create y (dependent variable) - the rate column
    y = df["tasa"].values

    # Create and fit the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Calculate the predicted values and add them as a new column
    df["rate_regression"] = model.predict(X)
    return df[["Aniomes", "rate_regression"]]


def get_chart_parameters(sidebar_options):
    """Conseguir la configuración ideal de parámetros para la gráfica general

    Args:
        sidebar_options: El diccionario de las opciones seleccionadfas en sidebar

    Returns:
        Series: Dicionario especpifico para la gráfica
    """
    dicc_basico = {
        "Nacional": "tasa_nal",
        "Entidad": "tasa_est",
        "Tendencia": "rate_regression",
    }

    len_multi_seleccion_ubi = len(sidebar_options["multi_seleccion_ubi"])
    len_multi_seleccion_marcas = len(sidebar_options["multi_seleccion_marcas"])

    n_elementos_ubi = 1
    dicc_parametros = {}
    dicc_parametros["Serie_campo"] = ["tasa"]
    dicc_parametros["Serie_leyenda"] = ["Ubicación referida"]
    if len_multi_seleccion_ubi == 1:
        dicc_parametros["Serie_campo"].append(
            dicc_basico[sidebar_options["multi_seleccion_ubi"][0]]
        )
        dicc_parametros["Serie_leyenda"].append(
            sidebar_options["multi_seleccion_ubi"][0]
        )
        n_elementos_ubi = 2
    if len_multi_seleccion_ubi == 2:
        dicc_parametros["Serie_campo"].append(
            dicc_basico[sidebar_options["multi_seleccion_ubi"][0]]
        )
        dicc_parametros["Serie_campo"].append(
            dicc_basico[sidebar_options["multi_seleccion_ubi"][1]]
        )

        dicc_parametros["Serie_leyenda"].append(
            sidebar_options["multi_seleccion_ubi"][0]
        )
        dicc_parametros["Serie_leyenda"].append(
            sidebar_options["multi_seleccion_ubi"][1]
        )

        n_elementos_ubi = 3

    n_elementos_marca = 0
    if len_multi_seleccion_marcas == 0:
        dicc_parametros["Serie_marca"] = ["Línea"]
        n_elementos_marca = 1
    if len_multi_seleccion_marcas == 1:
        dicc_parametros["Serie_marca"] = [sidebar_options["multi_seleccion_marcas"][0]]
        n_elementos_marca = 1
    if len_multi_seleccion_marcas == 2:
        dicc_parametros["Serie_marca"] = [sidebar_options["multi_seleccion_marcas"][0]]
        dicc_parametros["Serie_marca"].append(
            sidebar_options["multi_seleccion_marcas"][1]
        )
        n_elementos_marca = 2
    if len_multi_seleccion_marcas >= 3:
        dicc_parametros["Serie_marca"] = [sidebar_options["multi_seleccion_marcas"][0]]
        dicc_parametros["Serie_marca"].append(
            sidebar_options["multi_seleccion_marcas"][1]
        )
        dicc_parametros["Serie_marca"].append(
            sidebar_options["multi_seleccion_marcas"][2]
        )
        n_elementos_marca = 3

    dicc_parametros["Serie_color"] = [
        sidebar_options["selected_color_1elem"],
        sidebar_options["selected_color_2elem"],
        sidebar_options["selected_color_3elem"],
    ]

    dicc_parametros["ancho_bar"] = sidebar_options["ancho_bar"]
    dicc_parametros["ancho_linea"] = sidebar_options["ancho_linea"]
    dicc_parametros["tipo_linea"] = sidebar_options["tipo_linea"]
    dicc_parametros["n_elementos"] = min(n_elementos_ubi, n_elementos_marca)

    return dicc_parametros
