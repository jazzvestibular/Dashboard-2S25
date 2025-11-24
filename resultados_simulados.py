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
from plotly.subplots import make_subplots
from PIL import Image
import numpy as np
from tqdm import tqdm
import datetime
from logs import escrever_planilha
import pytz

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

def define_estado():
    return {
        'pagina_atual': 'Alunos - Resultados nos simulados'
    }

def get_estado():
    if 'estado' not in st.session_state:
        st.session_state.estado = define_estado()
    return st.session_state.estado

def dia_hora():

    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    data_e_hora_brasilia = datetime.datetime.now(fuso_horario_brasilia)
    data_hoje_brasilia = str(data_e_hora_brasilia.date())
    hora_atual_brasilia = str(data_e_hora_brasilia.strftime('%H:%M:%S'))
    return data_hoje_brasilia, hora_atual_brasilia

def ler_planilha(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME):
    creds = None

    # Carregar as credenciais do arquivo token.json
    if os.path.exists('token_gami.json'):
        creds = Credentials.from_authorized_user_file('token_gami.json', SCOPES)

    # Verificar se as credenciais estão válidas e atualizar se necessário
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_gami.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        
        # Salvar as credenciais atualizadas de volta no arquivo token.json
        with open('token_gami.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

        values = result.get('values', [])

        if values:
            values2 = pd.DataFrame(values[1:], columns=values[0])
        else:
            values2 = pd.DataFrame()  # Caso não haja dados na planilha

    except HttpError as err:
        print(f'An error occurred: {err}')
        values2 = pd.DataFrame()  # Inicializa como DataFrame vazio em caso de erro

    return values2

def extract_login(login):
    if login.startswith("jazzvestibular_"):
        return login[len("jazzvestibular_"):]
    else:
        return login
    
def truncar(num, digits):
    sp = str(num).split('.')
    
    if len(sp) > 1:
        parte_decimal = sp[1][:digits]
    else:
        parte_decimal = '0' * digits

    return float(f"{sp[0]}.{parte_decimal}")

def tabela_debate(df):

    with st.container():
            col2, col3 = st.columns([20,2])

            with col2:

                st.markdown("""
                            <style>
                                th, td {
                                    border-top: none;
                                    padding: 0px;  /* Adjust padding for better visual appearance */
                                    text-align: center;  /* Center align text */
                                    height: 60px; 
                                    vertical-align: middle;
                                }
                            </style>
                            <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                                <thead>
                                    <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                        <th style="width: 480px; min-width: 480px; max-width: 480px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Tema</th>
                                        <th style="width: 260px; min-width: 260px; max-width: 260px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Pensamento Crítico</th>
                                        <th style="width: 260px; min-width: 260px; max-width: 260px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Comunicação Assertiva</th>
                                        <th style="width: 260px; min-width: 260px; max-width: 260px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Interação com Pessoas</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """, unsafe_allow_html=True)
                
                st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)
                
                st.markdown("""
                            <style>
                                th, td {
                                    border-top: none;
                                    padding: 0px;  /* Adjust padding for better visual appearance */
                                    text-align: center;  /* Center align text */
                                    height: 60px; 
                                    vertical-align: middle;
                                }
                            </style>
                            <table style="border-collapse: collapse; margin-top: 0px; margin-bottom: -32px;">
                                <thead>
                                    <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                        <th style="width: 480px; min-width: 480px; max-width: 480px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);"></th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seu resultado</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Média geral</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seu resultado</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Média geral</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seu resultado</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Média geral</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """, unsafe_allow_html=True)
                
                st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

                for _, row in df.iterrows():

                    if (row['Nota_Aluno_Pensamento Crítico'] + row['Nota_Aluno_Comunicação Assertiva'] + row['Nota_Aluno_Interação com Pessoas']) > (row['Nota_Média_Geral_Pensamento Crítico'] + row['Nota_Média_Geral_Comunicação Assertiva'] + row['Nota_Média_Geral_Interação com Pessoas']):
                        background_color = 'rgba(144, 238, 144, 0.5)'  # Verde claro
                    elif (row['Nota_Aluno_Pensamento Crítico'] + row['Nota_Aluno_Comunicação Assertiva'] + row['Nota_Aluno_Interação com Pessoas']) > (row['Nota_Média_Geral_Pensamento Crítico'] + row['Nota_Média_Geral_Comunicação Assertiva'] + row['Nota_Média_Geral_Interação com Pessoas'] - 3):
                        background_color = 'rgba(255, 255, 153, 0.7)'  # Amarelo claro
                    else:
                        background_color = 'rgba(255, 102, 102, 0.5)'  # Vermelho claro


                    st.markdown(f"""
                    <tr style="text-align: center; background-color: {background_color};">
                        <td style="width: 480px; min-width: 480px; max-width: 480px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Frase Tema_']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Aluno_Pensamento Crítico']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Média_Geral_Pensamento Crítico']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Aluno_Comunicação Assertiva']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Média_Geral_Comunicação Assertiva']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Aluno_Interação com Pessoas']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Média_Geral_Interação com Pessoas']}</td>
                    </tr>
                    """, unsafe_allow_html=True)

def tabela_arguicao(df):

    with st.container():
            col1, col2, col3 = st.columns([3,20,2])

            with col2:

                st.markdown("""
                            <style>
                                th, td {
                                    border-top: none;
                                    padding: 0px;  /* Adjust padding for better visual appearance */
                                    text-align: center;  /* Center align text */
                                    height: 60px; 
                                    vertical-align: middle;
                                }
                            </style>
                            <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                                <thead>
                                    <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                        <th style="width: 700px; min-width: 700px; max-width: 700px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Tema</th>
                                        <th style="width: 260px; min-width: 260px; max-width: 260px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Aprender a Aprender</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """, unsafe_allow_html=True)
                
                st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)
                
                st.markdown("""
                            <style>
                                th, td {
                                    border-top: none;
                                    padding: 0px;  /* Adjust padding for better visual appearance */
                                    text-align: center;  /* Center align text */
                                    height: 60px; 
                                    vertical-align: middle;
                                }
                            </style>
                            <table style="border-collapse: collapse; margin-top: 0px; margin-bottom: -32px;">
                                <thead>
                                    <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                        <th style="width: 700px; min-width: 700px; max-width: 700px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);"></th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seu resultado</th>
                                        <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Média geral</th>
                                    </tr>
                                </thead>
                                <tbody>
                        """, unsafe_allow_html=True)
                
                st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

                for _, row in df.iterrows():

                    if row['Nota_Aluno_Aprender a Aprender'] > row['Nota_Média_Geral_Aprender a Aprender']:
                        background_color = 'rgba(144, 238, 144, 0.5)'  # Verde claro
                    elif row['Nota_Aluno_Aprender a Aprender'] > row['Nota_Média_Geral_Aprender a Aprender'] - 1:
                        background_color = 'rgba(255, 255, 153, 0.7)'  # Amarelo claro
                    else:
                        background_color = 'rgba(255, 102, 102, 0.5)'  # Vermelho claro


                    st.markdown(f"""
                    <tr style="text-align: center; background-color: {background_color};">
                        <td style="width: 700px; min-width: 700px; max-width: 700px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Frase Tema_']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Aluno_Aprender a Aprender']}</td>
                        <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nota_Média_Geral_Aprender a Aprender']}</td>
                    </tr>
                    """, unsafe_allow_html=True)

def tabela_assuntos(df):

    st.markdown("""
                <style>
                    th, td {
                        border-top: none;
                        padding: 0px;  /* Adjust padding for better visual appearance */
                        text-align: center;  /* Center align text */
                        height: 60px; 
                        vertical-align: middle;
                    }
                </style>
                <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                    <thead>
                        <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                            <th style="width: 280px; min-width: 280px; max-width: 280px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Assunto</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Quantidade de questões</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Resultado Individual</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Resultado Geral</th>
                            <th style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Status</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    
    st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        # Definir a cor de fundo com base no status
        if row['Status'] == '🟢':
            background_color = 'rgba(144, 238, 144, 0.5)'  # Verde claro
        elif row['Status'] == '🟡':
            background_color = 'rgba(255, 255, 153, 0.7)'  # Amarelo claro
        elif row['Status'] == '🔴':
            background_color = 'rgba(255, 102, 102, 0.5)'  # Vermelho claro
        else:
            background_color = 'transparent'  # Caso não haja um status reconhecido

        st.markdown(f"""
        <tr style="text-align: center; background-color: {background_color};">
            <td style="width: 280px; min-width: 280px; max-width: 280px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Assunto']}</td>
            <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Quantidade de questões']}</td>
            <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Individual']}</td>
            <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Geral']}</td>
            <td style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Status']}</td>
        </tr>
        """, unsafe_allow_html=True)

def tabela_competencias(df):

    st.markdown("""
                <style>
                    th, td {
                        border-top: none;
                        padding: 0px;  /* Adjust padding for better visual appearance */
                        text-align: center;  /* Center align text */
                        height: 60px; 
                        vertical-align: middle;
                    }
                </style>
                <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                    <thead>
                        <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                            <th style="width: 280px; min-width: 280px; max-width: 280px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Competência</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Resultado Individual</th>
                            <th style="width: 130px; min-width: 130px; max-width: 130px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Resultado Geral</th>
                            <th style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Status</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    
    st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

    for _, row in df.iterrows():
        # Definir a cor de fundo com base no status
        if row['Status'] == '🟢':
            background_color = 'rgba(144, 238, 144, 0.5)'  # Verde claro
        elif row['Status'] == '🟡':
            background_color = 'rgba(255, 255, 153, 0.7)'  # Amarelo claro
        elif row['Status'] == '🔴':
            background_color = 'rgba(255, 102, 102, 0.5)'  # Vermelho claro
        else:
            background_color = 'transparent'  # Caso não haja um status reconhecido

        st.markdown(f"""
        <tr style="text-align: center; background-color: {background_color};">
            <td style="width: 280px; min-width: 280px; max-width: 280px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Competência']}</td>
            <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Individual']}</td>
            <td style="width: 130px; min-width: 130px; max-width: 130px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Geral']}</td>
            <td style="width: 100px; min-width: 100px; max-width: 100px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Status']}</td>
        </tr>
        """, unsafe_allow_html=True)

def tabela_pontos(df_melhor, df_pior):

    html_br="""
        <br>
        """

    if 'Competência' in df_melhor.columns:
        df_melhor['Competência'] = df_melhor['Competência'].apply(lambda x: "🟢 " + x)
        df_melhor.rename(columns = {'Competência':'Assunto'}, inplace = True)
        df_pior['Competência'] = df_pior['Competência'].apply(lambda x: "🔴 " + x)
        df_pior.rename(columns = {'Competência':'Assunto'}, inplace = True)
    else:
        df_melhor['Assunto'] = df_melhor['Assunto'].apply(lambda x: "🟢 " + x)
        df_pior['Assunto'] = df_pior['Assunto'].apply(lambda x: "🔴 " + x)

    if len(df_melhor) > 3:
        df_melhor = df_melhor.head(3)

    if len(df_pior) > 3:
        df_pior = df_pior.head(3)

    if len(df_melhor) > 0:

        st.markdown("""
                    <style>
                        th, td {
                            border-top: none;
                            padding: 0px;  /* Adjust padding for better visual appearance */
                            text-align: center;  /* Center align text */
                            height: 65px; 
                            vertical-align: middle;
                        }
                    </style>
                    <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: 0px;">
                        <thead>
                            <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                <th style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; border-top-left-radius: 10px;border-top-right-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seus melhores resultados</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True)
        
        st.markdown(html_br, unsafe_allow_html=True)
                    
        for _, row in df_melhor.iterrows():
                    st.markdown("""
                    <tr style="text-align: center; background-color: rgba(144, 238, 144, 0.5); margin-bottom: 10px; ">
                        <td style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;border-top-left-radius: 10px;border-top-right-radius: 10px;border-bottom-left-radius: 10px;border-bottom-right-radius: 10px;">{0}</td>
                    </tr>
                """.format(row['Assunto']), unsafe_allow_html=True)
                    st.markdown(html_br, unsafe_allow_html=True)
                    
        st.markdown(html_br, unsafe_allow_html=True)

    if len(df_pior) > 0: 

        st.markdown("""
                    <style>
                        th, td {
                            border-top: none;
                            padding: 0px;  /* Adjust padding for better visual appearance */
                            text-align: center;  /* Center align text */
                            height: 65px; 
                            vertical-align: middle;
                        }
                    </style>
                    <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: 0px;">
                        <thead>
                            <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                                <th style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; border-top-left-radius: 10px;border-top-right-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Pontos que você pode melhorar</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True)
        
        st.markdown(html_br, unsafe_allow_html=True)

        for _, row in df_pior.iterrows():
                    st.markdown("""
                    <tr style="text-align: center; background-color: rgba(255, 102, 102, 0.5); margin-bottom: 10px; ">
                        <td style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;border-top-left-radius: 10px;border-top-right-radius: 10px;border-bottom-left-radius: 10px;border-bottom-right-radius: 10px;">{0}</td>
                    </tr>
                """.format(row['Assunto']), unsafe_allow_html=True)
                    st.markdown(html_br, unsafe_allow_html=True)

def tabela_questoes(df):

    df['Número da questão'] = pd.to_numeric(df['Número da questão'], errors='coerce')

    df = df.sort_values(by='Número da questão', ascending = True)

    df = df.loc[df['Número da questão'] != 61]

    st.markdown("""
                <style>
                    th, td {
                        border-top: none;
                        padding: 0px;  /* Adjust padding for better visual appearance */
                        text-align: center;  /* Center align text */
                        height: 60px; 
                        vertical-align: middle;
                    }
                </style>
                <table style="border-collapse: collapse; margin-top: 10px; margin-bottom: -32px;">
                    <thead>
                        <tr style="background-color: rgba(158, 8, 158, 0.8); color: white; font-weight: bold;">
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Questão</th>
                            <th style="width: 200px; min-width: 200px; max-width: 200px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Área do conhecimento</th>
                            <th style="width: 400px; min-width: 400px; max-width: 400px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Assunto</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Gabarito</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Seu resultado</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Média geral</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    
    st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

    if len(df) < 60: 

        for _, row in df.iterrows():
            if row['Resultado Individual'] == 0:
                background_color = 'rgba(255, 102, 102, 0.5)'
            elif row['Resultado Individual'] >= row['Resultado Geral']:
                background_color = 'rgba(144, 238, 144, 0.5)'
            elif row['Resultado Individual'] - row['Resultado Geral'] > - 0.25:
                background_color = 'rgba(255, 255, 153, 0.7)'
            else:
                background_color = 'rgba(255, 102, 102, 0.5)'

            row['Resultado Individual'] = str((row['Resultado Individual'] * 100)) + '%'
            #row['Resultado Geral'] = str((row['Resultado Geral'] * 100)) + '%'
            #row['Resultado Geral'] = str(round(row['Resultado Geral'] * 100, 0)) + '%'
            row['Resultado Geral'] = str(int(row['Resultado Geral'] * 100)) + '%'


            st.markdown(f"""
            <tr style="text-align: center; background-color: {background_color};">
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Número da questão']}</td>
                <td style="width: 200px; min-width: 200px; max-width: 200px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Área do conhecimento']}</td>
                <td style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Assunto']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Gabarito']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Individual']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Geral']}</td>
            </tr>
            """, unsafe_allow_html=True)
    else:

        df['Resultado Individual'] = (df['Resultado Individual'] * 100).round(0).astype(int).astype(str) + '%'
        #df['Resultado Geral'] = (df['Resultado Geral'] * 100).round(0).astype(int).astype(str) + '%'
        df['Resultado Geral'] = (df['Resultado Geral'] * 100).round(0).astype(int).astype(str) + '%'
        #df['Resultado Geral'] = df['Resultado Geral'].apply(lambda x: f"{x * 100:.0f}%")

        for _, row in df.iterrows():
            # Definir a cor de fundo com base no status
            if row['Resultado Individual'] == '100%':
                background_color = 'rgba(144, 238, 144, 0.5)'  # Verde claro
            elif row['Resultado Individual'] == '0%':
                background_color = 'rgba(255, 102, 102, 0.5)'  # Vermelho claro
            else:
                background_color = 'transparent'  # Caso não haja um status reconhecido

            st.markdown(f"""
            <tr style="text-align: center; background-color: {background_color};">
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Número da questão']}</td>
                <td style="width: 200px; min-width: 200px; max-width: 200px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Área do conhecimento']}</td>
                <td style="width: 400px; min-width: 400px; max-width: 400px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Assunto']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Gabarito']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Individual']}</td>
                <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Resultado Geral']}</td>
            </tr>
            """, unsafe_allow_html=True)

def cards_principais_2fase(nota_aluno, nota_media, classificacao_aluno, total_alunos):

    with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1,20,1,20,1,20,1])
            with col1:
                st.write("")
            with col2:

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    """
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                        <strong>Nota</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                if nota_aluno < 5:
                    nota_aluno = 250*nota_aluno

                st.markdown(
                        f"""
                        <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                            <strong>{nota_aluno} / 1000</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                if nota_media < 5:
                    nota_media = 250*nota_media

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {nota_media}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    """
                    <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.write("")
            with col4:
                st.write("")
            with col5:
                st.write("")
            with col6:

                if nota_aluno != 0:

                        st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                        """,
                        unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                                <strong>Classificação</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{classificacao_aluno}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            f"""
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                                <strong>Total: {total_alunos}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            """
                            <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                            """,
                            unsafe_allow_html=True
                        )

            with col7:
                st.write("")

