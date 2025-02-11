import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_sortables import sort_items

# Carregar a logo
logo_path = "logo.png"
logo = Image.open(logo_path)

# Configuração Inicial do Streamlit
st.set_page_config(page_title="Gestão de Tarefas", layout="wide")
st.image(logo, width=300)
st.title("Sistema de Gestão de Tarefas")

# Banco de dados Simulado
if "tasks" not in st.session_state:
    st.session_state["tasks"] = pd.DataFrame(columns=["ID", "Tarefa", "Subtarefa", "Nível", "Responsáveis", "Competência", "Status", "Data de Criação", "Data de Conclusão"])

if "users" not in st.session_state:
    st.session_state["users"] = ["User1", "User2", "User3"]

# Função para adicionar tarefa
def add_task(task, subtarefa, nivel, responsaveis, competencia, status, data_conclusao):
    new_task = pd.DataFrame({
        "ID": [len(st.session_state["tasks"]) + 1],
        "Tarefa": [task],
        "Subtarefa": [subtarefa],
        "Nível": [nivel],
        "Responsáveis": [", ".join(responsaveis)],
        "Competência": [competencia.strftime("%Y-%m")],
        "Status": [status],
        "Data de Criação": [datetime.datetime.now().strftime("%Y-%m-%d")],
        "Data de Conclusão": [data_conclusao.strftime("%Y-%m-%d")]
    })
    st.session_state["tasks"] = pd.concat([st.session_state["tasks"], new_task], ignore_index=True)

# Interface para adicionar tarefa
with st.sidebar:
    st.header("Adicionar Nova Tarefa")
    task = st.text_input("Tarefa")
    subtarefa = st.text_input("Subtarefa (Opcional)")
    nivel = st.selectbox("Nível da Subtarefa", ["Principal", "Nível 1", "Nível 2"])
    responsaveis = st.multiselect("Responsáveis", st.session_state["users"])
    competencia = st.date_input("Competência (Mês/Ano)")
    status = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluída"])
    data_conclusao = st.date_input("Data de Conclusão")
    if st.button("Adicionar"):
        add_task(task, subtarefa, nivel, responsaveis, competencia, status, data_conclusao)
        st.success("Tarefa adicionada com sucesso!")

# Visualizações
st.subheader("Visualização das Tarefas")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Kanban", "Calendário", "Planilha", "Linha do Tempo", "Dashboards"])

# Kanban
with tab1:
    st.write("### Visualização Kanban")
    statuses = ["Pendente", "Em Andamento", "Concluída"]
    kanban_columns = {status: list(st.session_state["tasks"][st.session_state["tasks"]["Status"] == status]["Tarefa"]) for status in statuses}
    updated_columns = sort_items(kanban_columns, multi_containers=True)
    for i, status in enumerate(statuses):
        st.session_state["tasks"].loc[st.session_state["tasks"]["Tarefa"].isin(updated_columns[i]), "Status"] = status
    for col, tasks in updated_columns.items():
        st.write(f"### {statuses[col]}")
        for task in tasks:
            st.write(f"- {task}")

# Calendário
with tab2:
    st.write("### Visualização em Calendário")
    st.dataframe(st.session_state["tasks"][["Tarefa", "Competência", "Data de Conclusão"]])

# Planilha
with tab3:
    st.write("### Visualização em Planilha")
    st.dataframe(st.session_state["tasks"])

# Linha do Tempo
with tab4:
    st.write("### Linha do Tempo")
    st.dataframe(st.session_state["tasks"][["Tarefa", "Data de Criação", "Data de Conclusão"]])

# Dashboards
with tab5:
    st.write("### Dashboards de Tarefas")
    st.bar_chart(st.session_state["tasks"]["Status"].value_counts())
