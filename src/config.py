"""
Módulo de Configuración y Conexión para el Pipeline ETL INF-522.
Gestiona variables de entorno y conexiones a PostgreSQL sin credenciales quemadas en el código.
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Configuración de PostgreSQL (valores por defecto seguros para entorno local/Docker)
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
PG_DATABASE = os.getenv("PG_DATABASE", "dw_astronomia")

# Endpoints de APIs públicas de Chile
ESO_API_URL = os.getenv("ESO_API_URL", "https://archive.eso.org/tap_obs/sync")
ALERCE_API_URL = os.getenv("ALERCE_API_URL", "https://api.alerce.online/ztf/v1/objects/")

# Rangos MJD por defecto sincronizados: Octubre 2026 (Observaciones contemporáneas en Chile)
# MJD 61300 = 2026-09-17 | MJD 61341 = 2026-10-28 (Detecciones en tiempo real) | MJD 61350 = 2026-11-06
DEFAULT_MJD_INICIO = float(os.getenv("MJD_INICIO", 61300.0))
DEFAULT_MJD_FIN = float(os.getenv("MJD_FIN", 61350.0))

def get_connection():
    """Retorna una conexión activa a PostgreSQL."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )

def get_connection_string():
    """Retorna el connection string para SQLAlchemy o herramientas de datos."""
    return f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
