"""Functions for generating visualizations."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.helpers import get_dt64


def create_crime_chart(
    df, chart_parameteres, chart_options, nom_agrupador_selecc, nom_ubic_selecc
):
    """Create a crime statistics chart.

    Args:
        df: DataFrame with crime data
        chart_parameteres: parámetros específicos
        chart_options: Dictionary of chart format options
        nom_agrupador_selecc: Selected crime group name
        nom_ubic_selecc: Selected location name

    Returns:
        matplotlib.figure.Figure: Generated chart
    """
    # Create a copy of the dataframe for visualization
    dftemp = df.copy()
    dftemp["dt64"] = dftemp["Aniomes"].apply(get_dt64)

    # Set up date formatters
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    years_fmt = mdates.DateFormatter("%Y")
    months_fmt = mdates.DateFormatter("%b")
    fmt = mdates.DateFormatter("%Y-%m")

    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16.0, 10.0), layout="constrained")
    fig.set_constrained_layout_pads(
        w_pad=2.0 / 12.0, h_pad=8.0 / 12.0, hspace=0.0, wspace=0.0
    )

    # Plot data based on selected markers

    for index, elem in enumerate(range(0, chart_parameteres["n_elementos"])):
        if chart_parameteres["Serie_marca"][index] == "Barra":
            ax.bar(
                "dt64",
                chart_parameteres["Serie_campo"][index],
                data=dftemp,
                width=chart_parameteres["ancho_bar"],
                color=chart_parameteres["Serie_color"][index],
                label=chart_parameteres["Serie_leyenda"][index],
            )
        else:
            ax.plot(
                "dt64",
                chart_parameteres["Serie_campo"][index],
                data=dftemp,
                linewidth=chart_parameteres["ancho_linea"],
                linestyle=chart_parameteres["tipo_linea"],
                color=chart_parameteres["Serie_color"][index],
                label=chart_parameteres["Serie_leyenda"][index],
            )

    # Configure x-axis
    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_locator(months)

    # Set labels and title
    ax.set_xlabel("Periodo", fontsize=14, color="black")
    ax.set_ylabel("Tasa delictiva", fontsize=14, color="black")

    titulo_grafica = (
        "Tasa delictiva mensual de " + nom_agrupador_selecc + " \n" + nom_ubic_selecc
    )
    ax.set_title(titulo_grafica, fontsize=26, color="darkslategrey")

    # Add grid and legend
    ax.grid(which="major", alpha=0.2)
    fig.legend(loc="lower right", fontsize="10", shadow=True)

    return fig


def calculate_variations(df):
    """Calculate variation metrics for crime data.

    Args:
        df: DataFrame with crime data

    Returns:
        tuple: (df with variations, average variation percentage)
    """
    # Create a copy of the dataframe
    dftemp = df.copy()

    # Calculate month-to-month percentage changes
    dftemp["Variacion"] = dftemp["tasa"].pct_change() * 100
    dftemp.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Calculate average variation
    variacion_promedio = round(dftemp["Variacion"].mean(skipna=True), 1)

    return dftemp, variacion_promedio
