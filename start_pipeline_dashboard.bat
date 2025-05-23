@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Iniciando PostgreSQL (Docker)...
docker start postgres

echo Rodando carga incremental...
python carga_incremental_postgres.py

echo Abrindo o dashboard no navegador...
start streamlit run dashboard_streamlit_postgres.py

echo Tudo rodando! Feche esta janela se quiser.
pause