import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Carregar a logo
logo_path = "logo.png"
logo = Image.open(logo_path)

# Configuração Inicial do Streamlit
st.set_page_config(page_title="Gestão de Tarefas", layout="wide")
st.image(logo, width=300)
st.title("Sistema de Gestão de Tarefas")

# Banco de dados Simulado
if "tasks" not in st.session_state:
    st.session_state["tasks"] = pd.DataFrame(columns=["ID", "Tarefa", "Subtarefa", "Nível", "Responsável", "Competência", "Status", "Data de Criação", "Data de Conclusão"])

# Função para adicionar tarefa
def add_task(task, subtarefa, nivel, responsavel, competencia, status, data_conclusao):
    new_task = pd.DataFrame({
        "ID": [len(st.session_state["tasks"]) + 1],
        "Tarefa": [task],
        "Subtarefa": [subtarefa],
        "Nível": [nivel],
        "Responsável": [responsavel],
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
    responsavel = st.text_input("Responsável")
    competencia = st.date_input("Competência (Mês/Ano)")
    status = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluída"])
    data_conclusao = st.date_input("Data de Conclusão")
    if st.button("Adicionar"):
        add_task(task, subtarefa, nivel, responsavel, competencia, status, data_conclusao)
        st.success("Tarefa adicionada com sucesso!")

# Visualizações
st.subheader("Visualização das Tarefas")
tab1, tab2, tab3, tab4 = st.tabs(["Kanban", "Calendário", "Planilha", "Linha do Tempo"])

# Kanban
with tab1:
    st.write("### Visualização Kanban")
    for status in ["Pendente", "Em Andamento", "Concluída"]:
        st.write(f"#### {status}")
        tasks_status = st.session_state["tasks"][st.session_state["tasks"]["Status"] == status]
        st.dataframe(tasks_status)

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

# Alertas por Email
def send_email(to_email, subject, message):
    sender_email = "seuemail@gmail.com"
    sender_password = "suasenha"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        st.success("Alerta enviado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")

st.sidebar.subheader("Enviar Alerta por Email")
to_email = st.sidebar.text_input("Email do destinatário")
subject = st.sidebar.text_input("Assunto")
message = st.sidebar.text_area("Mensagem")
if st.sidebar.button("Enviar Email"):
    send_email(to_email, subject, message)
