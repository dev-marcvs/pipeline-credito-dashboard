from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

# Conecta ao banco PostgreSQL via SQLAlchemy
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/postgres")

# Lê dados do banco
fundo_df = pd.read_sql("SELECT * FROM dim_fundo", con=engine)
cessao_df = pd.read_sql("SELECT * FROM fact_cessao", con=engine)
estoque_df = pd.read_sql("SELECT * FROM fact_estoque", con=engine)
baixa_df = pd.read_sql("SELECT * FROM fact_baixa", con=engine)

# Ajustes após merge
cessao_df = cessao_df.merge(fundo_df, left_on="cnpj_fundo", right_on="cnpj", how="left")
estoque_df = estoque_df.merge(fundo_df, left_on="CNPJ_FUNDO", right_on="cnpj", how="left")
baixa_df = baixa_df.merge(fundo_df, left_on="FUNDO", right_on="nome", how="left")

# Renomeia a coluna "nome" para "FUNDO" para padronizar
cessao_df.rename(columns={"nome": "FUNDO"}, inplace=True)
estoque_df.rename(columns={"nome": "FUNDO"}, inplace=True)

# Conversões
cessao_df["vl_presente"] = cessao_df["vl_presente"].astype(float)
estoque_df["VALOR_PRESENTE"] = estoque_df["VALOR_PRESENTE"].astype(float)
baixa_df["VALOR_PAGO"] = baixa_df["VALOR_PAGO"].astype(float)

baixa_df["DATA_MOVIMENTO"] = pd.to_datetime(baixa_df["DATA_MOVIMENTO"], errors="coerce")
baixa_df["DATA_AQUISICAO"] = pd.to_datetime(baixa_df["DATA_AQUISICAO"], errors="coerce")
baixa_df["TEMPO_ATE_BAIXA"] = (baixa_df["DATA_MOVIMENTO"] - baixa_df["DATA_AQUISICAO"]).dt.days

# KPIs por fundo
kpi_df = fundo_df[["nome", "cnpj"]].drop_duplicates().copy()
kpi_df = kpi_df.rename(columns={"nome": "FUNDO"})

cedido = cessao_df.groupby("FUNDO")["vl_presente"].sum().reset_index(name="valor_cedido")
kpi_df = kpi_df.merge(cedido, on="FUNDO", how="left")

estoque = estoque_df.groupby("FUNDO")["VALOR_PRESENTE"].sum().reset_index(name="volume_estoque")
kpi_df = kpi_df.merge(estoque, on="FUNDO", how="left")

baixa = baixa_df.groupby("FUNDO").agg(
    valor_recebido=pd.NamedAgg(column="VALOR_PAGO", aggfunc="sum"),
    tempo_medio_ate_baixa=pd.NamedAgg(column="TEMPO_ATE_BAIXA", aggfunc="mean")
).reset_index()
kpi_df = kpi_df.merge(baixa, on="FUNDO", how="left")

kpi_df["retorno_realizado"] = kpi_df["valor_recebido"] / kpi_df["valor_cedido"]

hoje = pd.Timestamp(datetime.today().date())
estoque_df["DATA_VENCIMENTO"] = pd.to_datetime(estoque_df["DATA_VENCIMENTO"], errors="coerce")
estoque_df["vencido"] = estoque_df["DATA_VENCIMENTO"] < hoje

inad = estoque_df.groupby("FUNDO").agg(
    total=("VALOR_PRESENTE", "sum"),
    vencido=("VALOR_PRESENTE", lambda x: x[estoque_df.loc[x.index, "vencido"].values].sum())
).reset_index()
inad["inadimplencia"] = inad["vencido"] / inad["total"]

kpi_df = kpi_df.merge(inad[["FUNDO", "inadimplencia"]], on="FUNDO", how="left")

# STREAMLIT DASHBOARD
st.set_page_config(layout="wide")
st.title("Dashboard - PostgreSQL")

fundo = st.selectbox("Selecione o fundo:", kpi_df["FUNDO"].unique())
dados = kpi_df[kpi_df["FUNDO"] == fundo].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Volume Cedido", f"R$ {dados['valor_cedido']:,.2f}")
col2.metric("Estoque Atual", f"R$ {dados['volume_estoque']:,.2f}")
col3.metric("Valor Recebido", f"R$ {dados['valor_recebido']:,.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Retorno Realizado", f"{dados['retorno_realizado']:.2f}x")
col5.metric("Tempo Médio até Baixa", f"{dados['tempo_medio_ate_baixa']:.2f} dias")
col6.metric("Inadimplência", f"{dados['inadimplencia']*100:.2f}%")

# AGING
aging_df = estoque_df[estoque_df["FUNDO"] == fundo].copy()
aging_df["dias_em_atraso"] = (hoje - aging_df["DATA_VENCIMENTO"]).dt.days

def faixa_aging(d):
    if d < 0: return "A vencer"
    elif d <= 30: return "0–30 dias"
    elif d <= 60: return "31–60 dias"
    elif d <= 90: return "61–90 dias"
    return "91+ dias"

aging_df["faixa"] = aging_df["dias_em_atraso"].apply(faixa_aging)
aging_grouped = aging_df.groupby("faixa")["VALOR_PRESENTE"].sum().reset_index()

st.subheader("Aging dos Recebíveis")
fig, ax = plt.subplots()
ax.bar(aging_grouped["faixa"], aging_grouped["VALOR_PRESENTE"])
ax.set_ylabel("Valor total (R$)")
ax.set_title("Distribuição por Faixa de Atraso")
st.pyplot(fig)