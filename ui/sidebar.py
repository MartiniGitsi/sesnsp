"""Sidebar UI components for the application."""

import streamlit as st
import numpy as np
from utils.helpers import get_ubicaciones


def render_sidebar(catalogs):
    """Render the sidebar UI and return selected options.

    Args:
        catalogs: Dictionary of catalog dataframes

    Returns:
        dict: Dictionary of selected options
    """
    st.sidebar.header("🔧 Ajustes")

    # Crime type selection
    df_cab_agrp = catalogs["cab_agrupador_delito"]
    nom_agrupador_selecc = st.sidebar.selectbox(
        ":rotating_light: Seleccione un delito:", df_cab_agrp["Nombre_Agrupador_Delito"]
    )
    id_agrup_del = list(
        df_cab_agrp.loc[
            df_cab_agrp["Nombre_Agrupador_Delito"] == nom_agrupador_selecc,
            "Id_Agrupador_Delito",
        ]
    )[0]

    # Location controls
    location_options = render_location_controls(catalogs)

    # Chart format controls
    chart_options = render_chart_format_controls()

    # Return all selected options
    return {
        "nom_agrupador_selecc": nom_agrupador_selecc,
        "id_agrup_del": id_agrup_del,
        **location_options,
        **chart_options,
    }


def render_location_controls(catalogs):
    """Render location selection controls.

    Args:
        catalogs: Dictionary of catalog dataframes

    Returns:
        dict: Dictionary of selected location options
    """
    df_lugar = catalogs["lugar"]
    df_pob_extendida = catalogs["poblacion_extendida"]
    max_year = catalogs["max_year"]

    with st.sidebar.expander(":earth_americas: Control de ubicaciones"):
        tipo_ubicacion = st.radio(
            "Seleccione:",
            [
                "Nacional",
                "Entidades",
                "Metrópolis",
                "Municipios 800K+",
                "Municipios 400K+",
                "Municipios 100K+",
                "Todos los municipios",
            ],
        )

        nom_ubic_selecc = st.selectbox(
            ":round_pushpin: Seleccione ubicación principal:",
            get_ubicaciones(catalogs, tipo_ubicacion, max_year),
        )

        # Get location ID based on selected location type
        if tipo_ubicacion == "Nacional":
            id_ubic = list(
                df_lugar.loc[
                    (df_lugar["TIPO_LUGAR"] == "Pais")
                    & (df_lugar["NOM_LUGAR"] == nom_ubic_selecc),
                    "CVE_LUGAR",
                ]
            )[0]
            id_ent_asoc = "0"
        elif tipo_ubicacion == "Entidades":
            id_ubic, id_ent_asoc = (
                df_lugar.loc[
                    (df_lugar["TIPO_LUGAR"] == "Entidad")
                    & (df_lugar["NOM_LUGAR"] == nom_ubic_selecc),
                    ["CVE_LUGAR", "CVE_ENT"],
                ]
            ).iloc[0]

        elif tipo_ubicacion == "Metrópolis":
            id_ubic, id_ent_asoc = (
                df_lugar.loc[
                    (df_lugar["TIPO_LUGAR"] == "Metropoli")
                    & (df_lugar["NOM_LUGAR"] == nom_ubic_selecc),
                    ["CVE_LUGAR", "CVE_ENT"],
                ]
            ).iloc[0]
        else:
            id_ubic, id_ent_asoc = (
                df_lugar.loc[
                    (df_lugar["TIPO_LUGAR"] == "Municipio")
                    & (df_lugar["NOM_LUGAR"] == nom_ubic_selecc),
                    ["CVE_LUGAR", "CVE_ENT"],
                ]
            ).iloc[0]

        # Get population for selected location
        pob_ubi = int(
            list(
                df_pob_extendida.loc[
                    (df_pob_extendida["CVE_LUGAR"] == id_ubic)
                    & (df_pob_extendida["Year"] == max_year),
                    "Num_Habs",
                ]
            )[0]
        )

        # Display population information
        txt_habitantes = f"{pob_ubi:,}" + " habs." + " (est. " + str(max_year) + ")"
        st.caption(
            '<p style="text-align: right;">' + txt_habitantes + "</p>",
            unsafe_allow_html=True,
        )

    return {
        "tipo_ubicacion": tipo_ubicacion,
        "nom_ubic_selecc": nom_ubic_selecc,
        "id_ubic": id_ubic,
        "id_ent_asoc": id_ent_asoc,
        "pob_ubi": pob_ubi,
    }


def render_chart_format_controls():
    """Render chart formatting controls.

    Returns:
        dict: Dictionary of selected chart formatting options
    """
    chart_options = {}

    with st.sidebar.expander(":chart: Personalización de la gráfica"):
        chart_options["multi_seleccion_ubi"] = st.multiselect(
            "Incluir adicional",
            ["Nacional", "Entidad", "Tendencia"],
        )
        chart_options["multi_seleccion_marcas"] = st.multiselect(
            "Indicar marcas",
            ["Barra", "Línea", "Línea", "Línea"],
            default="Barra",
        )
        chart_options["selected_color_1elem"] = st.color_picker(
            "Seleccione color para 1er elemento:", "#2f4f4f"
        )
        chart_options["selected_color_2elem"] = st.color_picker(
            "Seleccione color para 2do elemento:", "#FF796C"
        )
        chart_options["selected_color_3elem"] = st.color_picker(
            "Seleccione color para 3er elemento:", "#6cb6ef"
        )

    with st.sidebar.expander(":chart_with_upwards_trend: Formato de las series"):
        chart_options["ancho_bar"] = st.select_slider(
            "Seleccione el ancho de barra:", options=np.arange(5, 20, 0.5), value=10.5
        )
        chart_options["ancho_linea"] = st.select_slider(
            "Seleccione el ancho de línea:", options=np.arange(2.5, 10, 0.5), value=4
        )
        chart_options["tipo_linea"] = st.selectbox(
            "Seleccione tipo de línea:", ["-", "--", "-.", ":", "None"]
        )

    return chart_options
