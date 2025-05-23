from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

# Conectar ao PostgreSQL
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

# Data da carga incremental (simulação)
data_ingestao = pd.Timestamp.today().normalize()

# Lista de arquivos e tabelas
tabelas = [
    {
        "nome": "fact_cessao",
        "arquivo": "data/aquisicao_dia_database_fundo_teste.csv",
        "sep": ";",
        "preprocessamento": lambda df: preprocessar_cessao(df)
    },
    {
        "nome": "fact_estoque",
        "arquivo": "data/estoque_aquisicoes_database_fundo_teste.csv",
        "sep": ";",
        "preprocessamento": lambda df: preprocessar_estoque(df)
    },
    {
        "nome": "fact_baixa",
        "arquivo": "data/liquidados_estoque_database_fundo_teste.csv",
        "sep": ";",
        "preprocessamento": lambda df: preprocessar_baixa(df)
    }
]

def preprocessar_cessao(df):
    df["vl_presente"] = df["vl_presente"].str.replace(",", ".").astype(float)
    df["valor_futuro_nominal"] = df["valor_futuro_nominal"].str.replace(",", ".").astype(float)
    df["dt_cessao"] = pd.to_datetime(df["dt_cessao"], dayfirst=True, errors="coerce")
    df["data_vencimento_da_parcela"] = pd.to_datetime(df["data_vencimento_da_parcela"], dayfirst=True, errors="coerce")
    df["data_ingestao"] = data_ingestao
    return df

def preprocessar_estoque(df):
    for col in ["VALOR_PRESENTE", "VALOR_FUTURO", "VALOR_AQUISICAO"]:
        df[col] = df[col].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    df["DATA_AQUISICAO"] = pd.to_datetime(df["DATA_AQUISICAO"], dayfirst=True, errors="coerce")
    df["DATA_VENCIMENTO"] = pd.to_datetime(df["DATA_VENCIMENTO"], dayfirst=True, errors="coerce")
    df["data_ingestao"] = data_ingestao
    return df

def preprocessar_baixa(df):
    df["VALOR_PAGO"] = df["VALOR_PAGO"].str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    df["DATA_MOVIMENTO"] = pd.to_datetime(df["DATA_MOVIMENTO"], dayfirst=True, errors="coerce")
    df["DATA_AQUISICAO"] = pd.to_datetime(df["DATA_AQUISICAO"], dayfirst=True, errors="coerce")
    df["data_ingestao"] = data_ingestao
    return df

# Rodar a carga incremental
for tabela in tabelas:
    nome = tabela["nome"]
    arquivo = tabela["arquivo"]
    print(f"Carregando {nome}...")

    df = pd.read_csv(arquivo, encoding="latin1", sep=tabela["sep"])
    df = tabela["preprocessamento"](df)

    with engine.connect() as conn:
        existentes = pd.read_sql(f"SELECT DISTINCT data_ingestao FROM {nome}", conn)
        if data_ingestao in existentes["data_ingestao"].values:
            print(f"Carga de {nome} para {data_ingestao.date()} já existe. Pulando.")
            continue
        df.to_sql(nome, con=engine, if_exists="append", index=False)
        print(f"{nome} carregado com sucesso ({len(df)} registros).")
