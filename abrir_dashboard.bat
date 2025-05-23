@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Abrindo o dashboard no navegador...
start streamlit run dashboard_streamlit_postgres.py

echo Dashboard carregando! Feche esta janela se quiser.
pause