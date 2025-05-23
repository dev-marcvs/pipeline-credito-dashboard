# Pipeline de Análise de Créditos

Este projeto foi desenvolvido como parte de um desafio técnico para uma vaga na área de dados. Ele simula um pipeline completo de ingestão, armazenamento, análise e visualização de dados financeiros utilizando ferramentas modernas do ecossistema Python.

## Funcionalidades

- Leitura de arquivos .csv com dados simulados
- Armazenamento relacional em PostgreSQL com estrutura normalizada
- Simulação de cargas incrementais usando coluna de controle
- Cálculo de indicadores financeiros por fundo
- Visualização interativa com Streamlit (dashboard)

## Tecnologias utilizadas

- Python 3.11
- pandas
- sqlalchemy + psycopg2-binary
- PostgreSQL (via Docker)
- Streamlit
- VSCode com ambiente virtual (venv)

## Estrutura do projeto

```
teste_tecnico/
├── data/
│   ├── aquisicao_dia_database_fundo_teste.csv
│   ├── estoque_aquisicoes_database_fundo_teste.csv
│   └── liquidados_estoque_database_fundo_teste.csv
├── dashboard_streamlit_postgres.py
├── carga_incremental_postgres.py
├── start_pipeline_dashboard.bat
├── abrir_dashboard.bat
└── venv/
```

## Como executar o projeto

1. Instale as dependências (caso ainda não tenha feito):

```bash
pip install pandas streamlit sqlalchemy psycopg2-binary
```

2. Suba o banco PostgreSQL com Docker:

```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```

3. Execute o pipeline completo (inclui carga e dashboard):

```bash
start_pipeline_dashboard.bat
```

Ou, para abrir apenas o dashboard:

```bash
abrir_dashboard.bat
```

## Sobre o dashboard

A aplicação construída com Streamlit permite selecionar fundos e visualizar:

- Volume cedido
- Estoque atual
- Valor recebido
- Tempo médio até baixa
- Retorno financeiro
- Percentual de inadimplência
- Distribuição dos recebíveis por faixa de atraso (aging)

## Observações finais

- Os dados utilizados são simulados e foram fornecidos exclusivamente para fins de avaliação.
- O projeto foi estruturado para refletir boas práticas de engenharia de dados e visualização analítica.

## Autor

Marcus V. G. Ferreira