def cards_principais(nota_aluno, nota_media, acerto_aluno, acerto_media, vestibular, classificacao_aluno, total_alunos, simulado):

    with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1,20,1,20,1,20,1])
            with col1:
                st.write("")
            with col2:

                if vestibular != 'Simulado Nacional Insper 1ª fase Total':
                    st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                            <strong>Nota</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                    
                    st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{nota_aluno} / 100</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                            <strong>Média: {nota_media}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                        """,
                        unsafe_allow_html=True
                    )

            with col3:
                st.write("")
            with col4:

                if acerto_media != 0:
                    st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                            <strong>Acertos</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                    if (vestibular == 'Semana 01'):

                        st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 36</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                    if (vestibular == 'Esparta 3º' or vestibular == 'Esparta 2º'):
                        
                        if (simulado == '1 Geral' or simulado == 0):

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 30</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        
                        if (simulado == '2 Geral' or simulado == '3 Geral' or simulado == '4 Geral' or simulado == '5 Geral' or simulado == '6 Geral' or simulado == '7 Geral'):

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 40</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if simulado == '1 Matemática':

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 20</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if (simulado == '2 Matemática' or simulado == '3 Matemática' or simulado == '4 Matemática' or simulado == '5 Matemática' or simulado == '6 Matemática' or simulado == '7 Matemática'):

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 25</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if simulado == '1 Linguagens' or simulado == '2 Linguagens' or simulado == '1 Humanas' or simulado == '3 Linguagens' or simulado == '4 Linguagens' or simulado == '5 Linguagens' or simulado == '6 Linguagens' or simulado == '7 Linguagens':

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 5</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if simulado == '2 Humanas' or simulado == '3 Humanas' or simulado == '4 Humanas' or simulado == '5 Humanas' or simulado == '6 Humanas' or simulado == '7 Humanas':

                            st.markdown(
                                f"""
                                <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                    <strong>{acerto_aluno} / 10</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    if vestibular == 'Semana 01 Matemática':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 30</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'Semana 01 Linguagens':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 6</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'Insper' or vestibular == 'Simulado Nacional Insper 1ª fase':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 15</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'Insper Total' or vestibular == 'Simulado Nacional Insper 1ª fase Total':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 60</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV' or vestibular == 'Simulado Nacional FGV 1ª fase':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 15</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV Total' or vestibular == 'Simulado Nacional FGV 1ª fase Total':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 60</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV Disc Matemática':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 8</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV Disc Língua Portuguesa':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 8</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV Disc Ciências Humanas':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 8</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    if vestibular == 'FGV Disc Artes e QC':

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{acerto_aluno} / 5</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                            <strong>Média: {acerto_media}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                        """,
                        unsafe_allow_html=True
                    )

            with col5:
                st.write("")
            with col6:

                if nota_aluno != 0:

                    if vestibular == 'Simulado Nacional Insper 1ª fase' or vestibular == 'Simulado Nacional Insper 1ª fase Total' or vestibular == 'Simulado Nacional FGV 1ª fase Total' or vestibular == 'Simulado Nacional FGV 1ª fase':

                        st.markdown(
                        """
                        <hr style="border: 0px solid #9E089E; margin-bottom: -15px; margin-top: -15px">
                        """,
                        unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                                <strong>Classificação</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{classificacao_aluno}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                            f"""
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                                <strong>Total: {total_alunos}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            """
                            <hr style="border: 0px solid #9E089E; margin-top: -1px; ">
                            """,
                            unsafe_allow_html=True
                        )

                    else:
                        st.write("")
            with col7:
                st.write("")

def criar_histograma_2fase(resultados, nome_aluno):

    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                            <strong>Distribuição de notas</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    nome_do_aluno = nome_aluno['Nome do aluno(a)'].iloc[0]

    nota_aluno = resultados[resultados['Nome'] == nome_do_aluno]['Nota'].iloc[0]

    if int(nota_aluno) < 250:

        nota_aluno = int(250*nota_aluno)

        resultados['Nota'] = 250*resultados['Nota']

    media_nota = int(resultados['Nota'].mean())
    media_nota_jazz = int(resultados[resultados['Estratégia'] == '0. Aluno Jazz']['Nota'].mean())
    media_nota_fora_jazz = int(resultados[resultados['Estratégia'] != '0. Aluno Jazz']['Nota'].mean())

    fig = go.Figure()

    fig.add_trace(go.Histogram(
            x=resultados['Nota'],
            name='Nota',
            nbinsx=20,  # Número de bins no histograma, ajuste conforme necessário
            marker_color='rgba(158, 8, 158, 0.8)',  # Cor das barras do histograma
            opacity=0.75
        ))

        # 4. Adicionar a linha vertical para o acerto do aluno
    fig.add_vline(
            x=nota_aluno,
            line=dict(color='blue', width=3, dash='dash'),
            annotation_text=f'{nome_do_aluno}: {nota_aluno}',  # Texto na linha
            annotation_position="top right",
            annotation=dict(font_size=12, yshift=-10)  # Move a anotação um pouco para cima
        )

        # 5. Adicionar a linha vertical para a média
    fig.add_vline(
            x=media_nota,
            line=dict(color='red', width=3, dash='dash'),
            annotation_text=f'Med. {media_nota:.0f}',  # Texto na linha
            annotation_position="top left",
            annotation=dict(font_size=12, yshift=0)  # Move a anotação um pouco para cima
        )

    fig.add_vline(
            x=media_nota_jazz,
            line=dict(color='green', width=3, dash='dash'),
            annotation_text=f'Med. Jazz: {media_nota_jazz:.0f}',  # Texto na linha
            annotation_position="top",  # Posição da anotação
            annotation=dict(font_size=12, yshift=10)  # Move a anotação um pouco para cima
        )

    fig.add_vline(
            x=media_nota_fora_jazz,
            line=dict(color='gray', width=3, dash='dash'),
            annotation_text=f'Med. sem Jazz: {media_nota_fora_jazz:.0f}',  # Texto na linha
            annotation_position="top",  # Posição da anotação
            annotation=dict(font_size=12, yshift=20)  # Move a anotação um pouco para cima
        )

        # 6. Configurações do layout
    fig.update_layout(
            xaxis_title_text='Nota',
            yaxis_title_text='Número de alunos',
            bargap=0.2,  # Espaço entre as barras
            bargroupgap=0.1,  # Espaço entre os grupos de barras
            xaxis_range=[0, 1050]  # Definindo o limite máximo no eixo X
        )

    st.plotly_chart(fig, use_container_width=True)

