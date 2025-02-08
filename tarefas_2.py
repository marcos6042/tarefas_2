import streamlit as st
import sqlite3

# Configurações iniciais
st.set_page_config(page_title="Gestão de Tarefas", layout="wide")

# Conexão com o banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabelas no banco de dados
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT NOT NULL,
            cnpj TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS filiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            cnpj TEXT NOT NULL UNIQUE,
            municipio TEXT NOT NULL,
            uf TEXT NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_categoria TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subcategorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER,
            nome_subcategoria TEXT NOT NULL,
            periodicidade TEXT NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_usuario TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_tarefa TEXT NOT NULL,
            data_vencimento TEXT NOT NULL,
            filial_id INTEGER,
            subcategoria_id INTEGER,
            status TEXT DEFAULT 'pendente',
            FOREIGN KEY (filial_id) REFERENCES filiais (id),
            FOREIGN KEY (subcategoria_id) REFERENCES subcategorias (id)
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar o banco de dados
init_db()

# Função para exibir mensagens de sucesso/erro
def show_message(message, success=True):
    if success:
        st.success(message)
    else:
        st.error(message)

# Página principal
def main_page():
    st.title("Gestão de Tarefas")
    menu = ["Cadastro de Empresas", "Cadastro de Filiais", "Cadastro de Categorias",
            "Cadastro de Subcategorias", "Cadastro de Usuários", "Nova Tarefa", "Baixa de Tarefas"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Cadastro de Empresas":
        cadastro_empresas()
    elif choice == "Cadastro de Filiais":
        cadastro_filiais()
    elif choice == "Cadastro de Categorias":
        cadastro_categorias()
    elif choice == "Cadastro de Subcategorias":
        cadastro_subcategorias()
    elif choice == "Cadastro de Usuários":
        cadastro_usuarios()
    elif choice == "Nova Tarefa":
        nova_tarefa()
    elif choice == "Baixa de Tarefas":
        baixa_tarefas()

# Cadastro de Empresas
def cadastro_empresas():
    st.header("Cadastro de Empresas")
    with st.form("form_empresa"):
        razao_social = st.text_input("Razão Social")
        cnpj = st.text_input("CNPJ")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO empresas (razao_social, cnpj) VALUES (?, ?)', (razao_social, cnpj))
                conn.commit()
                show_message("Empresa cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                show_message("Erro: CNPJ já cadastrado.", success=False)
            finally:
                conn.close()

    # Listar empresas cadastradas
    conn = get_db_connection()
    empresas = conn.execute('SELECT * FROM empresas').fetchall()
    conn.close()
    if empresas:
        st.subheader("Empresas Cadastradas")
        for empresa in empresas:
            st.write(f"{empresa['razao_social']} - {empresa['cnpj']}")

# Cadastro de Filiais
def cadastro_filiais():
    st.header("Cadastro de Filiais")
    conn = get_db_connection()
    empresas = conn.execute('SELECT * FROM empresas').fetchall()
    conn.close()

    with st.form("form_filial"):
        empresa_id = st.selectbox("Empresa", [f"{e['razao_social']} ({e['cnpj']})" for e in empresas])
        cnpj = st.text_input("CNPJ da Filial")
        municipio = st.text_input("Município")
        uf = st.text_input("UF")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            empresa_id = [e['id'] for e in empresas if f"{e['razao_social']} ({e['cnpj']})" == empresa_id][0]
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO filiais (empresa_id, cnpj, municipio, uf) VALUES (?, ?, ?, ?)',
                             (empresa_id, cnpj, municipio, uf))
                conn.commit()
                show_message("Filial cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                show_message("Erro: CNPJ já cadastrado.", success=False)
            finally:
                conn.close()

# Cadastro de Categorias
def cadastro_categorias():
    st.header("Cadastro de Categorias")
    with st.form("form_categoria"):
        nome_categoria = st.text_input("Nome da Categoria")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO categorias (nome_categoria) VALUES (?)', (nome_categoria,))
                conn.commit()
                show_message("Categoria cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                show_message("Erro: Categoria já cadastrada.", success=False)
            finally:
                conn.close()

# Cadastro de Subcategorias
def cadastro_subcategorias():
    st.header("Cadastro de Subcategorias")
    conn = get_db_connection()
    categorias = conn.execute('SELECT * FROM categorias').fetchall()
    conn.close()

    with st.form("form_subcategoria"):
        categoria_id = st.selectbox("Categoria", [c['nome_categoria'] for c in categorias])
        nome_subcategoria = st.text_input("Nome da Subcategoria")
        periodicidade = st.selectbox("Periodicidade", ["mensal", "trimestral", "anual", "avulso"])
        submit = st.form_submit_button("Cadastrar")
        if submit:
            categoria_id = [c['id'] for c in categorias if c['nome_categoria'] == categoria_id][0]
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO subcategorias (categoria_id, nome_subcategoria, periodicidade) VALUES (?, ?, ?)',
                             (categoria_id, nome_subcategoria, periodicidade))
                conn.commit()
                show_message("Subcategoria cadastrada com sucesso!")
            except sqlite3.IntegrityError:
                show_message("Erro: Subcategoria já cadastrada.", success=False)
            finally:
                conn.close()

# Cadastro de Usuários
def cadastro_usuarios():
    st.header("Cadastro de Usuários")
    with st.form("form_usuario"):
        nome_usuario = st.text_input("Nome do Usuário")
        email = st.text_input("E-mail")
        submit = st.form_submit_button("Cadastrar")
        if submit:
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO usuarios (nome_usuario, email) VALUES (?, ?)', (nome_usuario, email))
                conn.commit()
                show_message("Usuário cadastrado com sucesso!")
            except sqlite3.IntegrityError:
                show_message("Erro: E-mail já cadastrado.", success=False)
            finally:
                conn.close()

# Nova Tarefa
def nova_tarefa():
    st.header("Nova Tarefa")
    conn = get_db_connection()
    filiais = conn.execute('SELECT * FROM filiais').fetchall()
    subcategorias = conn.execute('SELECT * FROM subcategorias').fetchall()
    conn.close()

    with st.form("form_tarefa"):
        nome_tarefa = st.text_input("Nome da Tarefa")
        data_vencimento = st.date_input("Data de Vencimento")
        filial_id = st.selectbox("Filial", [f"{f['cnpj']} - {f['municipio']}/{f['uf']}" for f in filiais])
        subcategoria_id = st.selectbox("Subcategoria", [s['nome_subcategoria'] for s in subcategorias])
        submit = st.form_submit_button("Cadastrar")
        if submit:
            filial_id = [f['id'] for f in filiais if f"{f['cnpj']} - {f['municipio']}/{f['uf']}" == filial_id][0]
            subcategoria_id = [s['id'] for s in subcategorias if s['nome_subcategoria'] == subcategoria_id][0]
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO tarefas (nome_tarefa, data_vencimento, filial_id, subcategoria_id) VALUES (?, ?, ?, ?)',
                             (nome_tarefa, data_vencimento, filial_id, subcategoria_id))
                conn.commit()
                show_message("Tarefa cadastrada com sucesso!")
            except Exception as e:
                show_message(f"Erro ao cadastrar tarefa: {str(e)}", success=False)
            finally:
                conn.close()

# Baixa de Tarefas
def baixa_tarefas():
    st.header("Baixa de Tarefas")
    conn = get_db_connection()
    tarefas = conn.execute('''
        SELECT t.id, t.nome_tarefa, t.data_vencimento, f.cnpj AS filial_cnpj, s.nome_subcategoria, t.status
        FROM tarefas t
        LEFT JOIN filiais f ON t.filial_id = f.id
        LEFT JOIN subcategorias s ON t.subcategoria_id = s.id
    ''').fetchall()
    conn.close()

    pendentes = [t for t in tarefas if t['status'] == 'pendente']
    if pendentes:
        st.subheader("Tarefas Pendentes")
        tarefa_selecionada = st.selectbox("Selecione uma tarefa para registrar baixa",
                                          [f"{t['nome_tarefa']} - {t['data_vencimento']} ({t['filial_cnpj']}, {t['nome_subcategoria']})"
                                           for t in pendentes])
        if st.button("Registrar Baixa"):
            tarefa_id = [t['id'] for t in pendentes if f"{t['nome_tarefa']} - {t['data_vencimento']} ({t['filial_cnpj']}, {t['nome_subcategoria']})" == tarefa_selecionada][0]
            conn = get_db_connection()
            try:
                conn.execute('UPDATE tarefas SET status = "concluida" WHERE id = ?', (tarefa_id,))
                conn.commit()
                show_message("Baixa registrada com sucesso!")
            except Exception as e:
                show_message(f"Erro ao registrar baixa: {str(e)}", success=False)
            finally:
                conn.close()
    else:
        st.info("Não há tarefas pendentes.")

# Executar o aplicativo
if __name__ == "__main__":
    main_page()
