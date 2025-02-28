import streamlit as st

# Database configuration
BASE_DE_DATOS = "postgresql"  # ['mongodb','postgresql']

# MongoDB settings
MONGODB_URI = st.secrets["mongodb_uri"]
MONGODB_DB_NAME = "dbmongo_sesnsp"

# PostgreSQL settings
PG_USER = "postgres.ojioiftryayyihlqnitm"
PG_PASSWORD = "Supra.Normal1"
PG_HOST = "aws-0-us-west-1.pooler.supabase.com"
PG_PORT = 6543
PG_DB_NAME = "postgres"
PG_DATABASE_URL = (
    f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB_NAME}"
)


def setup_page_config():
    """Set Streamlit page configuration."""
    st.set_page_config(
        page_title="Estadísticas Delictivas",  # Title shown on browser tab
        page_icon=":bar_chart:",  # Favicon (emoji or URL)
        layout="wide",  # Options: "centered" or "wide"
        initial_sidebar_state="expanded",  # Options: "auto", "expanded", "collapsed"
    )