def criar_histograma_acertos(resultados, nome_aluno, limite_max):

    #st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    
    # 1. Filtrar a linha do aluno
    nome_do_aluno = nome_aluno['Nome do aluno(a)'].iloc[0]
    if 'Fez questão' in resultados.columns:
        resultados = resultados[resultados['Fez questão'] > 0]
    else:
        resultados = resultados[resultados['Nota na questão'] > 0]



    if limite_max < 100:

        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                                <strong>Distribuição de acertos</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        acerto_aluno = resultados[resultados['Nome do aluno(a)'] == nome_do_aluno]['Acerto'].iloc[0]

        # 2. Calcular a média dos acertos

        resultados_filtrados = resultados#[resultados['Fez questão'] > limite_max*40/60]

            # Calculando as médias
        media_acertos = resultados_filtrados['Acerto'].mean()
        media_acertos_jazz = resultados_filtrados[resultados_filtrados['Estratégia'] == '0. Aluno Jazz']['Acerto'].mean()
        media_acertos_fora_jazz = resultados_filtrados[resultados_filtrados['Estratégia'] != '0. Aluno Jazz']['Acerto'].mean()

        # 3. Criar o histograma com a coluna 'Acerto'
        start = 0
        if limite_max == 15:
            end = float(limite_max)+1  # por exemplo 100 ou o máximo desejado
        else:
            end = float(limite_max)+4
        n_bins = 16
        
        bin_size = (end - start) / n_bins

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=resultados['Acerto'],
            name='Acertos',
            #nbinsx=15,  # Número de bins no histograma, ajuste conforme necessário
            xbins=dict(
                start=start,
                end=end,
                size=bin_size
            ),
            marker_color='rgba(158, 8, 158, 0.8)',  # Cor das barras do histograma
            opacity=0.75
        ))

        # 4. Adicionar a linha vertical para o acerto do aluno
        fig.add_vline(
            x=acerto_aluno,
            line=dict(color='blue', width=3, dash='dash'),
            annotation_text=f'Acerto {nome_do_aluno}: {acerto_aluno}',  # Texto na linha
            annotation_position="top",
            annotation=dict(font_size=12, yshift=0)  # Move a anotação um pouco para cima
        )

        # 5. Adicionar a linha vertical para a média
        fig.add_vline(
            x=media_acertos,
            line=dict(color='red', width=3, dash='dash'),
            annotation_text=f'Média Geral: {media_acertos:.1f}',  # Texto na linha
            annotation_position="top",
            annotation=dict(font_size=12, yshift=15)  # Move a anotação um pouco para cima
        )

        #fig.add_vline(
        #    x=media_acertos_jazz,
        #    line=dict(color='green', width=3, dash='dash'),
        #    annotation_text=f'Média Jazz: {media_acertos_jazz:.1f}',  # Texto na linha
        #    annotation_position="top",  # Posição da anotação
        #    annotation=dict(font_size=12, yshift=30)  # Move a anotação um pouco para cima
        #)

        #fig.add_vline(
        #    x=media_acertos_fora_jazz,
        #    line=dict(color='orange', width=3, dash='dash'),
        #    annotation_text=f'Média Sem Jazz: {media_acertos_fora_jazz:.1f}',  # Texto na linha
        #    annotation_position="top",  # Posição da anotação
        #    annotation=dict(font_size=12, yshift=45)  # Move a anotação um pouco para cima
        #)

        # 6. Configurações do layout
        fig.update_layout(
            xaxis_title_text='Acertos',
            yaxis_title_text='Número de alunos',
            bargap=0.2,  # Espaço entre as barras
            bargroupgap=0.1,  # Espaço entre os grupos de barras
            xaxis_range=[0, limite_max + (1 if limite_max == 15 else 4)]  # Definindo o limite máximo no eixo X
        )

    else:

        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

        st.markdown(
                        """
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; ">
                            <strong>Distribuição de nota</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        acerto_aluno = resultados[resultados['Nome do aluno(a)'] == nome_do_aluno]['Nota na questão'].iloc[0]#.reset_index(drop = True).['Acerto'].iloc[0]
        resultados_filtrados = resultados.copy()

        media_acertos = resultados_filtrados['Nota na questão'].mean()
        media_acertos_jazz = resultados_filtrados[resultados_filtrados['Estratégia'] == '0. Aluno Jazz']['Nota na questão'].mean()
        media_acertos_fora_jazz = resultados_filtrados[resultados_filtrados['Estratégia'] != '0. Aluno Jazz']['Nota na questão'].mean()

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=resultados['Nota na questão'],
            name='Nota',
            nbinsx=14,  # Número de bins no histograma, ajuste conforme necessário
            marker_color='rgba(158, 8, 158, 0.8)',  # Cor das barras do histograma
            opacity=0.75
        ))

        # 4. Adicionar a linha vertical para o acerto do aluno
        fig.add_vline(
            x=acerto_aluno,
            line=dict(color='blue', width=3, dash='dash'),
            annotation_text=f'Nota {nome_do_aluno}: {acerto_aluno}',  # Texto na linha
            annotation_position="top",
            annotation=dict(font_size=12, yshift=-0)  # Move a anotação um pouco para cima
        )

        # 5. Adicionar a linha vertical para a média
        fig.add_vline(
            x=media_acertos,
            line=dict(color='red', width=3, dash='dash'),
            annotation_text=f'Média Geral: {media_acertos:.1f}',  # Texto na linha
            annotation_position="top",
            annotation=dict(font_size=12, yshift=15)  # Move a anotação um pouco para cima
        )

        #fig.add_vline(
        #    x=media_acertos_jazz,
        #    line=dict(color='green', width=3, dash='dash'),
        #    annotation_text=f'Média Jazz: {media_acertos_jazz:.1f}',  # Texto na linha
        #    annotation_position="top",  # Posição da anotação
        #    annotation=dict(font_size=12, yshift=30)  # Move a anotação um pouco para cima
        #)

        #fig.add_vline(
        #    x=media_acertos_fora_jazz,
        #    line=dict(color='orange', width=3, dash='dash'),
        #    annotation_text=f'Média Sem Jazz: {media_acertos_fora_jazz:.1f}',  # Texto na linha
        #    annotation_position="top",  # Posição da anotação
        #    annotation=dict(font_size=12, yshift=45)  # Move a anotação um pouco para cima
        #)

        # 6. Configurações do layout
        fig.update_layout(
            xaxis_title_text='Nota',
            yaxis_title_text='Número de alunos',
            bargap=0.2,  # Espaço entre as barras
            bargroupgap=0.1,  # Espaço entre os grupos de barras
            xaxis_range=[0, limite_max]  # Definindo o limite máximo no eixo X
        )

    # 7. Mostrar o gráfico no Streamlit
    st.plotly_chart(fig, use_container_width=True)   

def mostrar_resultados_simulados(nome, permissao, email, turma):

    import time
    start_time = time.time()

    progress_css = """
    <style>
    .progress-bar {
        background-color: #9e089e;
    }
    </style>
    """

    # Renderizar o CSS personalizado
    st.markdown(progress_css, unsafe_allow_html=True)

    progress_bar = st.progress(0)
    percentage_text = st.empty()

    estado = get_estado()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    alunos = ler_planilha("16IN1TyqZ2YXYRivDMPPZGspo5FpsGG53ZzWIk_07xLg", "Streamlit | Alunos!A1:D")
    alunos['Nome'] = alunos['Nome'].fillna('').astype(str)
    alunos = alunos[alunos['Nome'] != '']

    if turma is None:
        turma = turma
    elif "Esparta 2º" in turma:
        alunos = alunos[alunos['Turma'].str.contains("Esparta 2º")]
    elif "Esparta 3º" in turma:
        alunos = alunos[alunos['Turma'].str.contains("Esparta 3º")]
    elif (turma == None or turma == "-"):
        alunos = alunos
    elif "Revisão" in turma:
        alunos = alunos[alunos['Turma'].str.contains("Revisão")]
    else:
        alunos = alunos[~alunos['Turma'].str.contains("Esparta")]

    alunos_sn = ler_planilha("1F7sepzDX6VdYtUhCjClzJW280QYL_70GNLJFVwafYUk", "Central!A1:E")
    alunos_sn['Nome'] = alunos_sn['Nome'].fillna('').astype(str)
    alunos_sn = alunos_sn[alunos_sn['Nome'] != '']


    if (permissao == 'Aluno' or permissao == 'Responsável' or permissao == 'Inscrito Simulado Nacional'):

        nome_selecionado = nome

    
    else:

        nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(alunos_sn['Nome'].unique())
        
        #nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(alunos['Nome'].unique())

        nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos, key = 'Aluno')

        if nome_selecionado == 'Escolha o(a) aluno(a)':

            progress_bar.progress(100)
            percentage_text.text("100%")
            st.warning("Por favor, escolha um(a) aluno(a)!")
            st.stop()

    #turma_aluno = alunos.loc[alunos['Nome'] == nome_selecionado, 'Turma'].iloc[0]

    turma_aluno = alunos.loc[alunos['Nome'] == nome_selecionado, 'Turma']

    # Verificar se a série está vazia e atribuir o valor 'Turma do Simulado Nacional'
    if turma_aluno.empty:
        turma_aluno = 'Turma do Simulado Nacional'
    else:
        turma_aluno = turma_aluno.iloc[0]


    data_hoje_brasilia, hora_atual_brasilia = dia_hora()
    data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", nome_selecionado, email]]
    escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")

    progress_bar.progress(50)
    percentage_text.text("50%")

    if permissao != 'Inscrito Simulado Nacional':

        if (turma == 'Manhã' or turma == 'Tarde' or turma_aluno == 'Manhã' or turma_aluno == 'Tarde'):

            simulados = ["Escolha o simulado"] + ['Simulado Semana 01'] + ['Simulado Insper 01'] + ['Simulado FGV 01'] + ['Simulado Insper 02'] + ['Simulado FGV 02'] + ['Simulado Insper 03'] + ['Simulado FGV 03'] + ['Simulado Nacional Insper'] + ['Simulado Nacional FGV'] + ['Simulado FGV 05'] + ['Simulado Insper 05'] + ['Simulado FGV 06'] + ['Simulado Insper 06'] + ['Simulado Insper 07'] + ['Simulado Insper 08']# + ['Simulado FGV 02'] + ['Simulado FGV 03'] + ['Simulado FGV 04'] + ['Simulado FGV 05'] + ['Simulado FGV 06']

        elif (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º'):

            simulados = ["Escolha o simulado"] + ['Simulado Nacional Insper'] + ['Simulado Nacional FGV']# + ['Simulado Nacional FGV'] ['Simulado 01'] + ['Simulado 02'] + ['Simulado 03'] + ['Simulado 04'] + ['Simulado 05'] + ['Simulado 06'] + ['Simulado 07']

        elif (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2'):

            simulados = ["Escolha o simulado"] + ['Simulado 01'] + ['Simulado 02'] + ['Simulado 03'] + ['Simulado 04'] + ['Simulado Nacional Insper'] + ['Simulado Nacional FGV'] + ['Simulado 05'] + ['Simulado 06'] + ['Simulado 07']

        elif (turma == 'Turma do Simulado Nacional' or turma_aluno == 'Turma do Simulado Nacional'):

            simulados = ["Escolha o simulado"] + ["Simulado Nacional Insper"] + ['Simulado Nacional FGV']

        elif(turma == 'Revisão Online' or turma == 'Revisão Presencial' or turma_aluno == 'Revisão Online' or turma_aluno == 'Revisão Presencial'):

            simulados = ["Escolha o simulado"] + ["Simulado FGV 05"] + ["Simulado FGV 06"] + ["Simulado Insper 06"] + ["Simulado Insper 07"] + ["Simulado Insper 08"] + ["Simulado Nacional Insper"] + ['Simulado Nacional FGV']

        simulado_selecionado = st.selectbox('Selecione o simulado:', simulados)

        if simulado_selecionado == 'Escolha o simulado':

            progress_bar.progress(1.00)
            percentage_text.text("100%")
            st.warning("Por favor, escolha um simulado!")
            st.stop()

        if simulado_selecionado == 'Simulado Insper 01':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 01!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 01!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 02':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 02!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 02!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 03':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 03!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 03!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 04':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 04!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 04!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 05':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 05!A1:M22000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 05!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 06':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 06!A1:M22000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 06!A1:J22000")
        
        elif simulado_selecionado == 'Simulado Insper 07':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 07!A1:M22000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 07!A1:J22000")

        elif simulado_selecionado == 'Simulado Insper 08':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 08!A1:M22000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 08!A1:J2000")

        elif simulado_selecionado == 'Simulado Nacional Insper':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 04!A1:M29000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 04!A1:J22000")

        elif simulado_selecionado == 'Simulado FGV 01':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 01!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 01!A1:J4000")

        elif simulado_selecionado == 'Simulado FGV 02':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 02!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 02!A1:J4000")

        elif simulado_selecionado == 'Simulado FGV 03':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 03!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 03!A1:J4000")

        elif simulado_selecionado == 'Simulado FGV 05':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 05!A1:M4000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 05!A1:J4000")

        elif simulado_selecionado == 'Simulado Nacional FGV':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 04!A1:M29000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 04!A1:J4000")

        elif simulado_selecionado == 'Simulado FGV 06':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 06!A1:m22000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 06!A1:J4000")

        elif simulado_selecionado == 'Simulado Semana 01':

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Semana 01!A1:L3000")

        elif (simulado_selecionado == 'Simulado 01' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 01!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 01!A1:J4000")

        elif (simulado_selecionado == 'Simulado 02' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 02!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 02!A1:J4000")

        elif (simulado_selecionado == 'Simulado 03' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 03!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 03!A1:J4000")

        elif (simulado_selecionado == 'Simulado 04' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 04!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 04!A1:J4000")

        elif (simulado_selecionado == 'Simulado 05' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 05!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 05!A1:J4000")

        elif (simulado_selecionado == 'Simulado 06' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 06!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 06!A1:J4000")

        elif (simulado_selecionado == 'Simulado 07' and (turma == 'Esparta 2º' or turma_aluno == 'Esparta 2º')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 2º 07!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 2º 07!A1:J4000")

        elif (simulado_selecionado == 'Simulado 01' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 01!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 01!A1:J4000")

        elif (simulado_selecionado == 'Simulado 02' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 02!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 02!A1:J4000")

        elif (simulado_selecionado == 'Simulado 03' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 03!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 03!A1:J4000")

        elif (simulado_selecionado == 'Simulado 04' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 04!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 04!A1:J4000")

        elif (simulado_selecionado == 'Simulado 05' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 05!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 05!A1:J4000")

        elif (simulado_selecionado == 'Simulado 06' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 06!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 06!A1:J4000")

        elif (simulado_selecionado == 'Simulado 07' and (turma == 'Esparta 3º' or turma_aluno == 'Esparta 3º 1' or turma_aluno == 'Esparta 3º 2')):

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Esparta 3º 07!A1:L3000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Esparta 3º 07!A1:J4000")

        '''
        
        #### BASES INSPER

        base_resultados_matbasica = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Matemática Básica!A1:I3000")

        progress_bar.progress(0.10)
        percentage_text.text("10%")

        base_resultados_insper1 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Insper 01!A1:M4000")

        progress_bar.progress(0.15)
        percentage_text.text("15%")

        base_resultados_insper2 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Insper 02!A1:M4000")

        base_resultados_insper3 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Insper 03!A1:M4000")

        base_resultados_insper4 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Insper 04!A1:M4000")

        base_resultados_insper5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | Insper 05!A1:L24000")

        progress_bar.progress(0.20)
        percentage_text.text("20%")

        base_resultados_insper_aux = pd.concat([base_resultados_insper1, base_resultados_insper2], axis=0)#.reset_index()
        base_resultados_insper_aux2 = pd.concat([base_resultados_insper_aux, base_resultados_insper3], axis=0)
        base_resultados_insper_aux3 = pd.concat([base_resultados_insper_aux2, base_resultados_insper4], axis=0)
        base_resultados_insper = pd.concat([base_resultados_insper_aux3, base_resultados_insper5], axis=0).reset_index()

        ### BASES FGV

        base_resultados_fgv1 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | FGV 01!A1:K4000")

        progress_bar.progress(0.25)
        percentage_text.text("25%")
        
        base_resultados_fgv2 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | FGV 02!A1:K4000")

        base_resultados_fgv3 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | FGV 03!A1:K4000")

        base_resultados_fgv4 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | FGV 04!A1:K4000")

        base_resultados_fgv5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "RelSimulado | FGV 05!A1:K4000")

        progress_bar.progress(0.30)
        percentage_text.text("30%")
        
        base_resultados_fgv_aux = pd.concat([base_resultados_fgv1, base_resultados_fgv2], axis=0)

        base_resultados_fgv_aux2 = pd.concat([base_resultados_fgv_aux, base_resultados_fgv3], axis=0)

        base_resultados_fgv_aux3 = pd.concat([base_resultados_fgv_aux2, base_resultados_fgv4], axis=0)

        base_resultados_fgv = pd.concat([base_resultados_fgv_aux3, base_resultados_fgv5], axis=0).reset_index()
        
        base_resultados_aux = pd.concat([base_resultados_matbasica, base_resultados_insper], axis=0).reset_index()
        
        base_resultados_aux = base_resultados_aux.drop(columns = ['level_0'])

        base_resultados = pd.concat([base_resultados_aux, base_resultados_fgv], axis=0).reset_index()

        #simulados = ["Escolha o simulado"] + sorted(base_resultados['Simulado'].drop_duplicates().sort_values().unique())

        #st.write(simulados)

        #simulado_selecionado = st.selectbox('Selecione o simulado:', simulados)
        
        #if simulado_selecionado == 'Escolha o simulado':
        #
        #    progress_bar.progress(1.00)
        #    percentage_text.text("100%")
        #    st.warning("Por favor, escolha um simulado!")
        #    st.stop()

        base_matriz_matbasica = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Matemática Básica!A1:G1000")

        base_matriz_insper1 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 01!A1:G1000")

        base_matriz_insper2 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 02!A1:G1000")

        base_matriz_insper3 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 03!A1:G1000")

        base_matriz_insper4 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 04!A1:G1000")

        base_matriz_insper5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 05!A1:G1000")

        progress_bar.progress(0.35)
        percentage_text.text("35%")

        base_matriz_insper_aux = pd.concat([base_matriz_insper1, base_matriz_insper2], axis=0)#.reset_index()
        base_matriz_insper_aux2 = pd.concat([base_matriz_insper_aux, base_matriz_insper3], axis=0)
        base_matriz_insper_aux3 = pd.concat([base_matriz_insper_aux2, base_matriz_insper4], axis=0)
        base_matriz_insper = pd.concat([base_matriz_insper_aux3, base_matriz_insper5], axis=0).reset_index()
    
        base_matriz_fgv1 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | FGV 01!A1:G1000")

        base_matriz_fgv2 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | FGV 02!A1:G61")

        base_matriz_fgv3 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | FGV 03!A1:G61")

        base_matriz_fgv4 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | FGV 04!A1:G61")

        base_matriz_fgv5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | FGV 05!A1:G61")

        progress_bar.progress(0.40)
        percentage_text.text("40%")

        base_matriz_fgv_aux = pd.concat([base_matriz_fgv1, base_matriz_fgv2], axis=0)

        base_matriz_fgv_aux2 = pd.concat([base_matriz_fgv_aux, base_matriz_fgv3], axis=0)

        base_matriz_fgv_aux3 = pd.concat([base_matriz_fgv_aux2, base_matriz_fgv4], axis=0)

        base_matriz_fgv = pd.concat([base_matriz_fgv_aux3, base_matriz_fgv5], axis=0).reset_index()
    
        base_redacao_insper1 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Red | Insper 01!A1:J22000")
        
        base_redacao_insper2 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Red | Insper 02!A1:J22000")

        base_redacao_insper3 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Red | Insper 03!A1:J22000")

        base_redacao_insper4 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Red | Insper 04!A1:J22000")

        base_redacao_insper5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Red | Insper 05!A1:J22000")

        progress_bar.progress(0.45)
        percentage_text.text("45%")
        
        base_redacao_insper_aux = pd.concat([base_redacao_insper1, base_redacao_insper2], axis=0)#.reset_index()
        base_redacao_insper_aux2 = pd.concat([base_redacao_insper_aux, base_redacao_insper3], axis=0)
        base_redacao_insper_aux3 = pd.concat([base_redacao_insper_aux2, base_redacao_insper4], axis=0)
        base_redacao_insper = pd.concat([base_redacao_insper_aux3, base_redacao_insper5], axis=0).reset_index()

        base_redacao_fgv = ler_planilha("1dwbt5wTCV1Dj0pukwCZDy4i6p6E3_bTYzDwNHFXfmV0", "Todos | Redação | FGV!A1:I22000")

        base_matriz_aux = pd.concat([base_matriz_matbasica, base_matriz_insper], axis=0).reset_index()
        base_matriz_aux = base_matriz_aux.drop(columns = ['level_0'])
        base_matriz = pd.concat([base_matriz_aux, base_matriz_fgv], axis=0).reset_index()

        base_redacao = pd.concat([base_redacao_insper, base_redacao_fgv], ignore_index=True)

        '''

    else:

        simulados = ["Escolha o simulado"] + ['Simulado Nacional Insper'] + ['Simulado Nacional FGV']

        simulado_selecionado2 = st.selectbox('Selecione o simulado:', simulados)

        if simulado_selecionado2 == 'Simulado Nacional FGV':

            simulado_selecionado = 'Simulado Nacional FGV'

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | FGV 04!A1:m29000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | FGV 04!A1:J22000")
            

        elif simulado_selecionado2 == 'Simulado Nacional Insper':

            simulado_selecionado = 'Simulado Nacional Insper'

            base_resultados = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "RelSimulado | Insper 04!A1:M29000")
            base_redacao = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Red | Insper 04!A1:J22000")  

        else:

            simulado_selecionado = 'Escolha o simulado'  

        #base_matriz_insper5 = ler_planilha("1iLxsOaDPsyraduRGj_kZWmuEMRqo5VSGURKWuXD40M8", "Matriz | Insper 05!A1:G1000")

        #base_matriz = base_matriz_insper5.copy()

    turma_eng12 = 'Engenharias e Ciência da Computação'
    turma_cien12 = 'Engenharias e Ciência da Computação'
    turma_adm12 = 'Administração, Economia e Direito'
    turma_eco12 = 'Administração, Economia e Direito'
    turma_dir12 = 'Administração, Economia e Direito'
    turma_eco = 'Economia'
    turma_adm = 'Administração'
    turma_dir = 'Direito'
    turma_eng = 'Engenharia'
    turma_cien = 'Ciência da Computação'
    turma_nat = 'Natureza'
    turma_hum = 'Humanas'

    turma_eng2 = 'Engenharias e Ciência da Computação'
    turma_cien2 = 'Engenharias e Ciência da Computação'
    turma_adm2 = 'Administração, Economia e Direito'
    turma_eco2 = 'Administração, Economia e Direito'
    turma_dir2 = 'Administração, Economia e Direito'

    #base_resultados['Disciplina'] = ''
    #base_resultados['Assunto'] = ''

    bar_color = '#9E089E'

    end_time = time.time()
    elapsed_time = end_time - start_time

    #st.write(elapsed_time)

    #if permissao == 'Aluno':

    #    login_aluno = email

    #else:

    #    nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(base_resultados['aluno_nome'].unique())
    #    nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

    #    if nome_selecionado != 'Escolha o(a) aluno(a)':

    #        auxiliar_aluno = base_resultados[base_resultados['aluno_nome'] == nome_selecionado].reset_index(drop = True)  
    #        login_aluno = auxiliar_aluno['aluno_login'][0]

    #    else:

    #        login_aluno = ''

        #login_aluno = st.text_input('Digite o seu login', '')


    if (nome_selecionado == 'Escolha o(a) aluno(a)' or simulado_selecionado == 'Escolha o simulado'):

        #progress_bar.progress(0.4)
        #percentage_text.text("40%")

        progress_bar.progress(1)
        percentage_text.text("100%")

    if (nome_selecionado != 'Escolha o(a) aluno(a)' and simulado_selecionado != 'Escolha o simulado'):

        base_resultados_simu_selecionado = base_resultados.copy()

        #base_resultados_simu_selecionado = base_resultados[base_resultados['Simulado'] == simulado_selecionado]
        base_resultados_simu_selecionado = base_resultados_simu_selecionado[base_resultados_simu_selecionado['num_exercicio'] != "61"].reset_index(drop = True) 

        auxiliar_aluno = base_resultados_simu_selecionado[base_resultados_simu_selecionado['aluno_nome'] == nome_selecionado].reset_index(drop = True)  

        login_aluno = auxiliar_aluno['aluno_login'][0]

        '''
    #if login_aluno != '':
        #estado['pagina_atual'] = 'Alunos - Resultados nos simulados [pós login]'
        # Substituindo o range(len(...)) pelo tqdm para adicionar a barra de progresso
        for i in tqdm(range(len(base_resultados_simu_selecionado['atividade_nome'])), desc='Processando dados', unit='item'):
            turma_atual = base_resultados_simu_selecionado['turma'][i]
            simulado_atual = base_resultados_simu_selecionado['Simulado'][i]
            num_exercicio_atual = base_resultados_simu_selecionado['num_exercicio'][i]

            matriz_questoes = base_matriz[base_matriz['Simulado'] == simulado_atual]
            matriz_questoes = matriz_questoes[matriz_questoes['num_exercicio'] != "61"]

            if turma_atual in [turma_eng12, turma_eng2, turma_cien12, turma_cien2, turma_eng, turma_cien, turma_nat]:
                matriz_questoes = matriz_questoes[matriz_questoes['disciplina'] != 'Ciências Humanas']
                matriz_questoes = matriz_questoes[matriz_questoes['num_exercicio_eng'] == num_exercicio_atual].reset_index(drop=True)
            else:
                matriz_questoes = matriz_questoes[matriz_questoes['disciplina'] != 'Ciências da Natureza']
                matriz_questoes = matriz_questoes[matriz_questoes['num_exercicio'] == num_exercicio_atual].reset_index(drop=True)

            # matriz_questoes = matriz_questoes[matriz_questoes['num_exercicio_eng'] == num_exercicio_atual].reset_index(drop=True)
            #st.write(base_resultados_simu_selecionado['aluno_nome'][i])
            #st.write(len(matriz_questoes))
            if len(matriz_questoes) > 0:
                base_resultados_simu_selecionado['Disciplina'][i] = matriz_questoes['disciplina'][0]
                base_resultados_simu_selecionado['Assunto'][i] = matriz_questoes['assunto'][0]

            # Atualizando a barra de progresso e o componente de texto a cada iteração
            progress_bar.progress(((i + 1) / len(base_resultados_simu_selecionado['atividade_nome']))/2 + 0.5)
            percentage_text.text(f"{round(((i + 1) / len(base_resultados_simu_selecionado['atividade_nome'])) * 100/2 + 50)}%")

        # Removendo a barra de progresso e o componente de texto no final do loop
        st.empty()

        '''
    else:

        if permissao != 'Inscrito Simulado Nacional':

            st.warning('Por favor, selecione o(a) aluno(a) e o simulado para continuar.')
        
        else:

            st.warning('Por favor, selecione o simulado para continuar.')

    if (nome_selecionado != 'Escolha o(a) aluno(a)' and simulado_selecionado != 'Escolha o simulado'):

        base = base_resultados_simu_selecionado.copy()

        base.rename(columns = {'atividade_nome':'Nome da avaliação','turma':'Turma','aluno_nome':'Nome do aluno(a)','aluno_login':'Login do aluno(a)','num_exercicio':'Número da questão','certo_ou_errado':'Certo ou errado','valor_do_exercicio':'Valor da questão','frente':'Frente','turma_jazz':'Turma Jazz'}, inplace = True)

        #base['Valor da questão'] = base['Valor da questão'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")))

        base['Valor da questão'] = base['Valor da questão'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")) if pd.notnull(x) and str(x).replace(".", "").replace(",", "").isdigit() else np.nan)

        base['Acerto'] = 0.00
        base['Nota na questão'] = 0.00
        base['Novo Nota na questão'] = 0.00
        base['Novo Valor da questão'] = base['Valor da questão']

        base['Acerto'] = np.where((base['Certo ou errado'] == 'certo') & (base['Número da questão'] != 61), 1, 0)
        base['Novo Nota na questão'] = base['Acerto'] * base['Novo Valor da questão']
        base['Nota na questão'] = base['Acerto'] * base['Valor da questão']

        base['Fez questão'] = base['Certo ou errado'].apply(lambda x: 1.00 if x in ['certo', 'errado'] else 0.00)

        resultados_gerais = base.groupby(['Nome da avaliação','Turma','Nome do aluno(a)','Login do aluno(a)','Simulado','Estratégia','Turma Jazz']).sum().reset_index()

        progress_bar.progress(0.6)
        percentage_text.text("60%")

        resultados_gerais2 = resultados_gerais.groupby(['Turma','Nome do aluno(a)','Login do aluno(a)','Simulado','Estratégia','Turma Jazz']).sum().reset_index()

        resultados_gerais2_aux = resultados_gerais2.copy()

        for i in range(len(resultados_gerais2_aux['Login do aluno(a)'])):
            if resultados_gerais2_aux['Simulado'][i][:15] == 'Simulado Insper':
                resultados_gerais2_aux['Nota na questão'][i] = (4/3)*resultados_gerais2_aux['Nota na questão'][i]
                resultados_gerais2_aux['Novo Nota na questão'][i] = (4/3)*resultados_gerais2_aux['Novo Nota na questão'][i]
            elif resultados_gerais2_aux['Simulado'][i][:15] == 'Simulado Semana':
                resultados_gerais2_aux['Nota na questão'][i] = (1.25)*resultados_gerais2_aux['Nota na questão'][i]
                resultados_gerais2_aux['Novo Nota na questão'][i] = (1.25)*resultados_gerais2_aux['Novo Nota na questão'][i]

        resultados_gerais3 = resultados_gerais2_aux.sort_values(by = 'Nota na questão', ascending = False).reset_index(drop = True)  

        progress_bar.progress(0.8)
        percentage_text.text("80%")

        #simulados = resultados_gerais3['Simulado'].drop_duplicates().sort_values()

        #simulados = ["Escolha o(a) aluno(a)"] + sorted(resultados_gerais3['Simulado'].drop_duplicates().sort_values().unique())

        #simulado_selecionado = st.selectbox('Selecione o simulado:', simulados)

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()

        if permissao == 'Aluno':

            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], simulado_selecionado, "", email]]

        else:

            nome_aluno4 = nome_selecionado
            #nome_aluno4 = resultados_gerais3[resultados_gerais3['Login do aluno(a)'] == login_aluno]['Nome do aluno(a)'].reset_index()
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], simulado_selecionado, nome_aluno4, email]]
            #data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], simulado_selecionado, nome_aluno4['Nome do aluno(a)'][0], email]]

        escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")


    if (nome_selecionado != 'Escolha o(a) aluno(a)' and simulado_selecionado != 'Escolha o simulado'):

        resultados_gerais3["Login do aluno(a)"] = resultados_gerais3["Login do aluno(a)"].apply(extract_login)
        nome_aluno3 = resultados_gerais3[resultados_gerais3['Login do aluno(a)'] == login_aluno]['Nome do aluno(a)'].reset_index()
        turma_aluno = resultados_gerais3[resultados_gerais3['Login do aluno(a)'] == login_aluno]['Turma'].reset_index()
        turma_jazz = resultados_gerais3[resultados_gerais3['Login do aluno(a)'] == login_aluno]['Turma Jazz'].reset_index(drop = True)

        if simulado_selecionado == 'Simulado Nacional Insper':

            resultado_2fase = ler_planilha("1aAxlTljt6SNvrZQSbHbZrhlG1EBfdidWCbFaFkz9EqU", "Streamlit | Simulado Nacional 2ª fase Insper!A1:I")
            
            resultado_2fase_aluno_fez = resultado_2fase[resultado_2fase['Nome'] == nome_selecionado]

            if len(resultado_2fase_aluno_fez) > 0:

                resultado_2fase_debate = resultado_2fase[resultado_2fase['Dinâmica'] == 'Debate']

                resultado_2fase_debate2 = resultado_2fase_debate[resultado_2fase_debate['Nota'] != '']
                resultado_2fase_debate2['Nota'] = resultado_2fase_debate2['Nota'].astype(int)
                resultado_2fase_debate3 = int(round(250 * resultado_2fase_debate2['Nota'].mean(), 0))

                resultado_2fase_debate4 = resultado_2fase_debate2.groupby(['Nome','Estratégia']).mean('Nota').reset_index()
                resultado_2fase_debate4 = resultado_2fase_debate4.sort_values(by='Nota', ascending=False)
                resultado_2fase_debate4['Classificação'] = resultado_2fase_debate4['Nota'].rank(ascending=False, method='min').astype(int)

                resultado_2fase_debate_aluno = resultado_2fase_debate4[resultado_2fase_debate4['Nome'] == nome_selecionado].reset_index(drop = True)
                
                if len(resultado_2fase_debate_aluno) > 0:
                
                    resultado_2fase_debate_aluno2 = int(round(250*resultado_2fase_debate_aluno['Nota'].mean(), 0))
                    
                    resultado_2fase_debate_aluno0 = resultado_2fase_debate2[resultado_2fase_debate2['Nome'] == nome_selecionado].reset_index(drop = True)

                    resultado_2fase_debate_aluno_media = resultado_2fase_debate_aluno0.groupby(['Tema', 'Frase Tema', 'Habilidade'], as_index=False).agg({'Nota': 'mean'}).rename(columns={'Nota': 'Nota_Aluno'})

                    resultado_2fase_debate_media = resultado_2fase_debate2.groupby(['Tema', 'Frase Tema', 'Habilidade'], as_index=False).agg({'Nota': 'mean'}).rename(columns={'Nota': 'Nota_Média_Geral'})            

                    resultado_2fase_debate_tabela = pd.merge(resultado_2fase_debate_aluno_media, resultado_2fase_debate_media, on=['Tema', 'Frase Tema', 'Habilidade'])

                    resultado_2fase_debate_tabela2 = resultado_2fase_debate_tabela.pivot(index=['Tema', 'Frase Tema'], columns='Habilidade', values=['Nota_Aluno', 'Nota_Média_Geral']).reset_index()            

                    resultado_2fase_debate_tabela2.columns = ['_'.join(col).strip() if type(col) is tuple else col for col in resultado_2fase_debate_tabela2.columns]

                    colunas_ordenadas = [
                        'Tema_',
                        'Frase Tema_', 
                        'Nota_Aluno_Pensamento Crítico', 'Nota_Média_Geral_Pensamento Crítico',
                        'Nota_Aluno_Comunicação Assertiva', 'Nota_Média_Geral_Comunicação Assertiva',
                        'Nota_Aluno_Interação com Pessoas', 'Nota_Média_Geral_Interação com Pessoas'
                    ]

                    resultado_2fase_debate_tabela2['Nota_Aluno_Pensamento Crítico'] = resultado_2fase_debate_tabela2['Nota_Aluno_Pensamento Crítico'].round(0).astype(int)
                    resultado_2fase_debate_tabela2['Nota_Aluno_Comunicação Assertiva'] = resultado_2fase_debate_tabela2['Nota_Aluno_Comunicação Assertiva'].round(0).astype(int)
                    resultado_2fase_debate_tabela2['Nota_Aluno_Interação com Pessoas'] = resultado_2fase_debate_tabela2['Nota_Aluno_Interação com Pessoas'].round(0).astype(int)

                    resultado_2fase_debate_tabela2['Nota_Média_Geral_Pensamento Crítico'] = resultado_2fase_debate_tabela2['Nota_Média_Geral_Pensamento Crítico'].round(1)
                    resultado_2fase_debate_tabela2['Nota_Média_Geral_Comunicação Assertiva'] = resultado_2fase_debate_tabela2['Nota_Média_Geral_Comunicação Assertiva'].round(1)
                    resultado_2fase_debate_tabela2['Nota_Média_Geral_Interação com Pessoas'] = resultado_2fase_debate_tabela2['Nota_Média_Geral_Interação com Pessoas'].round(1)

                    resultado_2fase_debate_tabela2 = resultado_2fase_debate_tabela2[colunas_ordenadas]

                resultado_2fase_arguicao = resultado_2fase[resultado_2fase['Dinâmica'] == 'Arguição']

                resultado_2fase_arguicao2 = resultado_2fase_arguicao[resultado_2fase_arguicao['Nota'] != '']
                resultado_2fase_arguicao2['Nota'] = resultado_2fase_arguicao2['Nota'].astype(int)
                resultado_2fase_arguicao3 = int(round(250 * resultado_2fase_arguicao2['Nota'].mean(), 0))

                resultado_2fase_arguicao4 = resultado_2fase_arguicao2.groupby(['Nome','Estratégia']).mean('Nota').reset_index()
                resultado_2fase_arguicao4 = resultado_2fase_arguicao4.sort_values(by='Nota', ascending=False)
                resultado_2fase_arguicao4['Classificação'] = resultado_2fase_arguicao4['Nota'].rank(ascending=False, method='min').astype(int)

                resultado_2fase_arguicao_aluno = resultado_2fase_arguicao4[resultado_2fase_arguicao4['Nome'] == nome_selecionado].reset_index(drop = True)
                
                if len(resultado_2fase_arguicao_aluno) > 0:

                    resultado_2fase_arguicao_aluno2 = int(round(250*resultado_2fase_arguicao_aluno['Nota'].mean(), 0))

                    resultado_2fase_arguicao_aluno0 = resultado_2fase_arguicao2[resultado_2fase_arguicao2['Nome'] == nome_selecionado].reset_index(drop = True)

                    resultado_2fase_arguicao_aluno_media = resultado_2fase_arguicao_aluno0.groupby(['Tema', 'Frase Tema', 'Habilidade'], as_index=False).agg({'Nota': 'mean'}).rename(columns={'Nota': 'Nota_Aluno'})

                    resultado_2fase_arguicao_media = resultado_2fase_arguicao2.groupby(['Tema', 'Frase Tema', 'Habilidade'], as_index=False).agg({'Nota': 'mean'}).rename(columns={'Nota': 'Nota_Média_Geral'})            

                    resultado_2fase_arguicao_tabela = pd.merge(resultado_2fase_arguicao_aluno_media, resultado_2fase_arguicao_media, on=['Tema', 'Frase Tema', 'Habilidade'])

                    resultado_2fase_arguicao_tabela2 = resultado_2fase_arguicao_tabela.pivot(index=['Tema', 'Frase Tema'], columns='Habilidade', values=['Nota_Aluno', 'Nota_Média_Geral']).reset_index()            

                    resultado_2fase_arguicao_tabela2.columns = ['_'.join(col).strip() if type(col) is tuple else col for col in resultado_2fase_arguicao_tabela2.columns]

                    colunas_ordenadas = [
                        'Tema_',
                        'Frase Tema_',
                        'Nota_Aluno_Aprender a Aprender', 'Nota_Média_Geral_Aprender a Aprender',
                    ]

                    resultado_2fase_arguicao_tabela2['Nota_Aluno_Aprender a Aprender'] = resultado_2fase_arguicao_tabela2['Nota_Aluno_Aprender a Aprender'].round(0).astype(int)

                    resultado_2fase_arguicao_tabela2['Nota_Média_Geral_Aprender a Aprender'] = resultado_2fase_arguicao_tabela2['Nota_Média_Geral_Aprender a Aprender'].round(1)

                    resultado_2fase_arguicao_tabela2 = resultado_2fase_arguicao_tabela2[colunas_ordenadas]

                if (len(resultado_2fase_debate_aluno) > 0 and len(resultado_2fase_arguicao_aluno) > 0):

                    resultado_2fase_completo = pd.merge(resultado_2fase_debate4, resultado_2fase_arguicao4, on=['Nome','Estratégia'], how='outer')

                    resultado_2fase_completo.rename(columns = {'Nota_x':'Nota Debate','Nota_y':'Nota Arguição'}, inplace = True)
                    resultado_2fase_completo['Nota'] = 0.75*resultado_2fase_completo['Nota Debate'] + 0.25*resultado_2fase_completo['Nota Arguição']
                    #resultado_2fase_completo['Nota'] = resultado_2fase_completo['Nota']/250
                    resultado_2fase_completo = resultado_2fase_completo[resultado_2fase_completo['Nota'] > 0]
                    resultado_2fase_completo['Classificação'] = resultado_2fase_completo['Nota'].rank(ascending=False, method='min').astype(int)
                    resultado_2fase_completo2 = int(round(250*resultado_2fase_completo['Nota'].mean(), 0))

                    resultado_2fase_completo_aluno = resultado_2fase_completo[resultado_2fase_completo['Nome'] == nome_selecionado].reset_index(drop = True)
                    resultado_2fase_completo_aluno2 = int(round(250*resultado_2fase_completo_aluno['Nota'].mean(), 0))

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>2ª Fase</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    cards_principais_2fase(resultado_2fase_completo_aluno2, resultado_2fase_completo2, str(resultado_2fase_completo_aluno['Classificação'][0])+"º", len(resultado_2fase_completo))

                    criar_histograma_2fase(resultado_2fase_completo, nome_aluno3)

                if len(resultado_2fase_debate_aluno) > 0:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Debate</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                    cards_principais_2fase(resultado_2fase_debate_aluno2, resultado_2fase_debate3, str(resultado_2fase_debate_aluno['Classificação'][0])+"º", len(resultado_2fase_debate4))

                    criar_histograma_2fase(resultado_2fase_debate4, nome_aluno3)

                    tabela_debate(resultado_2fase_debate_tabela2)

                if len(resultado_2fase_arguicao_aluno) > 0:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Arguição</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                    cards_principais_2fase(resultado_2fase_arguicao_aluno2, resultado_2fase_arguicao3, str(resultado_2fase_arguicao_aluno['Classificação'][0])+"º", len(resultado_2fase_arguicao4))

                    criar_histograma_2fase(resultado_2fase_arguicao4, nome_aluno3)

                    tabela_arguicao(resultado_2fase_arguicao_tabela2)


    if (nome_selecionado != 'Escolha o(a) aluno(a)' and simulado_selecionado != 'Escolha o simulado'):

        resultados_gerais3['Classificação'] = resultados_gerais3['Acerto'].rank(method='min', ascending=False).astype(int)

        resultados_gerais_aluno1 = resultados_gerais3[resultados_gerais3['Nome do aluno(a)'] == nome_aluno3['Nome do aluno(a)'][0]]

        if resultados_gerais_aluno1['Acerto'].sum() > 0:

            #if permissao != 'Inscrito Simulado Nacional':

            #    resultados_gerais_aluno1 = resultados_gerais_aluno1.drop(columns = ['level_0']) ###

            resultados_gerais_aluno = resultados_gerais_aluno1[resultados_gerais_aluno1['Simulado'] == simulado_selecionado].reset_index()

            resultados_gerais4 = resultados_gerais3[resultados_gerais3['Nota na questão'] > 0]

            resultados_gerais4_aux = resultados_gerais4[['Login do aluno(a)','Valor da questão','Acerto','Nota na questão','Simulado', 'Novo Nota na questão','Fez questão']]
            resultados_gerais5_aux = resultados_gerais4_aux.copy()
            resultados_gerais5 = resultados_gerais5_aux[resultados_gerais5_aux['Simulado'] == simulado_selecionado].reset_index() 

            alunos_fizeram = pd.DataFrame()

            #if permissao != 'Inscrito Simulado Nacional':

            #    resultados_gerais4 = resultados_gerais4.drop(columns = ['level_0']) ###

            resultados_gerais4_aux2 = resultados_gerais4[resultados_gerais4['Simulado'] == simulado_selecionado].reset_index()

            alunos_fizeram['Nome do aluno(a)'] = resultados_gerais4_aux2['Nome do aluno(a)']

            numero_candidatos = len(resultados_gerais4['Nome do aluno(a)'])
            aux = resultados_gerais4[(resultados_gerais4['Turma'] == turma_eng12) | (resultados_gerais4['Turma'] == turma_eng2)]
            aux2 = resultados_gerais4[(resultados_gerais4['Turma'] == turma_cien12) | (resultados_gerais4['Turma'] == turma_cien2)]
            numero_eng_cien = len(aux['Nome do aluno(a)']) + len(aux2['Nome do aluno(a)'])

            progress_bar.progress(1.00)
            percentage_text.text("100%")

            st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

            #if simulado_selecionado != 'Simulado Matemática Básica':

            st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Prova Objetiva</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            if "Insper" in simulado_selecionado:

                if simulado_selecionado != 'Simulado Nacional Insper':

                    cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)/10), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean()/10,-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'Insper Total', '0', '0', 0)

                else:

                    resultados_gerais5_60 = resultados_gerais5#[resultados_gerais5['Fez questão'] > 40]

                    cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)/10), int(round(truncar(resultados_gerais5_60['Novo Nota na questão'].mean()/10,-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5_60['Acerto'].mean(),0)),'Simulado Nacional Insper 1ª fase Total', str(int(round(truncar(resultados_gerais_aluno['Classificação'][0],0),0)))+'º',int(len(resultados_gerais5['index'])), 0)

            if "FGV" in simulado_selecionado:

                if simulado_selecionado != 'Simulado Nacional FGV':

                    cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)/10), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean()/10,-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'FGV Total', '0', '0', 0)

                else:

                    resultados_gerais5_40 = resultados_gerais5#[resultados_gerais5['Fez questão'] > 40]

                    cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais5_40['Novo Nota na questão'].mean()/10,-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5_40['Acerto'].mean(),0)),'Simulado Nacional FGV 1ª fase Total', str(int(round(truncar(resultados_gerais_aluno['Classificação'][0],0),0)))+'º',int(len(resultados_gerais5['index'])), 0)
                    

            if "Simulado 0" in simulado_selecionado:

                if (turma == 'Esparta 3º' or turma_jazz[0] == 'Esparta 3º 1' or turma_jazz[0] == 'Esparta 3º 2'):

                    if "Simulado 01" in simulado_selecionado:
                    
                        cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean(),-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Geral')

                    else:
                        
                        cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean(),-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Geral')

                if (turma == 'Esparta 2º' or turma_jazz[0] == 'Esparta 2º'):
                    
                    cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean(),-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'Esparta 2º', '0', '0', simulado_selecionado[-1]+' Geral')
            
            if "Semana 01" in simulado_selecionado:

                cards_principais(int(round(resultados_gerais_aluno['Novo Nota na questão'][0]/12.5,1)), int(round(truncar(resultados_gerais5['Novo Nota na questão'].mean()/12.5,-1))), int(round(truncar(resultados_gerais_aluno['Acerto'][0],0),0)), int(round(resultados_gerais5['Acerto'].mean(),0)),'Semana 01', '0', '0', 0)

            if simulado_selecionado == 'Simulado Nacional Insper':

                criar_histograma_acertos(resultados_gerais3, nome_aluno3, 60)

            if simulado_selecionado == 'Simulado Nacional FGV':

                resultados_gerais3_aux = resultados_gerais3[resultados_gerais3['Acerto'] > 10]
                criar_histograma_acertos(resultados_gerais3_aux, nome_aluno3, 60)
                
            
            base_alunos_fizeram_aux = base[base['Nome do aluno(a)'].isin(alunos_fizeram['Nome do aluno(a)'])].reset_index(drop = True)

            base_alunos_fizeram = base_alunos_fizeram_aux[base_alunos_fizeram_aux['Simulado'] == simulado_selecionado]

            base_alunos_fizeram_aux2 = base_alunos_fizeram.drop(columns = ['Nome da avaliação','Certo ou errado','Assunto'])

            resultados_gerais_disciplina_aux = base_alunos_fizeram_aux2.groupby(['Turma','Login do aluno(a)','Nome do aluno(a)','Disciplina','Simulado','Estratégia']).sum().reset_index()

            resultados_gerais_disciplina = resultados_gerais_disciplina_aux[resultados_gerais_disciplina_aux['Acerto'] >= 0]

            resultados_gerais_disciplina2 = resultados_gerais_disciplina#.drop(columns = ['Número da questão'])

            resultados_gerais_disciplina3 = resultados_gerais_disciplina2.sort_values(by = 'Nota na questão', ascending = False).reset_index(drop = True)

            resultados_gerais_disciplina3['Nota na questão'] = 1000*resultados_gerais_disciplina3['Nota na questão']/resultados_gerais_disciplina3['Valor da questão']
                
            resultados_gerais_disciplina3_aux = resultados_gerais_disciplina3.drop(columns = ['Turma','Login do aluno(a)','Nome do aluno(a)','Simulado'])

            resultados_gerais_disciplina4 = resultados_gerais_disciplina3_aux.groupby('Disciplina').agg({
                    'Valor da questão': 'mean',
                    'Acerto': 'mean',
                    'Nota na questão': 'mean',
                    'Novo Nota na questão': 'mean',
                    'Novo Valor da questão': 'mean'
                }).reset_index()

            resultados_gerais_disciplina5 = resultados_gerais_disciplina4.sort_values(by = 'Disciplina', ascending = False)

            resultados_gerais_disciplina3['Login do aluno(a)'] = resultados_gerais_disciplina3['Login do aluno(a)'].apply(extract_login)
            
            #if permissao != 'Inscrito Simulado Nacional':
            
            #    resultados_gerais_disciplina3 = resultados_gerais_disciplina3.drop(columns = ['level_0']) ###

            resultados_disciplina_aluno = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Login do aluno(a)'] == login_aluno].reset_index()
            resultados_disciplina_aluno2 = resultados_disciplina_aluno.sort_values(by = 'Disciplina', ascending = False)

            #if permissao != 'Inscrito Simulado Nacional':

            #    resultados_disciplina_aluno2 = resultados_disciplina_aluno2.drop(columns=['level_0'])      
            resultados_matematica = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Matemática'].reset_index()
            resultados_linguagens = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Linguagens'].reset_index()
            resultados_lingua_port = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Língua Portuguesa'].reset_index()
            resultados_ciencias_hum = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Ciências Humanas'].reset_index()
            resultados_ciencias_nat = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Ciências da Natureza'].reset_index()
            resultados_ingles = resultados_disciplina_aluno2[resultados_disciplina_aluno2['Disciplina'] == 'Inglês'].reset_index()
            
            resultados_gerais_disciplina3_mat = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Matemática'].reset_index(drop = True).reset_index()
            resultados_gerais_disciplina3_lin = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Linguagens'].reset_index(drop = True).reset_index()
            resultados_gerais_disciplina3_lp = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Língua Portuguesa'].reset_index(drop = True).reset_index()
            resultados_gerais_disciplina3_hum = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Ciências Humanas'].reset_index(drop = True).reset_index()
            resultados_gerais_disciplina3_nat = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Ciências da Natureza'].reset_index(drop = True).reset_index()
            resultados_gerais_disciplina3_ing = resultados_gerais_disciplina3[resultados_gerais_disciplina3['Disciplina'] == 'Inglês'].reset_index(drop = True).reset_index()
                        
            #classificacao_aluno_mat = resultados_gerais_disciplina3_mat[resultados_gerais_disciplina3_mat['Login do aluno(a)'] == login_aluno].reset_index()
            #classificacao_aluno_lin = resultados_gerais_disciplina3_lin[resultados_gerais_disciplina3_lin['Login do aluno(a)'] == login_aluno].reset_index()
            #classificacao_aluno_lp = resultados_gerais_disciplina3_lp[resultados_gerais_disciplina3_lp['Login do aluno(a)'] == login_aluno].reset_index()
            #classificacao_aluno_hum = resultados_gerais_disciplina3_hum[resultados_gerais_disciplina3_hum['Login do aluno(a)'] == login_aluno].reset_index()
            #classificacao_aluno_nat = resultados_gerais_disciplina3_nat[resultados_gerais_disciplina3_nat['Login do aluno(a)'] == login_aluno].reset_index()
            #classificacao_aluno_ing = resultados_gerais_disciplina3_ing[resultados_gerais_disciplina3_ing['Login do aluno(a)'] == login_aluno].reset_index()    

            resultados_gerais_disciplina_med_mat = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Matemática'].reset_index(drop = True)
            resultados_gerais_disciplina_med_lin = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Linguagens'].reset_index(drop = True)
            resultados_gerais_disciplina_med_lp = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Língua Portuguesa'].reset_index(drop = True)
            resultados_gerais_disciplina_med_hum = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Ciências Humanas'].reset_index(drop = True)
            resultados_gerais_disciplina_med_nat = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Ciências da Natureza'].reset_index(drop = True)
            resultados_gerais_disciplina_med_ing = resultados_gerais_disciplina5[resultados_gerais_disciplina5['Disciplina'] == 'Inglês'].reset_index(drop = True)

            if len(resultados_ciencias_hum['Disciplina']) == 0:
                    resultados_ciencias_fim = resultados_ciencias_nat.copy()
                    resultados_gerais_disciplina3_fim = resultados_gerais_disciplina3_nat.copy()
                    #classificacao_aluno_fim = classificacao_aluno_nat.copy()
                    resultados_gerais_disciplina_med_cie = resultados_gerais_disciplina_med_nat.copy()
            else:
                    resultados_ciencias_fim = resultados_ciencias_hum.copy()
                    resultados_gerais_disciplina3_fim = resultados_gerais_disciplina3_hum.copy()
                    #classificacao_aluno_fim = classificacao_aluno_hum.copy()
                    resultados_gerais_disciplina_med_cie = resultados_gerais_disciplina_med_hum.copy()

            base_alunos_fizeram['Login do aluno(a)'] = base_alunos_fizeram['Login do aluno(a)'].apply(extract_login)
            matematica_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Matemática']
            matematica_detalhes_media = matematica_detalhes.groupby(['Assunto']).mean(['Acerto']).reset_index()
                
            matematica_aluno = matematica_detalhes[matematica_detalhes['Login do aluno(a)'] == login_aluno]

            matematica_aluno_media = matematica_aluno.groupby('Assunto').mean(['Acerto']).reset_index()
            matematica_aluno_media2 = matematica_aluno.groupby('Assunto').count().reset_index()
            matematica_aluno_media3 = pd.DataFrame()
            matematica_aluno_media3['Assunto'] = matematica_aluno_media2['Assunto']
            matematica_aluno_media3['Número da questão'] = matematica_aluno_media2['Número da questão']

            matematica_tabela = pd.merge(matematica_aluno_media,matematica_detalhes_media, on = 'Assunto', how = 'inner')
            matematica_tabela2 = matematica_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])
            matematica_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
            matematica_tabela2['Resultado Geral'] = ''
            matematica_tabela2['Resultado Individual'] = ''
            for i in range(len(matematica_tabela2['Assunto'])):
                matematica_tabela2['Resultado Geral'][i] = "{0:.0%}".format(matematica_tabela2['Resultado Geral decimal'][i])
                matematica_tabela2['Resultado Individual'][i] = "{0:.0%}".format(matematica_tabela2['Resultado Individual decimal'][i])
            matematica_tabela3 = pd.merge(matematica_tabela2,matematica_aluno_media3, on = 'Assunto', how = 'inner')
            matematica_tabela3.rename(columns = {'Número da questão':'Quantidade de questões'}, inplace = True)
            matematica_tabela3 = matematica_tabela3[['Assunto','Quantidade de questões','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
            matematica_tabela3['Status'] = ''
            for i in range(len(matematica_tabela3['Assunto'])):
                if matematica_tabela3['Resultado Individual decimal'][i] == 0:
                    matematica_tabela3['Status'][i] = "🔴" 
                elif matematica_tabela3['Resultado Individual decimal'][i] >= matematica_tabela3['Resultado Geral decimal'][i]:
                    matematica_tabela3['Status'][i] = "🟢"
                elif matematica_tabela3['Resultado Individual decimal'][i] - matematica_tabela3['Resultado Geral decimal'][i] > - 0.25:
                    matematica_tabela3['Status'][i] = "🟡"
                else:
                    matematica_tabela3['Status'][i] = "🔴"
            matematica_tabela3['Diferença'] = ''
            for i in range(len(matematica_tabela3['Assunto'])):
                matematica_tabela3['Diferença'][i] = matematica_tabela3['Resultado Individual decimal'][i] - matematica_tabela3['Resultado Geral decimal'][i]
                
            matematica_tabela_ordenado = matematica_tabela3.sort_values(by = 'Diferença')

            matematica_tabela_verde = matematica_tabela_ordenado[matematica_tabela_ordenado['Status'] == '🟢']
            matematica_tabela_verde_ordenado = matematica_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)
                
            matematica_tabela_vermelho = matematica_tabela_ordenado[matematica_tabela_ordenado['Status'] == '🔴']
            matematica_tabela_vermelho_ordenado = matematica_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

            if len(resultados_matematica['Nome do aluno(a)']) != 0:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Matemática</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                html_br="""
                <br>
                """

                st.markdown(html_br, unsafe_allow_html=True)            

                #resultados_gerais_disciplina3_mat.drop(columns='level_0', inplace=True)
                resultados_gerais_disciplina3_mat = resultados_gerais_disciplina3_mat.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_mat['Classificação'] = resultados_gerais_disciplina3_mat['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_mat_aluno = resultados_gerais_disciplina3_mat[resultados_gerais_disciplina3_mat['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                if "Insper" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional Insper':

                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Nota na questão'][0]/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_mat_20 = resultados_gerais_disciplina3_mat[resultados_gerais_disciplina3_mat['Fez questão'] > 10]

                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat_20['Nota na questão'].mean()/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat_20['Acerto'].mean(),-1),0)),'Simulado Nacional Insper 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_mat_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_mat['Classificação']))), 0)              

                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                        
                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Nota na questão'][0]/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_mat_10 = resultados_gerais_disciplina3_mat[resultados_gerais_disciplina3_mat['Fez questão'] > 10]

                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat_10['Nota na questão'].mean()/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_mat_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_mat['Classificação']))), 0)              


                if "Simulado 0" in simulado_selecionado:

                    if (turma == 'Esparta 3º' or turma_jazz[0] == 'Esparta 3º 1' or turma_jazz[0] == 'Esparta 3º 2'):

                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Nota na questão'][0]/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Acerto'][0],-1),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Matemática')

                    if (turma == 'Esparta 2º' or turma_jazz[0] == 'Esparta 2º'):

                        cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Nota na questão'][0]/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Acerto'][0],-1),0)),'Esparta 2º', '0', '0', simulado_selecionado[-1]+' Matemática')

                if "Semana 01" in simulado_selecionado:

                    cards_principais(int(round(resultados_matematica['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Nota na questão'][0]/10,-1),0)), int(round(resultados_matematica['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_mat['Acerto'][0],-1),0)),'Semana 01 Matemática', '0', '0', 0)

                if simulado_selecionado == 'Simulado Nacional Insper':

                    criar_histograma_acertos(resultados_gerais_disciplina3_mat, nome_aluno3, 15)

                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_mat, nome_aluno3, 15)

                with st.container():
                    col1, col2, col3 = st.columns([5,0.1,2.5])
                    with col1:
                        tabela_assuntos(matematica_tabela3)
                    with col3:
                        tabela_pontos(matematica_tabela_verde_ordenado, matematica_tabela_vermelho_ordenado)

            if len(resultados_linguagens['Nome do aluno(a)']) != 0:

                linguagens_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Linguagens']

            elif len(resultados_lingua_port['Nome do aluno(a)']) != 0:   

                linguagens_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Língua Portuguesa']     

            if len(resultados_linguagens['Nome do aluno(a)']) != 0 or  len(resultados_lingua_port['Nome do aluno(a)']) != 0:

                linguagens_detalhes_media = linguagens_detalhes.groupby('Assunto').mean(['Acerto']).reset_index()
                linguagens_aluno = linguagens_detalhes[linguagens_detalhes['Login do aluno(a)'] == login_aluno]

                linguagens_aluno_media = linguagens_aluno.groupby('Assunto').mean(['Acerto']).reset_index()
                linguagens_aluno_media2 = linguagens_aluno.groupby('Assunto').count().reset_index()
                linguagens_aluno_media3 = pd.DataFrame()
                linguagens_aluno_media3['Assunto'] = linguagens_aluno_media2['Assunto']
                linguagens_aluno_media3['Número da questão'] = linguagens_aluno_media2['Número da questão']

                linguagens_tabela = pd.merge(linguagens_aluno_media,linguagens_detalhes_media, on = 'Assunto', how = 'inner')
                linguagens_tabela2 = linguagens_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])
                linguagens_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
                linguagens_tabela2['Resultado Geral'] = ''
                linguagens_tabela2['Resultado Individual'] = ''
                for i in range(len(linguagens_tabela2['Assunto'])):
                    linguagens_tabela2['Resultado Geral'][i] = "{0:.0%}".format(linguagens_tabela2['Resultado Geral decimal'][i])
                    linguagens_tabela2['Resultado Individual'][i] = "{0:.0%}".format(linguagens_tabela2['Resultado Individual decimal'][i])
                linguagens_tabela3 = pd.merge(linguagens_tabela2,linguagens_aluno_media3, on = 'Assunto', how = 'inner')
                linguagens_tabela3.rename(columns = {'Número da questão':'Quantidade de questões'}, inplace = True)
                linguagens_tabela3 = linguagens_tabela3[['Assunto','Quantidade de questões','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
                linguagens_tabela3['Status'] = ''
                for i in range(len(linguagens_tabela3['Assunto'])):
                    if linguagens_tabela3['Resultado Individual decimal'][i] == 0:
                        linguagens_tabela3['Status'][i] = "🔴" 
                    elif linguagens_tabela3['Resultado Individual decimal'][i] >= linguagens_tabela3['Resultado Geral decimal'][i]:
                        linguagens_tabela3['Status'][i] = "🟢"
                    elif linguagens_tabela3['Resultado Individual decimal'][i] - linguagens_tabela3['Resultado Geral decimal'][i] > - 0.25:
                        linguagens_tabela3['Status'][i] = "🟡"
                    else:
                        linguagens_tabela3['Status'][i] = "🔴"
                linguagens_tabela3['Diferença'] = ''
                for i in range(len(linguagens_tabela3['Assunto'])):
                    linguagens_tabela3['Diferença'][i] = linguagens_tabela3['Resultado Individual decimal'][i] - linguagens_tabela3['Resultado Geral decimal'][i]

                linguagens_tabela_ordenado = linguagens_tabela3.sort_values(by = 'Diferença')

                linguagens_tabela_verde = linguagens_tabela_ordenado[linguagens_tabela_ordenado['Status'] == '🟢']
                linguagens_tabela_verde_ordenado = linguagens_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)

                linguagens_tabela_vermelho = linguagens_tabela_ordenado[linguagens_tabela_ordenado['Status'] == '🔴']
                linguagens_tabela_vermelho_ordenado = linguagens_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

            if len(resultados_linguagens['Nome do aluno(a)']) != 0:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Linguagens</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                st.markdown(html_br, unsafe_allow_html=True)

                #resultados_gerais_disciplina3_lin.drop(columns='level_0', inplace=True)
                resultados_gerais_disciplina3_lin = resultados_gerais_disciplina3_lin.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_lin['Classificação'] = resultados_gerais_disciplina3_lin['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_lin_aluno = resultados_gerais_disciplina3_lin[resultados_gerais_disciplina3_lin['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                if "Insper" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional Insper':

                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Nota na questão'][0]/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_lin_20 = resultados_gerais_disciplina3_lin[resultados_gerais_disciplina3_lin['Fez questão'] > 10]

                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin_20['Nota na questão'].mean()/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin_20['Acerto'].mean(),-1),0)),'Simulado Nacional Insper 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_lin_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_lin['Classificação']))), 0)      

                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                    
                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Nota na questão'][0]/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_lin_10 = resultados_gerais_disciplina3_lin[resultados_gerais_disciplina3_lin['Fez questão'] > 10]

                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin_10['Nota na questão'].mean()/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_lin_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_lin['Classificação']))), 0)      



                if "Simulado 0" in simulado_selecionado:

                    if (turma == 'Esparta 3º' or turma_jazz[0] == 'Esparta 3º 1' or turma_jazz[0] == 'Esparta 3º 2'):

                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Nota na questão'][0]/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Acerto'][0],-1),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Linguagens')

                    if (turma == 'Esparta 2º' or turma_jazz[0] == 'Esparta 2º'):

                        cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Nota na questão'][0]/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Acerto'][0],-1),0)),'Esparta 2º', '0', '0', simulado_selecionado[-1]+' Linguagens')

                if "Semana 01" in simulado_selecionado:

                    cards_principais(int(round(resultados_linguagens['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Nota na questão'][0]/10,-1),0)), int(round(resultados_linguagens['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lin['Acerto'][0],-1),0)),'Semana 01 Linguagens', '0', '0', 0)

                if simulado_selecionado == 'Simulado Nacional Insper':

                    criar_histograma_acertos(resultados_gerais_disciplina3_lin, nome_aluno3, 15)

                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_lin, nome_aluno3, 15)

            elif len(resultados_lingua_port['Nome do aluno(a)']) != 0:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Língua Portuguesa</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                resultados_gerais_disciplina3_lp = resultados_gerais_disciplina3_lp.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_lp['Classificação'] = resultados_gerais_disciplina3_lp['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_lp_aluno = resultados_gerais_disciplina3_lp[resultados_gerais_disciplina3_lp['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                if "Insper" in simulado_selecionado:

                    cards_principais(int(round(resultados_lingua_port['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lp['Nota na questão'][0]/10,-1),0)), int(round(resultados_lingua_port['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lp['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                    
                        cards_principais(int(round(resultados_lingua_port['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lp['Nota na questão'][0]/10,-1),0)), int(round(resultados_lingua_port['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lp['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_lp_10 = resultados_gerais_disciplina3_lp[resultados_gerais_disciplina3_lp['Fez questão'] > 10]

                        cards_principais(int(round(resultados_lingua_port['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_lp_10['Nota na questão'].mean()/10,-1),0)), int(round(resultados_lingua_port['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_lp_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_lp_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_lp['Classificação']))), 0)      


                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_lp, nome_aluno3, 15)
        

            if len(resultados_linguagens['Nome do aluno(a)']) != 0 or  len(resultados_lingua_port['Nome do aluno(a)']) != 0:

                with st.container():
                        col1, col2, col3 = st.columns([5,0.1,2.5])
                        with col1:
                            tabela_assuntos(linguagens_tabela3)
                        with col3:
                            tabela_pontos(linguagens_tabela_verde_ordenado, linguagens_tabela_vermelho_ordenado)

            ingles_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Inglês']
            ingles_detalhes_media = ingles_detalhes.groupby(['Assunto']).mean(['Acerto']).reset_index()  

            ingles_aluno = ingles_detalhes[ingles_detalhes['Login do aluno(a)'] == login_aluno]

            ingles_aluno_media = ingles_aluno.groupby('Assunto').mean(['Acerto']).reset_index()
            ingles_aluno_media2 = ingles_aluno.groupby('Assunto').count().reset_index()
            ingles_aluno_media3 = pd.DataFrame()
            ingles_aluno_media3['Assunto'] = ingles_aluno_media2['Assunto']
            ingles_aluno_media3['Número da questão'] = ingles_aluno_media2['Número da questão']

            ingles_tabela = pd.merge(ingles_aluno_media,ingles_detalhes_media, on = 'Assunto', how = 'inner')
            ingles_tabela2 = ingles_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])
            ingles_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
            ingles_tabela2['Resultado Geral'] = ''
            ingles_tabela2['Resultado Individual'] = ''
            for i in range(len(ingles_tabela2['Assunto'])):
                ingles_tabela2['Resultado Geral'][i] = "{0:.0%}".format(ingles_tabela2['Resultado Geral decimal'][i])
                ingles_tabela2['Resultado Individual'][i] = "{0:.0%}".format(ingles_tabela2['Resultado Individual decimal'][i])
            ingles_tabela3 = pd.merge(ingles_tabela2,ingles_aluno_media3, on = 'Assunto', how = 'inner')
            ingles_tabela3.rename(columns = {'Número da questão':'Quantidade de questões'}, inplace = True)
            ingles_tabela3 = ingles_tabela3[['Assunto','Quantidade de questões','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
            ingles_tabela3['Status'] = ''
            for i in range(len(ingles_tabela3['Assunto'])):
                if ingles_tabela3['Resultado Individual decimal'][i] == 0:
                    ingles_tabela3['Status'][i] = "🔴" 
                elif ingles_tabela3['Resultado Individual decimal'][i] >= ingles_tabela3['Resultado Geral decimal'][i]:
                    ingles_tabela3['Status'][i] = "🟢"
                elif ingles_tabela3['Resultado Individual decimal'][i] - ingles_tabela3['Resultado Geral decimal'][i] > - 0.25:
                    ingles_tabela3['Status'][i] = "🟡"
                else:
                    ingles_tabela3['Status'][i] = "🔴"
            ingles_tabela3['Diferença'] = ''
            for i in range(len(ingles_tabela3['Assunto'])):
                ingles_tabela3['Diferença'][i] = ingles_tabela3['Resultado Individual decimal'][i] - ingles_tabela3['Resultado Geral decimal'][i]
                
            ingles_tabela_ordenado = ingles_tabela3.sort_values(by = 'Diferença')

            ingles_tabela_verde = ingles_tabela_ordenado[ingles_tabela_ordenado['Status'] == '🟢']
            ingles_tabela_verde_ordenado = ingles_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)
                
            ingles_tabela_vermelho = ingles_tabela_ordenado[ingles_tabela_ordenado['Status'] == '🔴']
            ingles_tabela_vermelho_ordenado = ingles_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

            if len(resultados_ingles['Nome do aluno(a)']) != 0:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Inglês</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                resultados_gerais_disciplina3_ing = resultados_gerais_disciplina3_ing.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_ing['Classificação'] = resultados_gerais_disciplina3_ing['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_ing_aluno = resultados_gerais_disciplina3_ing[resultados_gerais_disciplina3_ing['Login do aluno(a)'] == login_aluno].reset_index(drop = True)
                
                if "Insper" in simulado_selecionado:

                    cards_principais(int(round(resultados_ingles['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_ing['Nota na questão'][0]/10,-1),0)), int(round(resultados_ingles['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_ing['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                    
                        cards_principais(int(round(resultados_ingles['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_ing['Nota na questão'][0]/10,-1),0)), int(round(resultados_ingles['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_ing['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_ing_10 = resultados_gerais_disciplina3_ing[resultados_gerais_disciplina3_ing['Fez questão'] > 10]

                        cards_principais(int(round(resultados_ingles['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_ing_10['Nota na questão'].mean()/10,-1),0)), int(round(resultados_ingles['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_ing_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_ing_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_ing['Classificação']))), 0)      


                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_ing, nome_aluno3, 15)

                with st.container():
                    col1, col2, col3 = st.columns([5,0.1,2.5])
                    with col1:
                        tabela_assuntos(ingles_tabela3)
                    with col3:
                        tabela_pontos(ingles_tabela_verde_ordenado, ingles_tabela_vermelho_ordenado)
            
            if (len(resultados_ciencias_nat['Nome do aluno(a)']) != 0 or 'FGV' in simulado_selecionado):

                ciencias_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Ciências Humanas']

                ciencias_detalhes_media = ciencias_detalhes.groupby('Assunto').mean(['Acerto']).reset_index()

                ciencias_aluno = ciencias_detalhes[ciencias_detalhes['Login do aluno(a)'] == login_aluno]

                ciencias_aluno_media = ciencias_aluno.groupby('Assunto').mean(['Acerto']).reset_index()
                ciencias_aluno_media2 = ciencias_aluno.groupby('Assunto').count().reset_index()
                ciencias_aluno_media3 = pd.DataFrame()
                ciencias_aluno_media3['Assunto'] = ciencias_aluno_media2['Assunto']
                ciencias_aluno_media3['Número da questão'] = ciencias_aluno_media2['Número da questão']

                ciencias_tabela = pd.merge(ciencias_aluno_media,ciencias_detalhes_media, on = 'Assunto', how = 'inner')
                ciencias_tabela2 = ciencias_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])
                    
                ciencias_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
                ciencias_tabela2['Resultado Geral'] = ''
                ciencias_tabela2['Resultado Individual'] = ''
                for i in range(len(ciencias_tabela2['Assunto'])):
                    ciencias_tabela2['Resultado Geral'][i] = "{0:.0%}".format(ciencias_tabela2['Resultado Geral decimal'][i])
                    ciencias_tabela2['Resultado Individual'][i] = "{0:.0%}".format(ciencias_tabela2['Resultado Individual decimal'][i])
                ciencias_tabela3 = pd.merge(ciencias_tabela2,ciencias_aluno_media3, on = 'Assunto', how = 'inner')
                    
                ciencias_tabela3.rename(columns = {'Número da questão':'Quantidade de questões'}, inplace = True)
                ciencias_tabela3 = ciencias_tabela3[['Assunto','Quantidade de questões','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
                ciencias_tabela3['Status'] = ''
                for i in range(len(ciencias_tabela3['Assunto'])):
                    if ciencias_tabela3['Resultado Individual decimal'][i] == 0:
                        ciencias_tabela3['Status'][i] = "🔴" 
                    elif ciencias_tabela3['Resultado Individual decimal'][i] >= ciencias_tabela3['Resultado Geral decimal'][i]:
                        ciencias_tabela3['Status'][i] = "🟢"
                    elif ciencias_tabela3['Resultado Individual decimal'][i] - ciencias_tabela3['Resultado Geral decimal'][i] > - 0.25:
                        ciencias_tabela3['Status'][i] = "🟡"
                    else:
                        ciencias_tabela3['Status'][i] = "🔴"
                ciencias_tabela3['Diferença'] = ''
                for i in range(len(ciencias_tabela3['Assunto'])):
                    ciencias_tabela3['Diferença'][i] = ciencias_tabela3['Resultado Individual decimal'][i] - ciencias_tabela3['Resultado Geral decimal'][i]

                ciencias_tabela_ordenado = ciencias_tabela3.sort_values(by = 'Diferença')

                ciencias_tabela_verde = ciencias_tabela_ordenado[ciencias_tabela_ordenado['Status'] == '🟢']
                ciencias_tabela_verde_ordenado = ciencias_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)

                ciencias_tabela_vermelho = ciencias_tabela_ordenado[ciencias_tabela_ordenado['Status'] == '🔴']
                ciencias_tabela_vermelho_ordenado = ciencias_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

                if simulado_selecionado != 'Simulado Matemática Básica':

                        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Ciências Humanas</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        
                        html_br="""
                            <br>
                            """

                        st.markdown(html_br, unsafe_allow_html=True)

                #resultados_gerais_disciplina3_hum.drop(columns='level_0', inplace=True)
                resultados_gerais_disciplina3_hum = resultados_gerais_disciplina3_hum.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_hum['Classificação'] = resultados_gerais_disciplina3_hum['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_hum_aluno = resultados_gerais_disciplina3_hum[resultados_gerais_disciplina3_hum['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                if "Insper" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional Insper':

                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_hum_20 = resultados_gerais_disciplina3_hum[resultados_gerais_disciplina3_hum['Fez questão'] > 10]

                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum_20['Nota na questão'].mean()/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum_20['Acerto'].mean(),-1),0)),'Simulado Nacional Insper 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_hum_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_hum['Classificação']))), 0)      

                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                    
                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_hum_10 = resultados_gerais_disciplina3_hum[resultados_gerais_disciplina3_hum['Fez questão'] > 10]

                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum_10['Nota na questão'].mean()/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_hum_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_hum['Classificação']))), 0)      


                if "Simulado 0" in simulado_selecionado:

                    if (turma == 'Esparta 3º' or turma_jazz[0] == 'Esparta 3º 1' or turma_jazz[0] == 'Esparta 3º 2'):

                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Acerto'][0],-1),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Humanas')

                    if (turma == 'Esparta 2º' or turma_jazz[0] == 'Esparta 2º'):

                        cards_principais(int(round(resultados_ciencias_hum['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_hum['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_hum['Acerto'][0],-1),0)),'Esparta 2º', '0', '0', simulado_selecionado[-1]+' Humanas')

                if simulado_selecionado == 'Simulado Nacional Insper':

                        criar_histograma_acertos(resultados_gerais_disciplina3_hum, nome_aluno3, 15)

                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_hum, nome_aluno3, 15)

                with st.container():
                    col1, col2, col3 = st.columns([5,0.1,2.5])
                    with col1:
                        tabela_assuntos(ciencias_tabela3)
                    with col3:
                        tabela_pontos(ciencias_tabela_verde_ordenado, ciencias_tabela_vermelho_ordenado)

            
            if (len(resultados_ciencias_hum['Nome do aluno(a)']) != 0 and "Insper" in simulado_selecionado):

                ciencias_detalhes = base_alunos_fizeram[base_alunos_fizeram['Disciplina'] == 'Ciências da Natureza']

                ciencias_detalhes_media = ciencias_detalhes.groupby('Assunto').mean(['Acerto']).reset_index()

                ciencias_aluno = ciencias_detalhes[ciencias_detalhes['Login do aluno(a)'] == login_aluno]

                ciencias_aluno_media = ciencias_aluno.groupby('Assunto').mean(['Acerto']).reset_index()
                ciencias_aluno_media2 = ciencias_aluno.groupby('Assunto').count().reset_index()
                ciencias_aluno_media3 = pd.DataFrame()
                ciencias_aluno_media3['Assunto'] = ciencias_aluno_media2['Assunto']
                ciencias_aluno_media3['Número da questão'] = ciencias_aluno_media2['Número da questão']

                ciencias_tabela = pd.merge(ciencias_aluno_media,ciencias_detalhes_media, on = 'Assunto', how = 'inner')
                ciencias_tabela2 = ciencias_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])

                ciencias_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
                ciencias_tabela2['Resultado Geral'] = ''
                ciencias_tabela2['Resultado Individual'] = ''
                for i in range(len(ciencias_tabela2['Assunto'])):
                    ciencias_tabela2['Resultado Geral'][i] = "{0:.0%}".format(ciencias_tabela2['Resultado Geral decimal'][i])
                    ciencias_tabela2['Resultado Individual'][i] = "{0:.0%}".format(ciencias_tabela2['Resultado Individual decimal'][i])
                ciencias_tabela3 = pd.merge(ciencias_tabela2,ciencias_aluno_media3, on = 'Assunto', how = 'inner')
                    
                ciencias_tabela3.rename(columns = {'Número da questão':'Quantidade de questões'}, inplace = True)
                ciencias_tabela3 = ciencias_tabela3[['Assunto','Quantidade de questões','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
                ciencias_tabela3['Status'] = ''
                for i in range(len(ciencias_tabela3['Assunto'])):
                    if ciencias_tabela3['Resultado Individual decimal'][i] == 0:
                        ciencias_tabela3['Status'][i] = "🔴" 
                    elif ciencias_tabela3['Resultado Individual decimal'][i] >= ciencias_tabela3['Resultado Geral decimal'][i]:
                        ciencias_tabela3['Status'][i] = "🟢"
                    elif ciencias_tabela3['Resultado Individual decimal'][i] - ciencias_tabela3['Resultado Geral decimal'][i] > - 0.25:
                        ciencias_tabela3['Status'][i] = "🟡"
                    else:
                        ciencias_tabela3['Status'][i] = "🔴"
                ciencias_tabela3['Diferença'] = ''
                for i in range(len(ciencias_tabela3['Assunto'])):
                    ciencias_tabela3['Diferença'][i] = ciencias_tabela3['Resultado Individual decimal'][i] - ciencias_tabela3['Resultado Geral decimal'][i]

                ciencias_tabela_ordenado = ciencias_tabela3.sort_values(by = 'Diferença')

                ciencias_tabela_verde = ciencias_tabela_ordenado[ciencias_tabela_ordenado['Status'] == '🟢']
                ciencias_tabela_verde_ordenado = ciencias_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)

                ciencias_tabela_vermelho = ciencias_tabela_ordenado[ciencias_tabela_ordenado['Status'] == '🔴']
                ciencias_tabela_vermelho_ordenado = ciencias_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

                if simulado_selecionado != 'Simulado Matemática Básica':

                        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                        st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Ciências da Natureza</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                        
                        html_br="""
                            <br>
                            """

                        st.markdown(html_br, unsafe_allow_html=True)

                #resultados_gerais_disciplina3_nat.drop(columns='level_0', inplace=True)
                resultados_gerais_disciplina3_nat = resultados_gerais_disciplina3_nat.sort_values(by = 'Acerto', ascending = False)
                resultados_gerais_disciplina3_nat['Classificação'] = resultados_gerais_disciplina3_nat['Acerto'].rank(method='min', ascending=False).astype(int)
                resultados_gerais_disciplina3_nat_aluno = resultados_gerais_disciplina3_nat[resultados_gerais_disciplina3_nat['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                if "Insper" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional Insper':

                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Acerto'][0],-1),0)),'Insper', '0', '0', 0)

                    else:
                        resultados_gerais_disciplina_med_nat_20 = resultados_gerais_disciplina3_nat[resultados_gerais_disciplina3_nat['Fez questão'] > 10]

                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_nat_20['Nota na questão'].mean()/10,-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat_20['Acerto'].mean(),-1),0)),'Simulado Nacional Insper 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_nat_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_nat['Classificação']))), 0)      
                '''
                if "FGV" in simulado_selecionado:

                    if simulado_selecionado != 'Simulado Nacional FGV':
                    
                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Nota na questão'][0],-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Acerto'][0],-1),0)),'FGV', '0', '0', 0)

                    else:

                        resultados_gerais_disciplina_med_nat_10 = resultados_gerais_disciplina3_nat[resultados_gerais_disciplina3_nat['Fez questão'] > 10]

                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat_10['Nota na questão'].mean(),-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat_10['Acerto'].mean(),-1),0)),'Simulado Nacional FGV 1ª fase', str(int(round(truncar(resultados_gerais_disciplina3_nat_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_disciplina3_nat['Classificação']))), 0)      
                '''

                if "Simulado 0" in simulado_selecionado:

                    if (turma == 'Esparta 3º' or turma_jazz[0] == 'Esparta 3º 1' or turma_jazz[0] == 'Esparta 3º 2'):

                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Acerto'][0],-1),0)),'Esparta 3º', '0', '0', simulado_selecionado[-1]+' Humanas')

                    if (turma == 'Esparta 2º' or turma_jazz[0] == 'Esparta 2º'):

                        cards_principais(int(round(resultados_ciencias_nat['Nota na questão'][0]/10,1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Nota na questão'][0]/10,-1),0)), int(round(resultados_ciencias_nat['Acerto'][0],1)), int(round(truncar(resultados_gerais_disciplina_med_nat['Acerto'][0],-1),0)),'Esparta 2º', '0', '0', simulado_selecionado[-1]+' Humanas')

                if simulado_selecionado == 'Simulado Nacional Insper':
                        
                        criar_histograma_acertos(resultados_gerais_disciplina3_nat, nome_aluno3, 15)

                if simulado_selecionado == 'Simulado Nacional FGV':

                    criar_histograma_acertos(resultados_gerais_disciplina3_nat, nome_aluno3, 15)

                with st.container():
                    col1, col2, col3 = st.columns([5,0.1,2.5])
                    with col1:
                        tabela_assuntos(ciencias_tabela3)
                    with col3:
                        tabela_pontos(ciencias_tabela_verde_ordenado, ciencias_tabela_vermelho_ordenado)

     

            
            if (simulado_selecionado[:15] == 'Simulado Insper' or simulado_selecionado[:12] == 'Simulado FGV' or simulado_selecionado[:17] == 'Simulado Nacional'):

                base_redacao['Acerto'] = 0.00
                base_redacao['Login do aluno(a)'] = base_redacao['Login do aluno(a)'].apply(extract_login)

                base_redacao['Nota na questão'] = base_redacao['Nota na questão'].replace('', np.nan)
                base_redacao['Valor da questão'] = base_redacao['Valor da questão'].replace('', np.nan)

                base_redacao['Nota na questão'] = (
                base_redacao['Nota na questão'].str.replace(',', '.', regex=False).astype(float)
                )

                base_redacao['Valor da questão'] = (
                base_redacao['Valor da questão'].str.replace(',', '.', regex=False).astype(float)
                )


                for i in range(len(base_redacao)):
                    base_redacao['Acerto'][i] = base_redacao['Nota na questão'][i]/base_redacao['Valor da questão'][i]
                
                base_redacao2_aux = base_redacao[base_redacao['Nota na questão'] >= 0]
                base_redacao_aux2 = base_redacao[base_redacao['Nota na questão'] > 0]
                    
                base_redacao_aux = base_redacao_aux2[base_redacao_aux2['Simulado'] == simulado_selecionado]
                base_redacao2 = base_redacao2_aux[base_redacao2_aux['Simulado'] == simulado_selecionado]

                redacao_detalhes_media = base_redacao_aux.groupby('Competência').mean(['Acerto']).reset_index()
                    
                redacao_aluno = base_redacao2[base_redacao2['Login do aluno(a)'] == login_aluno]

                redacao_aluno_media = redacao_aluno.groupby('Competência').mean(['Acerto']).reset_index()

                redacao_aluno_media2 = redacao_aluno.groupby('Competência').count().reset_index()

                redacao_aluno_media3 = pd.DataFrame()
                redacao_aluno_media3['Competência'] = redacao_aluno_media2['Competência']
                redacao_aluno_media3['Nota na questão'] = redacao_aluno_media2['Nota na questão']

                redacao_tabela = pd.merge(redacao_aluno_media,redacao_detalhes_media, on = 'Competência', how = 'inner')

                redacao_tabela2 = redacao_tabela.drop(columns = ['Valor da questão_x','Valor da questão_y','Nota na questão_x','Nota na questão_y'])
                redacao_tabela2.rename(columns = {'Acerto_x':'Resultado Individual decimal','Acerto_y':'Resultado Geral decimal'}, inplace = True)
                redacao_tabela2['Resultado Geral'] = ''
                redacao_tabela2['Resultado Individual'] = ''
                    
                for i in range(len(redacao_tabela2['Competência'])):
                    redacao_tabela2['Resultado Geral'][i] = "{0:.0%}".format(redacao_tabela2['Resultado Geral decimal'][i])
                    redacao_tabela2['Resultado Individual'][i] = "{0:.0%}".format(redacao_tabela2['Resultado Individual decimal'][i])
                redacao_tabela3 = pd.merge(redacao_tabela2,redacao_aluno_media3, on = 'Competência', how = 'inner')
                    
                redacao_tabela3 = redacao_tabela3[['Competência','Resultado Individual', 'Resultado Geral','Resultado Individual decimal', 'Resultado Geral decimal']]
                redacao_tabela3['Status'] = ''
                for i in range(len(redacao_tabela3['Competência'])):
                    if redacao_tabela3['Resultado Individual decimal'][i] == 0:
                        redacao_tabela3['Status'][i] = "🔴" 
                    elif redacao_tabela3['Resultado Individual decimal'][i] >= redacao_tabela3['Resultado Geral decimal'][i]:
                        redacao_tabela3['Status'][i] = "🟢"
                    elif redacao_tabela3['Resultado Individual decimal'][i] - redacao_tabela3['Resultado Geral decimal'][i] > - 0.25:
                        redacao_tabela3['Status'][i] = "🟡"
                    else:
                        redacao_tabela3['Status'][i] = "🔴"
                redacao_tabela3['Diferença'] = ''

                for i in range(len(redacao_tabela3['Competência'])):
                    redacao_tabela3['Diferença'][i] = redacao_tabela3['Resultado Individual decimal'][i] - redacao_tabela3['Resultado Geral decimal'][i]
                    
                redacao_tabela_ordenado = redacao_tabela3.sort_values(by = 'Diferença')
                redacao_tabela_ordenado = redacao_tabela_ordenado.dropna()

                redacao_tabela_verde = redacao_tabela_ordenado[redacao_tabela_ordenado['Status'] == '🟢']
                redacao_tabela_verde_ordenado = redacao_tabela_verde.sort_values(by = 'Diferença', ascending = False).reset_index(drop = True)
                    
                redacao_tabela_vermelho = redacao_tabela_ordenado[redacao_tabela_ordenado['Status'] == '🔴']
                redacao_tabela_vermelho_ordenado = redacao_tabela_vermelho.sort_values(by = 'Diferença', ascending = True).reset_index(drop = True)

                base_redacao_disciplina = base_redacao2.groupby(['Login do aluno(a)','Nome do aluno(a)']).sum().reset_index()
                    
                #for i in range(len(base_redacao_disciplina['Login do aluno(a)'])):
                #    if base_redacao_disciplina['Nota na questão'][i] > 0:
                #        base_redacao_disciplina['Nota na questão'][i] = 200 + 0.8*base_redacao_disciplina['Nota na questão'][i]
                #base_redacao_disciplina['Nota na questão'] = 200 + 0.8*base_redacao_disciplina['Nota na questão']

                base_redacao_disciplina2 = base_redacao_disciplina.sort_values(by = 'Nota na questão', ascending = False).reset_index()

                for i in range(len(redacao_aluno_media['Nota na questão'])):
                    if redacao_aluno_media['Nota na questão'][i] == 0:
                        redacao_aluno_media['Nota na questão'][i] = 0

                if len(redacao_tabela3['Status']) != 0:

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Redação</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    base_redacao3 = base_redacao2.groupby(['Login do aluno(a)','Nome do aluno(a)','Estratégia']).sum().reset_index()
                    #for i in range(len(base_redacao3['Nota na questão'])):
                    #    if base_redacao3['Nota na questão'][i] > 0:
                    #        base_redacao3['Nota na questão'][i] = 200 + 0.8*base_redacao3['Nota na questão'][i]
                    base_redacao4 = base_redacao3[base_redacao3['Login do aluno(a)'] == login_aluno]
                    base_redacao3aux = base_redacao3[base_redacao3['Nota na questão'] > 0]

                    base_redacao5 = base_redacao3aux['Nota na questão'].mean()

                    resultados_gerais_redacao = base_redacao3.sort_values(by = 'Nota na questão', ascending = False)
                    resultados_gerais_redacao['Classificação'] = resultados_gerais_redacao['Nota na questão'].rank(method='min', ascending=False).astype(int)
                    resultados_gerais_redacao_aluno = resultados_gerais_redacao[resultados_gerais_redacao['Login do aluno(a)'] == login_aluno].reset_index(drop = True)

                    if "Insper" in simulado_selecionado:

                        if simulado_selecionado != 'Simulado Nacional Insper':

                            cards_principais(int(round(redacao_aluno_media['Nota na questão'].sum(),1)), int(100*round(redacao_tabela3['Resultado Geral decimal'].mean(),2)), 0, 0, 'Insper', '0', '0', 0)
                        else:

                            cards_principais(int(round(redacao_aluno_media['Nota na questão'].sum(),1)), int(100*round(redacao_tabela3['Resultado Geral decimal'].mean(),2))-1, 0, 0, 'Simulado Nacional Insper 1ª fase', str(int(round(truncar(resultados_gerais_redacao_aluno['Classificação'][0],-1),0)))+"º", str(int(len(resultados_gerais_redacao['Classificação']))), 0)              

                    if "FGV" in simulado_selecionado:
        
                        cards_principais(int(round(redacao_aluno_media['Nota na questão'].sum(),1)), int(round(redacao_tabela3['Resultado Geral decimal'].mean(),0)), 0, 0, 'FGV', '0', '0', 0)

                    if simulado_selecionado == 'Simulado Nacional Insper':
                        
                        criar_histograma_acertos(resultados_gerais_redacao, nome_aluno3, 100.01)

                    redacao_tabela3 = redacao_tabela3.dropna()

                    with st.container():
                            col1, col2, col3 = st.columns([5,0.1,2.5])
                            with col1:
                                tabela_competencias(redacao_tabela3)
                            with col3:
                                tabela_pontos(redacao_tabela_verde_ordenado, redacao_tabela_vermelho_ordenado)

            if len(resultados_matematica['Nome do aluno(a)']) != 0:

                tabela_detalhes_aux = base.copy()

                #if permissao != 'Inscrito Simulado Nacional':

                #    tabela_detalhes_aux = tabela_detalhes_aux.drop(columns = ['level_0']) ###

                

                tabela_detalhes = tabela_detalhes_aux[tabela_detalhes_aux['Simulado'] == simulado_selecionado].reset_index()
 
                tabela_detalhes['Login do aluno(a)'] = tabela_detalhes['Login do aluno(a)'].apply(extract_login)

                tabela_detalhes_fizeram = tabela_detalhes[tabela_detalhes['Nome do aluno(a)'].isin(alunos_fizeram['Nome do aluno(a)'])].reset_index(drop = True)

                tabela_detalhes_aluno = tabela_detalhes[tabela_detalhes['Login do aluno(a)'] == login_aluno]

                tabela_detalhes_aluno2 = tabela_detalhes_aluno.drop(columns = ['Nota na questão','Valor da questão','Nome do aluno(a)','Login do aluno(a)','Certo ou errado'])
                tabela_detalhes_media = tabela_detalhes_fizeram.groupby(['Número da questão','Assunto']).mean(['Acerto']).reset_index()
                tabela_detalhes_media2 = tabela_detalhes_media.drop(columns = ['Nota na questão','Valor da questão'])

                tabela_detalhes_aluno3 = pd.merge(tabela_detalhes_aluno2, tabela_detalhes_media2, on = ['Número da questão','Assunto'], how = 'inner')

                tabela_detalhes_aluno5 = tabela_detalhes_aluno3.drop(columns = ['Nome da avaliação','Turma'])
                tabela_detalhes_aluno4 = tabela_detalhes_aluno5.sort_values(by = 'Número da questão', ascending = True).reset_index()

                tabela_detalhes_aluno4 = tabela_detalhes_aluno4[['Número da questão','Disciplina','Assunto','Acerto_x','Acerto_y','Gabarito']]
                tabela_detalhes_aluno4.rename(columns = {'Disciplina':'Área do conhecimento','Acerto_x':'Resultado Individual','Acerto_y':'Resultado Geral','Tempo na questão_x':'Tempo na questão','Tempo na questão_y':'Média geral'}, inplace = True)
                    
                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                    """
                                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                        <strong>Detalhamento por questão objetiva</strong>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                    
                html_br="""
                    <br>
                    """

                st.markdown(html_br, unsafe_allow_html=True)

                with st.container():
                    col1, col2, col3 = st.columns([0.55,5,1])

                    with col1:
                        st.write('')
                    with col2:
                        tabela_questoes(tabela_detalhes_aluno4)
                    with col3:
                        st.write('')


            if (turma_aluno['Turma'].isin(['Economia']).any() or turma_aluno['Turma'].isin(['Administração']).any() or turma_aluno['Turma'].isin(['Direito']).any()):

                base_resultados_disc_fgv = ler_planilha("1dwbt5wTCV1Dj0pukwCZDy4i6p6E3_bTYzDwNHFXfmV0", "Todos | Discursivas | FGV!A1:Q22000")

                base_resultados_disc_fgv.rename(columns = {'atividade_nome':'Nome da avaliação','turma':'Turma','aluno_nome':'Nome do aluno(a)','aluno_login':'Login do aluno(a)','num_exercicio':'Número da questão','resp_aluno':'Resposta do aluno(a)','gabarito':'Gabarito','nota':'Nota','tempo_no_exercicio(s)':'Tempo na questão','valor_do_exercicio':'Valor da questão','frente':'Frente'}, inplace = True)

                base_resultados_disc_fgv2 = base_resultados_disc_fgv.copy()

                base_resultados_disc_fgv2['Resposta do aluno(a)'] = base_resultados_disc_fgv2['Resposta do aluno(a)'].fillna('x')

                base_resultados_disc_fgv2['Valor da questão'] = base_resultados_disc_fgv2['Valor da questão'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")))

                #base_resultados_disc_fgv2 ['Acerto'] = 0.00
                #base_resultados_disc_fgv2 ['Nota na questão'] = 0.00
                base_resultados_disc_fgv2['Novo Nota na questão'] = base_resultados_disc_fgv2['Nota'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")))
                base_resultados_disc_fgv2['Novo Valor da questão'] = base_resultados_disc_fgv2['Valor da questão']

                #base_resultados_disc_fgv2 ['Acerto'] = np.where((base_resultados_disc_fgv2 ['Certo ou errado'] == 'certo') & (base_resultados_disc_fgv2 ['Número da questão'] != 61), 1, 0)
                #base_resultados_disc_fgv2 ['Novo Nota na questão'] = base_resultados_disc_fgv2 ['Acerto'] * base_resultados_disc_fgv2 ['Novo Valor da questão']
                #base_resultados_disc_fgv2 ['Nota na questão'] = base_resultados_disc_fgv2 ['Acerto'] * base_resultados_disc_fgv2 ['Valor da questão']

                resultados_gerais_disc = base_resultados_disc_fgv2.groupby(['Nome da avaliação','Turma','Nome do aluno(a)','Login do aluno(a)','Simulado','Área']).sum().reset_index()

                resultados_gerais_disc2 = resultados_gerais_disc.groupby(['Turma','Nome do aluno(a)','Login do aluno(a)','Simulado','Área']).sum().reset_index()

                resultados_gerais_disc2_aux = resultados_gerais_disc2.copy()

                #for i in range(len(resultados_gerais_disc2_aux['Login do aluno(a)'])):
                #    resultados_gerais_disc2_aux['Nota na questão'][i] = 1.25*resultados_gerais_disc2_aux['Nota na questão'][i]
                #    resultados_gerais2_aux['Novo Nota na questão'][i] = 1.25*resultados_gerais_disc2_aux['Novo Nota na questão'][i]

                resultados_gerais_disc3 = resultados_gerais_disc2_aux.sort_values(by = 'Novo Nota na questão', ascending = False).reset_index(drop = True)


                resultados_gerais_disc_aluno1 = resultados_gerais_disc3[resultados_gerais_disc3['Nome do aluno(a)'] == nome_aluno3['Nome do aluno(a)'][0]]
                resultados_gerais_disc_aluno = resultados_gerais_disc_aluno1[resultados_gerais_disc_aluno1['Simulado'] == simulado_selecionado].reset_index()

                resultados_gerais_disc4 = resultados_gerais_disc3[resultados_gerais_disc3['Novo Nota na questão'] > 0]

                resultados_gerais_disc4_aux = resultados_gerais_disc4[['Login do aluno(a)','Valor da questão','Simulado', 'Novo Nota na questão','Área']]
                resultados_gerais_disc5_aux = resultados_gerais_disc4_aux.copy()
                resultados_gerais_disc5 = resultados_gerais_disc5_aux[resultados_gerais_disc5_aux['Simulado'] == simulado_selecionado].reset_index() 

                alunos_fizeram_disc = pd.DataFrame()
                resultados_gerais_disc4_aux2 = resultados_gerais_disc4[resultados_gerais_disc4['Simulado'] == simulado_selecionado].reset_index()

                alunos_fizeram_disc['Nome do aluno(a)'] = resultados_gerais_disc4_aux2['Nome do aluno(a)']

                tabela_detalhes_disc_aux = base_resultados_disc_fgv2.copy()
                
                tabela_detalhes_disc = tabela_detalhes_disc_aux[tabela_detalhes_disc_aux['Simulado'] == simulado_selecionado].reset_index()


                tabela_detalhes_disc['Login do aluno(a)'] = tabela_detalhes_disc['Login do aluno(a)'].apply(extract_login)

                tabela_detalhes_disc_fizeram = tabela_detalhes_disc[tabela_detalhes_disc['Nome do aluno(a)'].isin(alunos_fizeram_disc['Nome do aluno(a)'])].reset_index(drop = True)
                tabela_detalhes_disc_fizeram['Novo Nota na questão'] = tabela_detalhes_disc_fizeram['Novo Nota na questão']/tabela_detalhes_disc_fizeram['Valor da questão']


                tabela_detalhes_disc_aluno = tabela_detalhes_disc[tabela_detalhes_disc['Login do aluno(a)'] == login_aluno]
                tabela_detalhes_disc_aluno['Novo Nota na questão'] = tabela_detalhes_disc_aluno['Novo Nota na questão']/tabela_detalhes_disc_aluno['Valor da questão']
                tabela_detalhes_disc_aluno2 = tabela_detalhes_disc_aluno.drop(columns = ['Valor da questão','Nome do aluno(a)','Login do aluno(a)'])
                tabela_detalhes_disc_media = tabela_detalhes_disc_fizeram.groupby(['Número da questão','Assunto','ID']).mean(['Novo Nota na questão']).reset_index()
                tabela_detalhes_disc_media2 = tabela_detalhes_disc_media#.drop(columns = ['Valor da questão'])

                tabela_detalhes_disc_aluno3 = pd.merge(tabela_detalhes_disc_aluno2, tabela_detalhes_disc_media2, on = ['Número da questão','Assunto','ID'], how = 'inner')

                tabela_detalhes_disc_aluno5 = tabela_detalhes_disc_aluno3.drop(columns = ['Nome da avaliação','Turma'])
                tabela_detalhes_disc_aluno4 = tabela_detalhes_disc_aluno5.sort_values(by = 'Número da questão', ascending = True).reset_index()
                tabela_detalhes_disc_aluno4 = tabela_detalhes_disc_aluno4[['Número da questão','Área','Assunto','Resposta do aluno(a)','Gabarito','Novo Nota na questão_x','Novo Nota na questão_y']]
                tabela_detalhes_disc_aluno4.rename(columns = {'Área':'Área do conhecimento','Novo Nota na questão_x':'Resultado Individual','Novo Nota na questão_y':'Resultado Geral','Tempo na questão_x':'Tempo na questão','Tempo na questão_y':'Média geral'}, inplace = True)

                if (turma_aluno['Turma'].isin(['Administração']).any() or turma_aluno['Turma'].isin(['Economia']).any()):

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                """
                                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                    <strong>Matemática Discursiva</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    resultados_gerais_disc_aluno2 = resultados_gerais_disc_aluno[resultados_gerais_disc_aluno['Área'] == 'Matemática'].reset_index(drop = True)
                    resultados_gerais_disc6 = resultados_gerais_disc5[resultados_gerais_disc5['Área'] == 'Matemática'].reset_index(drop = True)

                    cards_principais(int(round(resultados_gerais_disc_aluno2['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disc6['Novo Nota na questão'].mean(),-1))), 0, 0,'FGV Disc Matemática', '0', '0', 0)

                    st.markdown(html_br, unsafe_allow_html=True)

                    tabela_detalhes_disc_aluno5 = tabela_detalhes_disc_aluno4[tabela_detalhes_disc_aluno4['Área do conhecimento'] == 'Matemática'].reset_index(drop = True)

                    with st.container():
                        col1, col2, col3 = st.columns([0.55,5,1])

                        with col1:
                            st.write('')
                        with col2:
                            tabela_questoes(tabela_detalhes_disc_aluno5)
                        with col3:
                            st.write('')

                if (turma_aluno['Turma'].isin(['Direito']).any() or turma_aluno['Turma'].isin(['Economia']).any()):

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                """
                                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                    <strong>Língua Portuguesa Discursiva</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    resultados_gerais_disc_aluno2 = resultados_gerais_disc_aluno[resultados_gerais_disc_aluno['Área'] == 'Língua Portuguesa'].reset_index(drop = True)
                    resultados_gerais_disc6 = resultados_gerais_disc5[resultados_gerais_disc5['Área'] == 'Língua Portuguesa'].reset_index(drop = True)
                    
                    cards_principais(int(round(resultados_gerais_disc_aluno2['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disc6['Novo Nota na questão'].mean(),-1))), 0, 0,'FGV Disc Língua Portuguesa', '0', '0', 0)

                    st.markdown(html_br, unsafe_allow_html=True)

                    tabela_detalhes_disc_aluno5 = tabela_detalhes_disc_aluno4[tabela_detalhes_disc_aluno4['Área do conhecimento'] == 'Língua Portuguesa'].reset_index(drop = True)

                    with st.container():
                        col1, col2, col3 = st.columns([0.55,5,1])

                        with col1:
                            st.write('')
                        with col2:
                            tabela_questoes(tabela_detalhes_disc_aluno5)
                        with col3:
                            st.write('')

                if turma_aluno['Turma'].isin(['Direito']).any():

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                """
                                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                    <strong>Ciências Humanas Discursiva</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    resultados_gerais_disc_aluno2 = resultados_gerais_disc_aluno[resultados_gerais_disc_aluno['Área'] == 'Ciências Humanas'].reset_index(drop = True)
                    resultados_gerais_disc6 = resultados_gerais_disc5[resultados_gerais_disc5['Área'] == 'Ciências Humanas'].reset_index(drop = True)

                    cards_principais(int(round(resultados_gerais_disc_aluno2['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disc6['Novo Nota na questão'].mean(),-1))), 0, 0,'FGV Disc Ciências Humanas', '0', '0', 0)

                    st.markdown(html_br, unsafe_allow_html=True)

                    tabela_detalhes_disc_aluno5 = tabela_detalhes_disc_aluno4[tabela_detalhes_disc_aluno4['Área do conhecimento'] == 'Ciências Humanas'].reset_index(drop = True)

                    with st.container():
                        col1, col2, col3 = st.columns([0.55,5,1])

                        with col1:
                            st.write('')
                        with col2:
                            tabela_questoes(tabela_detalhes_disc_aluno5)
                        with col3:
                            st.write('')

                    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                    st.markdown(
                                """
                                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                    <strong>Artes e Questões Contemporâneas Discursiva</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    resultados_gerais_disc_aluno2 = resultados_gerais_disc_aluno[resultados_gerais_disc_aluno['Área'] == 'Artes e Questões Contemporâneas'].reset_index(drop = True)
                    resultados_gerais_disc6 = resultados_gerais_disc5[resultados_gerais_disc5['Área'] == 'Artes e Questões Contemporâneas'].reset_index(drop = True)

                    cards_principais(int(round(resultados_gerais_disc_aluno2['Novo Nota na questão'][0],1)), int(round(truncar(resultados_gerais_disc6['Novo Nota na questão'].mean(),-1))), 0, 0,'FGV Disc Artes e QC', '0', '0', 0)

                    st.markdown(html_br, unsafe_allow_html=True)

                    tabela_detalhes_disc_aluno5 = tabela_detalhes_disc_aluno4[tabela_detalhes_disc_aluno4['Área do conhecimento'] == 'Artes e Questões Contemporâneas'].reset_index(drop = True)

                    with st.container():
                        col1, col2, col3 = st.columns([0.55,5,1])

                        with col1:
                            st.write('')
                        with col2:
                            tabela_questoes(tabela_detalhes_disc_aluno5)
                        with col3:
                            st.write('')

        else:

            progress_bar.progress(1.00)
            percentage_text.text("100%")

            st.write('')
            st.write('')
            st.write('')

            if permissao == 'Aluno':

                st.warning("🚨 **Atenção!** 🚨\n\nVocê ainda não realizou esse simulado de 1ª fase ainda! Caso já tenha sido feito há mais de 24h, entre em contato com Padre!")

            elif (permissao == 'Mentor' or permissao == 'Administrador'):

                st.warning("🚨 **Atenção!** 🚨\n\nO(A) aluno(a) ainda não realizou esse simulado de 1ª fase!")   

            else:

                st.warning("🚨 **Atenção!** 🚨\n\nEnvie uma mensagem para Alexandre para você poder fazer o simulado de 1ª fase Insper!")                                


            