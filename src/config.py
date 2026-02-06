import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_env_variable(name: str, default: str = None, required: bool = True) -> str:
    value = os.getenv(name, default)
    if required and value is None:
        raise ValueError(f"❌ La variable de entorno {name} no está definida.")
    return value

# Variables exportadas explícitamente
REPOSITORY = get_env_variable("REPOSITORY")
REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = int(get_env_variable("REDIS_PORT"))
REDIS_USERNAME = get_env_variable("REDIS_USERNAME", "default")
REDIS_PASSWORD = get_env_variable("REDIS_PASSWORD")
REDIS_DB = int(get_env_variable("REDIS_DB", "0"))
OPENAI_API_KEY = get_env_variable("OPENAI_API_KEY")
DEBUG_EXPORT_JSON = get_env_variable("DEBUG_EXPORT_JSON", "false", required=False).lower() == "true"
DB_POSTGRES_NAME = get_env_variable("DB_POSTGRES_NAME")
DB_POSTGRES_USER = get_env_variable("DB_POSTGRES_USER")
DB_POSTGRES_PASSWORD = get_env_variable("DB_POSTGRES_PASSWORD")
DB_POSTGRES_HOST = get_env_variable("DB_POSTGRES_HOST")
DB_POSTGRES_PORT = int(get_env_variable("DB_POSTGRES_PORT"))

print("✅ Configuración cargada y validada correctamente.")

print(f"🔍 [DEBUG] DB Host: {DB_POSTGRES_HOST}")
print(f"🔍 [DEBUG] DB Port: {DB_POSTGRES_PORT}")
print(f"🔍 [DEBUG] DB Name: {DB_POSTGRES_NAME}")
print(f"🔍 [DEBUG] DB User: {DB_POSTGRES_USER}")
# No imprimir contraseña completa, solo longitud o primeros caracteres si es seguro
print(f"🔍 [DEBUG] DB Password Length: {len(str(DB_POSTGRES_PASSWORD))}")
