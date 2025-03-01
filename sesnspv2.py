"""Main entry point for the Streamlit crime statistics application."""

import streamlit as st
from config.settings import setup_page_config
from data.database import init_connections, close_connections
from models.catalogs import load_catalogs
from ui.sidebar import render_sidebar
from ui.tabs.tab_general import render_general_tab


def main():
    """Main application function."""
    # Initialize page configuration
    setup_page_config()

    # Initialize database connections
    client, engine = init_connections()

    # Load all catalogs
    catalogs = load_catalogs(client, engine)

    # App title
    st.title(":arrow_right: Generación de gráficas delictivas")

    # Render sidebar and get selected options
    sidebar_options = render_sidebar(catalogs)

    # Create tabs
    tab1, tab2 = st.tabs(["Grafica general", "."])

    # Render content for each tab
    with tab1:
        render_general_tab(catalogs, sidebar_options, client, engine)

    with tab2:
        pass

    # Close database connections
    close_connections(client, engine)


if __name__ == "__main__":
    main()
