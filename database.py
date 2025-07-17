# database.py

from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def get_database_url():
    """Constrói a URL do banco usando apenas a conexão pooler"""
    user = getenv("USER")
    password = getenv("PASSWORD")
    host = getenv("HOST")
    port = getenv("PORT")
    dbname = getenv("DBNAME")
    
    if not all([user, password, host, port, dbname]):
        raise ValueError("Variáveis de ambiente do pooler não encontradas")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

DATABASE_URL = get_database_url()

# Configurações do engine otimizadas para Supabase Pooler
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mude para True para debug
    pool_pre_ping=True,  # Verifica conexões antes de usar
    pool_recycle=3600,   # Recicla conexões a cada hora
    pool_size=5,         # Tamanho do pool de conexões
    max_overflow=10,     # Máximo de conexões extras
    connect_args={
        "sslmode": "require",
        "connect_timeout": 30,
        "application_name": "fastapi-darc-app"
    }
)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        raise