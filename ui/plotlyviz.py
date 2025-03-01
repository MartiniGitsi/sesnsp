import numpy as np
import plotly.graph_objects as go


def create_plotly_risk_chart(
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
        plotly figure: Generated chart
    """

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["Aniomes"],
            y=df["tasa"],
            orientation="h",
            text=df["tasa"],
            textfont=dict(size=19, family="Arial"),
        )
    )

    fig.update_layout(
        title="Multiple Bars and Lines",
        xaxis_title="Categories",
        yaxis_title="Values",
        barmode="group",  # Use "stack" for stacked bars
    )

    return fig
