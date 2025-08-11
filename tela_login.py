import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def define_estado():
    return {
        'pagina_atual': 'Página Inicial'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def ler_planilha(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
    creds = None
    values2 = pd.DataFrame()  # Inicializando a variável

    if os.path.exists("token_gami.json"):
        creds = Credentials.from_authorized_user_file("token_gami.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials_gami.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)

        with open("token_gami.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )

        values = result.get("values", [])
    
        values2 = pd.DataFrame(values[1:], columns=values[0])

    except HttpError as err:
        st.error(f"Erro ao ler a planilha: {err}")

    return values2

def ChangeButtonColour(widget_label, font_color, background_color='transparent'):
        htmlstr = f"""
            <script>
                var elements = window.parent.document.querySelectorAll('button');
                for (var i = 0; i < elements.length; ++i) {{ 
                    if (elements[i].innerText == '{widget_label}') {{ 
                        elements[i].style.color ='{font_color}';
                        elements[i].style.background = '{background_color}';
                        elements[i].style.width = '120px';  // Adiciona a largura desejada
                        elements[i].style.height = '50px';  // Adiciona a altura desejada
                    }}
                }}
            </script>
            """
        components.html(f"{htmlstr}", height=0, width=0)




def mostrar_formulario_login():

    html_br="""
        <br>
        """

    with st.container():
            col1, col2, col3 = st.columns([3,4,3])
            with col1:
                st.markdown(html_br, unsafe_allow_html=True)
            with col2:
                st.image("./logo_jazz.png")
            with col3:
                st.markdown(html_br, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    email = col2.text_input("Email", key="emaill", value="")

    senha = col2.text_input("Senha", type="password", key="senha", value="")

    html_br="""
        <br>
        """

    st.markdown(html_br, unsafe_allow_html=True)

    col4, col5, col6 = st.columns([9, 1, 10])
    #st.write('Entrei01')
    entrar_button = col5.button('Entrar', key='b20')
    ChangeButtonColour('Entrar', 'white', '#9E089E')

    tabela_usuarios = ler_planilha("1ddv-J2gk6r3rH_djTunhedsMpMuP3_hPLB6GbYvvRic", "Streamlit | Usuarios!A1:G1000")
    lista_emails = tabela_usuarios["Email"].tolist()
    #st.write(lista_emails)

    if entrar_button:
        #st.write('Entrei')
        email = email.lower()  

        if email in lista_emails:
            #st.write('Entrei02')

            indice_email = lista_emails.index(email)  
            senha_correspondente = tabela_usuarios.loc[indice_email, "Senha"]


            if senha == senha_correspondente:
                #st.write('Entrei 03')
                st.session_state.logged_in = True
                st.success("Login bem-sucedido! Você pode acessar seu conteúdo aqui.")
                #st.write('Entrei2')

                if tabela_usuarios.loc[indice_email, "Permissão"] != 'Responsável':
                    #st.write('Entrei3')
                    return True, tabela_usuarios.loc[indice_email, "Permissão"], tabela_usuarios.loc[indice_email, "Nome"], tabela_usuarios.loc[indice_email, "Email"], tabela_usuarios.loc[indice_email, "Turma"]
                else:
                    return True, tabela_usuarios.loc[indice_email, "Permissão"], tabela_usuarios.loc[indice_email, "Aluno (responsável)"], tabela_usuarios.loc[indice_email, "Email"], tabela_usuarios.loc[indice_email, "Turma"]
            else:
                st.error("Senha incorreta. Tente novamente.")
                return False, "Sem Permissão", "Sem Nome", "Sem Email", "Sem Turma"
        else:
            st.error("Email não encontrado. Verifique o email fornecido.")
            return False, "Sem Permissão", "Sem Nome",  "Sem Email", "Sem Turma"

    return False, "Sem Permissão", "Sem Nome",  "Sem Email", "Sem Turma"
        
def mostrar_tela_login():

    estado = get_estado()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "tipo_usuario" not in st.session_state:
        st.session_state.tipo_usuario = "Sem Permissão"

    if "nome_usuario" not in st.session_state:
        st.session_state.nome_usuario = "Sem Nome"

    if "Email" not in st.session_state:
        st.session_state.email = "Sem Email"

    if "Turma" not in st.session_state:
        st.session_state.turma = "Sem Turma"

    if st.session_state.logged_in:
        tipo_usuario = st.session_state.get("tipo_usuario", None)
        nome_usuario = st.session_state.get("nome_usuario", None)
        Email = st.session_state.get("Email", None)
        Turma = st.session_state.get("Turma", None)
        return True, tipo_usuario, nome_usuario, Email, Turma

    if not st.session_state.logged_in:
        #st.write('Entrei0')
        login_ok, tipo_usuario, nome_usuario, Email, Turma = mostrar_formulario_login()
        #st.write(login_ok, tipo_usuario, nome_usuario, Email, Turma)
        #st.write('Entrei04')
        if login_ok:
            st.session_state.tipo_usuario = tipo_usuario
            st.session_state.nome_usuario = nome_usuario
            st.session_state.Email = Email
            st.session_state.Turma = Turma
            i = 0
            if i == 0:
                #st.experimental_rerun()
                #st.request_rerun()
                st.rerun()

                i = i + 1
            return True, st.session_state.tipo_usuario, st.session_state.nome_usuario, st.session_state.Email, st.session_state.Turma
        
        return False, "Sem Permissão", "Sem Nome", "Sem Email", "Sem Turma"

    else:
        return True, st.session_state.tipo_usuario, st.session_state.nome_usuario, st.session_state.Email, st.session_state.Turma



        
