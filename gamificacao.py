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
from logs import escrever_planilha, escrever_planilha_pontos
import datetime
import pytz

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

def define_estado():
    return {
        'pagina_atual': 'Gamificação'
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

def card_principal(pontuacao_aluno, pontuacao_media, nivel_aluno2):

    with st.container():
            col1, col2, col3, col4, col5 = st.columns([1,3,1,3,1])
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
                        <strong>Pontos</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                            <strong>{pontuacao_aluno}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                    f"""
                    <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                        <strong>Média: {pontuacao_media}</strong>
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
                            <strong>Fase</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

                st.markdown(
                            f"""
                            <div style="background-color: white; color: #9E089E; padding: 0px; border-top-left-radius: 0px; border-top-right-radius: 0px; text-align: center; font-size: 36px; margin-bottom: 10px;">
                                <strong>{nivel_aluno2}</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown('<div style="height: 2px;"></div>', unsafe_allow_html=True)

                st.markdown(
                        f"""
                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center;  margin-top: -10px;">
                            <strong>-</strong>
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

def definir_nivel(pontuacao, pont_nivel12, pont_nivel23, pont_nivel34, pont_nivel45, pont_nivel56, pont_nivel67):
    if pontuacao == 0:
        #return "Nível 1"
        return "1ª | Exploration"
    elif pontuacao < pont_nivel12:
        #return "Nível 1"
        return "1ª | Exploration"
    elif pontuacao < pont_nivel23:
        #return "Nível 2"
        return "2ª | Discovery"
    elif pontuacao < pont_nivel34:
        #return "Nível 3"
        return "3ª | Action"
    elif pontuacao < pont_nivel45:
        #return "Nível 4"
        return "4ª | Confrontation"
    elif pontuacao < pont_nivel56:
        #return "Nível 5"
        return "5ª | Resilience"
    elif pontuacao < pont_nivel67:
        #return "Nível 6"
        return "6ª | Experience"
    else:
        #return "Nível 7"
        return "7ª | Final Battle"

def progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, id_bar, pont_niveis_menor, pont_niveis_maior):

    #prox_nivel = int(nivel_aluno[-1]) + 1

    if id_bar == 1:
        atual =  "Exploration"
        proximo = "Discovery"
    elif id_bar == 2:
        atual = "Discovery"
        proximo = "Action"
    elif id_bar == 3:
        atual = "Action"
        proximo = "Confrontation"
    elif id_bar == 4:
        atual = "Confrontation"
        proximo = "Resilience"
    elif id_bar == 5:
        atual = "Resilience"
        proximo = "Experience"
    elif id_bar == 6:
        atual = "Experience"
        proximo = "Final Battle"
    elif id_bar == 7:
        atual = "Final Battle"
        proximo = ""

    with st.container():

        col1, col2, col3 = st.columns([1,3,1])

        with col1:
            mensagem_html_principal = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: left">
                <p style="font-size: 24px; color: #333; margin: 0;">Fase <strong style="color: #9E089E;">{atual}</strong></p>
            </div>
            """

            mensagem_html_principal2 = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: left">
                <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">{pont_niveis_menor}</strong></p>
            </div>
            """

            st.markdown(mensagem_html_principal, unsafe_allow_html=True)

            if progress > 0:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

            if progress == 0 and pont_niveis_maior == 400:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

        with col3:
            mensagem_html_principal = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: right">
                <p style="font-size: 24px; color: #333; margin: 0;">Fase <strong style="color: #9E089E;">{proximo}</strong></p>
            </div>
            """

            mensagem_html_principal2 = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 0px; text-align: right">
                <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">{pont_niveis_maior}</strong></p>
            </div>
            """

            st.markdown(mensagem_html_principal, unsafe_allow_html=True)

            if progress > 0:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

            if progress == 0 and pont_niveis_maior == 400:

                st.markdown(mensagem_html_principal2, unsafe_allow_html=True)

    if progress != 0 and progress != 1:

        progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: #9E089E; height: 45px; border-radius: 8px;"></div>
            </div>
            """
        mensagem_html = f"""
        <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
            <p style="font-size: 16px; color: #333; margin: 0;">Faltam <strong style="color: #9E089E;">{pontos_para_proximo_nivel}</strong> pontos para você alcançar a Fase <strong style="color: #9E089E;">{proximo}</strong>!</p>
        </div>
        """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)
        
    elif progress == 0:
        
        if nivel_aluno == 'Nível 1' and pont_niveis_maior == 400:

            progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: #9E089E; height: 45px; border-radius: 8px;"></div>
            </div>
            """

            mensagem_html = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Faltam <strong style="color: #9E089E;">{pontos_para_proximo_nivel}</strong> pontos para você alcançar a Fase <strong style="color: #9E089E;">{proximo}</strong>!</p>
            </div>
            """

    
        else:

            progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #cccccc; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: rgba(158, 8, 158, 0.8); height: 35px; border-radius: 8px;"></div>
            </div>
            """

            mensagem_html = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Alcance a Fase <strong style="color: #9E089E;">{atual}</strong> para avançar rumo a Fase <strong style="color: #9E089E;">{proximo}!</p>
            </div>
            """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)
        
    else: 

        progress_bar_html_nivel = f"""
            <div style="width: 100%; background-color: #f0f2f6; border-radius: 8px;">
                <div style="width: {100*progress}%; background-color: rgba(158, 8, 158, 0.8); height: 35px; border-radius: 8px;"></div>
            </div>
            """
        
        mensagem_html = f"""
        <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
            <p style="font-size: 16px; color: #333; margin: 0;">Você já alcançou a Fase <strong style="color: #9E089E;">{proximo}</strong>! Parabéns!!</p>
        </div>
        """
        
        st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

        st.markdown(mensagem_html, unsafe_allow_html=True)

        if proximo == 'Discovery':

            html_br="""
            <br>
            """

            #st.markdown(html_br, unsafe_allow_html=True)

            mensagem_html_contato_breve = f"""
            <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                <p style="font-size: 16px; color: #333; margin: 0;">Entraremos em contato com você em breve!!</p>
            </div>
            """

            #st.markdown(mensagem_html_contato_breve, unsafe_allow_html=True)

def esferas_bar(esfera, pont_normalizado_aluno, pont_normalizado_media):

    if pont_normalizado_aluno < pont_normalizado_media - 0.25:
        cor_barra = "rgba(255, 165, 0, 0.6)"  # Laranja com opacidade
    elif pont_normalizado_aluno < pont_normalizado_media:
        cor_barra = "rgba(255, 255, 0, 0.6)"  # Amarela com opacidade
    elif pont_normalizado_aluno > pont_normalizado_media + 0.25:
        cor_barra = "rgba(0, 0, 255, 0.6)"  # Azul com opacidade
    else:
        cor_barra = "rgba(0, 128, 0, 0.6)"  # Verde com opacidade

    # HTML da barra de progresso com linha vertical preta para a média
    progress_bar_html_nivel = f"""
    <div style="position: relative; width: 100%; background-color: #cccccc; border-radius: 8px;">
        <div style="width: {100*pont_normalizado_aluno}%; background-color: {cor_barra}; height: 35px; border-radius: 8px;"></div>
        <div style="position: absolute; left: {100*pont_normalizado_media}%; top: 0; bottom: 0; width: 2px; background-color: #000000;">
            <div style="position: absolute; top: -20px; left: -10px; transform: translateX(-50%); color: #000000; font-size: 12px; font-weight: bold;">Média</div>
        </div>
    </div>
    """

    st.markdown(progress_bar_html_nivel, unsafe_allow_html=True)

def create_radar_chart(original_categories, values, medias, nome_selecionado):
    original_to_new_categories = {
        'Pontuação_Presença_Aulas_Normalizada': 'Presença nas aulas',
        'Pontuação_Presença_Mentoria_Normalizada': 'Presença nas mentorias',
        'Pontuação_Presença_Simulado_Normalizada': 'Presença nos simulados',
        'Pontuação_Engajamento_Plataforma_Normalizada': 'Engajamento na plataforma',
        'Pontuação_Duvida_Monitoria_Normalizada': 'Dúvidas na monitoria',
        'Pontuação_Nota_Simulado_Normalizada': 'Nota nos simulados'
    }

    # Convertendo as categorias originais para os novos nomes
    categories = [original_to_new_categories[cat] for cat in original_categories]
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + values[:1],
        theta=categories + categories[:1],
        fill='toself',
        fillcolor='rgba(158, 8, 158, 0.4)',  # Cor de preenchimento com opacidade
        line=dict(color='rgba(158, 8, 158, 0.8)', width=2),
        name=nome_selecionado
    ))

    fig.add_trace(go.Scatterpolar(
        r=medias + medias[:1],
        theta=categories + categories[:1],
        fill='toself',
        fillcolor='rgba(255,167,62, 0.4)',  # Cor de preenchimento com opacidade
        line=dict(color='rgba(255,167,62, 0.8)', width=2),
        name='Média'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
    )

    st.plotly_chart(fig)

def tabela_pontuacoes(gamificacao, nome_selecionado):

    with st.container():
        col1, col2, col3 = st.columns([1.15,4,1]) 

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
                            <th style="width: 300px; min-width: 300px; max-width: 300px; text-align: center; border-top-left-radius: 10px;border-right: 1px solid rgba(158, 8, 158, 0.8);border-left: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Aluno(a)</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Turma</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center;border-right: 1px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8);">Fase</th>
                            <th style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-top-right-radius: 10px;border-right: 0px solid rgba(158, 8, 158, 0.8);border-top: 0px solid rgba(158, 8, 158, 0.8)">Pontuação</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
    
            st.markdown("<table style='width:100%;'>", unsafe_allow_html=True)

            for _, row in gamificacao.iterrows():
                if row['Nome do aluno(a)'] == nome_selecionado:
                    background_color = 'rgba(158, 8, 158, 0.5)'
                    font_color = '#FFFFFF'
                else: 
                    background_color = 'rgba(255, 255, 255, 1)'
                    font_color = '#000000'

                st.markdown(f"""
                    <tr style="text-align: center; background-color: {background_color}; color: {font_color};">
                        <td style="width: 300px; min-width: 300px; max-width: 300px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nome do aluno(a)']}</td>
                        <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Turma']}</td>
                        <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Nível']}</td>
                        <td style="width: 150px; min-width: 150px; max-width: 150px; text-align: center; border-bottom: 1px solid #FFFFFF; padding: 10px; height: 40px; border-left: 1px solid white; border-right: 1px solid white;">{row['Pontuação selecionada']}</td>
                    </tr>
                    """, unsafe_allow_html=True)                    

def grafico_pontuacao_semanal(gamificacao, nome_selecionado, esferas_selecionadas):

    gamificacao_aluno = gamificacao[gamificacao['Nome do aluno(a)'] == nome_selecionado]

    # Calculando a média de pontuação por semana
    media_por_semana = gamificacao.groupby(['Nome do aluno(a)', 'Semana'])['Pontuação'].sum().groupby('Semana').mean().reset_index()
    media_por_semana['Pontuação'] = media_por_semana['Pontuação'].round(2)

    # Obtendo as esferas únicas
    if len(esferas_selecionadas) == 0:

        esferas_unicas = gamificacao['Esfera'].unique()

    else:

        esferas_unicas = esferas_selecionadas

    cores_esferas = {
    "Presença nas aulas de 1ª fase": "rgba(0, 128, 255, 0.9)",   # Um tom de azul claro
    "Presença nas aulas de 2ª fase": "rgba(128, 255, 0, 0.9)",   # Um tom de verde claro
    "Presença nas mentorias": "rgba(255, 153, 51, 0.9)",         # Um tom de laranja suave
    "Presença nos simulados": "rgba(102, 51, 153, 0.9)",         # Um tom de roxo suave
    "Nota nos simulados": "rgba(255, 77, 77, 0.9)",              # Um tom de vermelho claro
    "Dúvidas na monitoria": "rgba(255, 255, 204, 0.9)",          # Um tom de amarelo bem suave
    "Engajamento na plataforma": "rgba(191, 191, 255, 0.9)",     # Um tom de azul/lilás suave
}

    # Criando o gráfico
    fig = go.Figure()

    # Adicionando as barras empilhadas para cada esfera
    for esfera in esferas_unicas:
        pontuacao_por_semana = gamificacao_aluno[gamificacao_aluno['Esfera'] == esfera].groupby('Semana')['Pontuação'].sum().reset_index()
        fig.add_trace(go.Bar(
            x=pontuacao_por_semana['Semana'],
            y=pontuacao_por_semana['Pontuação'],
            name=esfera,
            marker_color=cores_esferas.get(esfera, 'gray')  # Define a cor ou usa cinza como padrão
        ))

    # Adicionando a linha da média
    #fig.add_trace(go.Scatter(
    #    x=media_por_semana['Semana'],
    #    y=media_por_semana['Pontuação'],
    #    mode='lines+markers',
    #    name='Média Geral',
    #    line=dict(color='red', width=2),
    #))

    # Atualizando layout
    fig.update_layout(
        #title='Pontuação por Semana',
        xaxis_title='Semana',
        yaxis_title='Pontuação',
        barmode='stack',  # Para empilhar as colunas
        legend=dict(
            orientation='h',  # Horizontal
            yanchor='bottom',
            y=1.1,
            xanchor='center',
            x=0.5
        ),
        #width=1000,  # Largura do gráfico (ajuste conforme necessário)
        #height=500  # Altura do gráfico (ajuste conforme necessário)
    )

    st.plotly_chart(fig, use_container_width=True)  # O gráfico usará toda a largura do container

def mostrar_gamificacao(nome, permissao, email, turma):

    import time
    start_time = time.time()

    estado = get_estado()

    st.markdown('<style>td { border-right: none !important; }</style>', unsafe_allow_html=True)

    alunos = ler_planilha("16IN1TyqZ2YXYRivDMPPZGspo5FpsGG53ZzWIk_07xLg", "Streamlit | Alunos!A1:E")

    st.write(turmas)
    st.write(turma)
    st.dataframe(alunos)

    if (turma is None or turma == "-"):
            alunos = alunos

            turmas = st.selectbox('Selecione a turma:', ['Extensivo','Esparta'])

            if turmas == 'Extensivo':
                alunos = alunos[~alunos['Turma'].str.contains("Esparta")]
            if turmas == 'Esparta':
                alunos = alunos[alunos['Turma'].str.contains("Esparta")]

    elif "Esparta 2º" in turma:
            turmas = 'Esparta 2º'
            alunos = alunos[alunos['Turma'].str.contains("Esparta 2º")]
    elif "Esparta 3º" in turma:
            turmas = 'Esparta 3º'
            alunos = alunos[alunos['Turma'].str.contains("Esparta 3º")]
    else:
            turmas = 'Extensivo'
            alunos = alunos[~alunos['Turma'].str.contains("Esparta")]

    alunos['Nome'] = alunos['Nome'].fillna('').astype(str)
    alunos = alunos[alunos['Nome'] != '']
    alunos.rename(columns = {'Nome':'Nome do aluno(a)'}, inplace = True)

    progress = st.progress(0)
    percentage_text = st.empty()

    def update_progress(value):
        progress.progress(value)
        percentage_text.text(f"{round((value))}%")

    if (permissao == 'Aluno' or permissao == 'Responsável'):

        nome_selecionado = nome
    
    else:

        nomes_alunos = ["Escolha o(a) aluno(a)"] + sorted(alunos['Nome do aluno(a)'].unique())

        nome_selecionado = st.selectbox('Selecione um(a) aluno(a):', nomes_alunos)

        if nome_selecionado == 'Escolha o(a) aluno(a)':

            update_progress(100)
            st.warning("Por favor, escolha um(a) aluno(a)!")
            st.stop()

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "", nome_selecionado, email]]
        escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")

    end_time = time.time()
    elapsed_time = end_time - start_time

    presenca_aulasMT = ler_planilha("1aEYh7UtI9CDyfIQBij4Q6m8p9MmtH-MjZZgdKRW9F1k", "Streamlit | Presença nas aulas | Manhã + Tarde!A1:R")
    #presenca_aulasMT1 = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Presença nas aulas | Manhã + Tarde 1!A1:R")

    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(10)

    presenca_aulasE3 = ler_planilha("1EDQdQqTrwAWxjUKvXbiOYPFhvNnKFiaS8DGm6hAVvF4", "Streamlit | Presença nas aulas | Esparta 3º!A1:R")
    #presenca_aulasT2 = ler_planilha("1qV-TL1B26Xhrmg7w5JkO6RPRSlaD3Li3saeBRtQZJD0", "Streamlit | Presença nas aulas | Tarde 2!A1:R")
    #presenca_aulasT2 = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Presença nas aulas | Tarde 2!A1:R")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(20)

    presenca_aulasE2N = ler_planilha("1bLUt5GVLDidmUnYN_ZbxdKQL5vsYeJep4lJDEoWayOk", "Streamlit | Presença nas aulas | Esparta 2º + Natureza!A1:R")
    #presenca_aulasNT1 = ler_planilha("10ocwUa69s-3c_FMpNMWq6CRooGooa0-9K19rFwm8oEo", "Streamlit | Presença nas aulas | Tarde 1 (Nat)!A1:R")
    #presenca_aulasNT1 = ler_planilha("1rq83WLY5Wy6jZMtf54oB2wfhibq_6MywEcVV9SK60oI", "Streamlit | Presença nas aulas | Tarde 1 (Nat)!A1:R")

    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(30)

    engajamento_plataforma = ler_planilha("1GiTWn1ImitItvUh17HIdQ1afkA9TDFEExifCPDzvDSw", "Streamlit | Engajamento na plataforma!A1:J")

    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(40)
    
    presenca_aulas_aux2 = pd.concat([presenca_aulasE3, presenca_aulasMT], axis=0)
    presenca_aulas_aux = pd.concat([presenca_aulas_aux2, presenca_aulasE2N], axis=0)
    #presenca_aulas_aux = presenca_aulasMT
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(50)
    
    presenca_aulas = presenca_aulas_aux
    #presenca_aulas = pd.concat([presenca_aulas_aux, presenca_aulasNT1], axis=0)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(60)

    presenca_mentoria = ler_planilha("1QL4YDiH5U__uES-Pz-ShiCH-fhz81HZdtpT_NR6nEEY", "Streamlit | Presença na mentoria!A1:F")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(70)

    presenca_nota_simulado = ler_planilha("1-han5cwytzetPhBqd3AHvLrJsYW0eiwv5FwA5s8Pibo", "Streamlit | Presença + Notas simulado!A1:R")

    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(80)

    duvidas_monitoria = ler_planilha("1nif344ZmxDUAeiV_DBHJEzLb5Ctavv9VYPz3r2DSxRs", "Streamlit | Monitoria!A1:O")
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    update_progress(90)
    
    presenca_aulas_2fase = ler_planilha("1da_mnC8ycK8DtITuektoBRg6ne-_GkAK8Imsn1vdrsc", "Streamlit | Presença nas aulas | 2ª fase!A1:G10000")

    engajamento_plataforma['Pontuação_Engajamento_Plataforma'] = engajamento_plataforma['Pontuação'].fillna(0).astype(int)
    presenca_aulas['Pontuação_Presença_Aulas'] = presenca_aulas['Pontuação'].fillna(0).astype(int)
    presenca_aulas = presenca_aulas[presenca_aulas['Pontuação_Presença_Aulas'] > 0]
    presenca_mentoria['Pontuação_Presença_Mentoria'] = presenca_mentoria['Pontuação'].fillna(0).astype(int)
    presenca_nota_simulado['Pontuação_Presença_Simulado'] = presenca_nota_simulado['Pontuação Presença'].fillna(0).astype(int)
    presenca_nota_simulado['Pontuação_Nota_Simulado'] = presenca_nota_simulado['Pontuação Nota'].fillna(0).astype(int)
    duvidas_monitoria['Pontuação_Duvidas_Monitoria'] = duvidas_monitoria['Pontuação'].fillna(0).astype(int)
    presenca_aulas_2fase['Pontuação_Presença_2Fase'] = presenca_aulas_2fase['Pontuação'].fillna(0).astype(int)
    
    #engajamento_plataforma = engajamento_plataforma[engajamento_plataforma['Pontuação_Engajamento_Plataforma'] > 0]
    engajamento_plataforma['Data de conclusão'] = pd.to_datetime(engajamento_plataforma['Data de conclusão'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    engajamento_plataforma['Semana'] = engajamento_plataforma['Data de conclusão'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)
    engajamento_plataforma['Semana'] = engajamento_plataforma['Semana'] - 31 ## Ajuste
    presenca_aulas['Data de conclusão'] = pd.to_datetime(presenca_aulas['Data'], format='%d/%m/%Y', errors='coerce')
    presenca_aulas['Semana'] = presenca_aulas['Data de conclusão'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)
    presenca_aulas['Semana'] = presenca_aulas['Semana'] - 31 ## Ajuste
    presenca_mentoria['Data de conclusão'] = pd.to_datetime(presenca_mentoria['Data'], format='%d/%m/%Y', errors='coerce')
    presenca_mentoria['Semana'] = presenca_mentoria['Data de conclusão'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)
    presenca_mentoria['Semana'] = presenca_mentoria['Semana'] - 31 ## Ajuste
    #presenca_nota_simulado = presenca_nota_simulado[presenca_nota_simulado['Pontuação_Presença_Simulado'] > 0]
    presenca_nota_simulado['Data de conclusão'] = presenca_nota_simulado['Data de conclusão'].str.replace(r'\s+', ' ', regex=True).str.strip()
    presenca_nota_simulado['Data de conclusão 2'] = pd.to_datetime(presenca_nota_simulado['Data de conclusão'], errors='coerce',infer_datetime_format=True)
    presenca_nota_simulado['Semana'] = presenca_nota_simulado['Data de conclusão 2'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) and x != '' else None)
    presenca_nota_simulado['Semana'] = presenca_nota_simulado['Semana'] - 31 ## Ajuste
    duvidas_monitoria['Data de conclusão'] = duvidas_monitoria['Data'].str.replace(r', às', ' ', regex=True).str.strip()
    duvidas_monitoria['Data de conclusão'] = pd.to_datetime(duvidas_monitoria['Data de conclusão'], format='%d/%m/%Y %H:%M:%S',errors='coerce')
    duvidas_monitoria['Semana'] = duvidas_monitoria['Data de conclusão'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)
    duvidas_monitoria['Semana'] = duvidas_monitoria['Semana'] - 31
    presenca_aulas_2fase['Data de conclusão'] = pd.to_datetime(presenca_aulas_2fase['Data'], format='%d/%m/%Y', errors='coerce')
    presenca_aulas_2fase['Semana'] = presenca_aulas_2fase['Data de conclusão'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)
    presenca_aulas_2fase['Semana'] = presenca_aulas_2fase['Semana'] - 31 ## Ajuste
    engajamento_plataforma_semana = engajamento_plataforma.groupby(['Nome do aluno(a)', 'Turma','Semana']).agg({'Pontuação_Engajamento_Plataforma': 'sum'}).reset_index()
    engajamento_plataforma_semana['Esfera'] = 'Engajamento na plataforma'
    engajamento_plataforma_semana.rename(columns = {'Pontuação_Engajamento_Plataforma':'Pontuação'}, inplace = True)
    presenca_aulas_semana = presenca_aulas.groupby(['Nome do aluno(a)', 'Turma','Semana']).agg({'Pontuação_Presença_Aulas': 'sum'}).reset_index()
    presenca_aulas_semana['Esfera'] = 'Presença nas aulas de 1ª fase'
    presenca_aulas_semana.rename(columns = {'Pontuação_Presença_Aulas':'Pontuação'}, inplace = True)
    presenca_mentoria_semana = presenca_mentoria.groupby(['Nome do aluno(a)','Turma','Semana']).agg({'Pontuação_Presença_Mentoria': 'sum'}).reset_index()
    presenca_mentoria_semana['Esfera'] = 'Presença nas mentorias'
    presenca_mentoria_semana.rename(columns = {'Pontuação_Presença_Mentoria':'Pontuação'}, inplace = True)
    presenca_nota_simulado_semana = presenca_nota_simulado.groupby(['Nome do aluno(a)','Turma','Semana']).agg({'Pontuação_Nota_Simulado': 'sum','Pontuação_Presença_Simulado':'sum'}).reset_index()
    nota_simulado_semana = presenca_nota_simulado_semana.drop(columns = ['Pontuação_Presença_Simulado'])
    presenca_simulado_semana = presenca_nota_simulado_semana.drop(columns = ['Pontuação_Nota_Simulado'])
    nota_simulado_semana ['Esfera'] = 'Nota nos simulados'
    presenca_simulado_semana ['Esfera'] = 'Presença nos simulados'
    nota_simulado_semana.rename(columns = {'Pontuação_Nota_Simulado':'Pontuação'}, inplace = True)
    presenca_simulado_semana.rename(columns = {'Pontuação_Presença_Simulado':'Pontuação'}, inplace = True)
    duvidas_monitoria_semana = duvidas_monitoria.groupby(['Nome do aluno(a)','Turma','Semana']).agg({'Pontuação_Duvidas_Monitoria': 'sum'}).reset_index()
    duvidas_monitoria_semana['Esfera'] = 'Dúvidas na monitoria'
    duvidas_monitoria_semana.rename(columns = {'Pontuação_Duvidas_Monitoria':'Pontuação'}, inplace = True)
    presenca_aulas_2fase_semana = presenca_aulas_2fase.groupby(['Nome do aluno(a)','Turma','Semana']).agg({'Pontuação_Presença_2Fase': 'sum'}).reset_index()
    presenca_aulas_2fase_semana['Esfera'] = 'Presença nas aulas de 2ª fase'
    presenca_aulas_2fase_semana.rename(columns = {'Pontuação_Presença_2Fase':'Pontuação'}, inplace = True)

    gamificacao_semana1 = pd.concat([presenca_aulas_semana, presenca_aulas_2fase_semana], axis=0)
    gamificacao_semana2 = pd.concat([gamificacao_semana1, presenca_mentoria_semana], axis=0)
    gamificacao_semana3 = pd.concat([gamificacao_semana2, presenca_simulado_semana], axis=0)
    gamificacao_semana4 = pd.concat([gamificacao_semana3, nota_simulado_semana], axis=0)
    gamificacao_semana5 = pd.concat([gamificacao_semana4, duvidas_monitoria_semana], axis=0)
    gamificacao_semana6 = pd.concat([gamificacao_semana5, engajamento_plataforma_semana], axis=0)

    gamificacao_semana6 = gamificacao_semana6[gamificacao_semana6['Semana'] > 0]

    data_to_write0 = [gamificacao_semana6.columns.tolist()] + gamificacao_semana6.values.tolist()  # Inclui cabeçalhos

    escrever_planilha_pontos("1U5afhbKyxWuIUSh4-ZyLY5gpZullJOreuKvxsIfWUt0", data_to_write0, "Pontuação Semanal")
    
    #engajamento_plataforma2 = engajamento_plataforma.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    engajamento_plataforma2 = engajamento_plataforma.groupby(['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Engajamento_Plataforma': 'sum'}).reset_index()
    #presenca_aulas2 = presenca_aulas.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_aulas2 = presenca_aulas.groupby(['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Presença_Aulas': 'sum'}).reset_index()
    #presenca_mentoria2 = presenca_mentoria.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_mentoria2 = presenca_mentoria.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Presença_Mentoria': 'sum'}).reset_index()
    #presenca_nota_simulado2 = presenca_nota_simulado.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    presenca_nota_simulado2 = presenca_nota_simulado.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Nota_Simulado': 'sum','Pontuação_Presença_Simulado':'sum'}).reset_index()
    #duvidas_monitoria2 = duvidas_monitoria.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
    duvidas_monitoria2 = duvidas_monitoria.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Duvidas_Monitoria': 'sum'}).reset_index()

    presenca_aulas_2fase2 = presenca_aulas_2fase.groupby(['Nome do aluno(a)','Turma']).agg({'Pontuação_Presença_2Fase': 'sum'}).reset_index()

    if nome_selecionado == 'Escolha o(a) aluno(a)':

        end_time = time.time()
        elapsed_time = end_time - start_time
        update_progress(100)

    if nome_selecionado != "Escolha o(a) aluno(a)":

        #engajamento_plataforma_aluno = engajamento_plataforma[engajamento_plataforma['Nome do aluno(a)'] == nome_selecionado]
        #presenca_aulas_aluno = presenca_aulas[presenca_aulas['Nome do aluno(a)'] == nome_selecionado]
        #presenca_mentoria_aluno = presenca_mentoria[presenca_mentoria['Nome do aluno(a)'] == nome_selecionado]
        #presenca_nota_simulado_aluno = presenca_nota_simulado[presenca_nota_simulado['Nome do aluno(a)'] == nome_selecionado]
        #duvidas_monitoria_aluno = duvidas_monitoria[duvidas_monitoria['Nome do aluno(a)'] == nome_selecionado]
        #presenca_aulas_2fase_aluno = presenca_aulas_2fase[presenca_aulas_2fase['Nome do aluno(a)'] == nome_selecionado]

        #engajamento_plataforma_aluno2 = engajamento_plataforma_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        #presenca_aulas_aluno2 = presenca_aulas_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        #presenca_mentoria_aluno2 = presenca_mentoria_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        #presenca_nota_simulado_aluno2 = presenca_nota_simulado_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        #duvidas_monitoria_aluno2 = duvidas_monitoria_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()
        #presenca_aulas_2fase_aluno2 = presenca_aulas_2fase_aluno.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()

        gamificacao = pd.merge(alunos, presenca_aulas2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao1 = pd.merge(gamificacao, engajamento_plataforma2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao2 = pd.merge(gamificacao1, presenca_mentoria2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao4 = pd.merge(gamificacao2, presenca_nota_simulado2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao4 = pd.merge(gamificacao4, presenca_aulas_2fase2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao_final = pd.merge(gamificacao4, duvidas_monitoria2, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao_final.fillna(0, inplace=True)

        gamificacao_final['Pontuação_Engajamento_Plataforma'] = gamificacao_final['Pontuação_Engajamento_Plataforma'].astype(int)
        gamificacao_final['Pontuação_Presença_Aulas'] = gamificacao_final['Pontuação_Presença_Aulas'].astype(int)
        gamificacao_final['Pontuação_Presença_Mentoria'] = gamificacao_final['Pontuação_Presença_Mentoria'].astype(int)
        gamificacao_final['Pontuação_Presença_Simulado'] = gamificacao_final['Pontuação_Presença_Simulado'].astype(int)
        gamificacao_final['Pontuação_Nota_Simulado'] = gamificacao_final['Pontuação_Nota_Simulado'].astype(int)
        gamificacao_final['Pontuação_Duvidas_Monitoria'] = gamificacao_final['Pontuação_Duvidas_Monitoria'].astype(int)
        gamificacao_final['Pontuação_Presença_2Fase'] = gamificacao_final['Pontuação_Presença_2Fase'].astype(int)

        gamificacao_final['Pontuação'] = (
                gamificacao_final['Pontuação_Engajamento_Plataforma'] +
                gamificacao_final['Pontuação_Presença_Aulas'] +
                gamificacao_final['Pontuação_Presença_Mentoria'] + 
                gamificacao_final['Pontuação_Presença_Simulado'] + 
                gamificacao_final['Pontuação_Nota_Simulado'] +
                gamificacao_final['Pontuação_Duvidas_Monitoria'] +
                gamificacao_final['Pontuação_Presença_2Fase']
            )
        
        #gamificacao_final['Pontuação_Engajamento_Plataforma_Normalizada'] = gamificacao_final['Pontuação_Engajamento_Plataforma'] / gamificacao_final['Pontuação_Engajamento_Plataforma'].max()
        #gamificacao_final['Pontuação_Presença_Aulas_Normalizada'] = (gamificacao_final['Pontuação_Presença_Aulas'] + gamificacao_final['Pontuação_Presença_2Fase'])  / (gamificacao_final['Pontuação_Presença_Aulas'].max() + gamificacao_final['Pontuação_Presença_2Fase'].max())
        #gamificacao2['Pontuação_Presença_Mentoria_Normalizada'] = gamificacao2['Pontuação_Presença_Mentoria'] / gamificacao2['Pontuação_Presença_Mentoria'].max()    

        gamificacao_final['Pontuação_Engajamento_Plataforma_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Engajamento_Plataforma'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Engajamento_Plataforma'] / gamificacao_final['Pontuação_Engajamento_Plataforma'].max()
        )

        gamificacao_final['Pontuação_Presença_Aulas_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Presença_Aulas'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Presença_Aulas'] / gamificacao_final['Pontuação_Presença_Aulas'].max()
        )
        
        gamificacao_final['Pontuação_Presença_Mentoria_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Presença_Mentoria'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Presença_Mentoria'] / gamificacao_final['Pontuação_Presença_Mentoria'].max()
        )

        gamificacao_final['Pontuação_Presença_Simulado_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Presença_Simulado'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Presença_Simulado'] / gamificacao_final['Pontuação_Presença_Simulado'].max()
        )

        gamificacao_final['Pontuação_Nota_Simulado_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Nota_Simulado'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Nota_Simulado'] / gamificacao_final['Pontuação_Nota_Simulado'].max() 
        )

        gamificacao_final['Pontuação_Duvidas_Monitoria_Normalizada'] = np.where(
            gamificacao_final['Pontuação_Duvidas_Monitoria'].max() == 0, 
            0, 
            gamificacao_final['Pontuação_Duvidas_Monitoria'] / gamificacao_final['Pontuação_Duvidas_Monitoria'].max()
        )       

        gamificacao3 = gamificacao_final.sort_values(by = 'Pontuação', ascending = False)

        #gamificacao3 = gamificacao3[gamificacao3['Pontuação'] >= 0]

        #pont_niveis = [400, 1000, 1900, 2800, 3700, 5000]
        if turmas == 'Extensivo':
            #pont_niveis = [600, 1300, 2200, 3200, 4300, 5600]
            pont_niveis = [600, 1300, 2200, 3400, 4700, 7200]
        if (turmas == 'Esparta 2º' or turmas == 'Esparta 3º' or turmas == 'Esparta'):
            pont_niveis = [400, 800, 1300, 2000, 2600, 3400]

        gamificacao3['Nível'] = gamificacao3['Pontuação'].apply(definir_nivel, args=(pont_niveis[0], pont_niveis[1], pont_niveis[2], pont_niveis[3], pont_niveis[4], pont_niveis[5]))

        data_to_write = [gamificacao3.columns.tolist()] + gamificacao3.values.tolist()  # Inclui cabeçalhos

        if turmas == 'Extensivo':

            escrever_planilha_pontos("1U5afhbKyxWuIUSh4-ZyLY5gpZullJOreuKvxsIfWUt0", data_to_write, "Pontuação Extensivo")

        if turmas == 'Esparta':

            escrever_planilha_pontos("1U5afhbKyxWuIUSh4-ZyLY5gpZullJOreuKvxsIfWUt0", data_to_write, "Pontuação Esparta")

        gamificacao3_aluno = gamificacao3[gamificacao3['Nome do aluno(a)'] == nome_selecionado].reset_index(drop = True)

        #gamificacao3_medias = gamificacao3.drop(columns=['Nome do aluno(a)', 'Turma']).mean().reset_index()
        gamificacao3_medias = gamificacao3.drop(columns=['Nome do aluno(a)', 'Turma']).agg({'Pontuação_Engajamento_Plataforma': 'mean','Pontuação_Presença_Aulas': 'mean','Pontuação_Presença_Simulado': 'mean','Pontuação_Nota_Simulado': 'mean','Pontuação_Duvidas_Monitoria': 'mean','Pontuação_Presença_2Fase': 'mean'}).reset_index()
        
        gamificacao3_medias.columns = ['Métrica', 'Média']

        pontuacao_aluno = gamificacao3_aluno['Pontuação'][0]

        pontuacao_media = gamificacao3['Pontuação'].mean().round(0).astype(int)

        nivel_aluno = gamificacao3_aluno['Nível'][0]
        nivel_aluno2 = int(nivel_aluno[0])

        st.markdown('<div style="height: 0px;"></div>', unsafe_allow_html=True)

        end_time = time.time()
        elapsed_time = end_time - start_time
        update_progress(100)

        #with st.container():
        
        #    col1, col2, col3 = st.columns([2,4,2])

        #    with col2:

        #       st.markdown(
        #                                f"""
        #                                <div style="background-color: #9E089E; color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; text-align: center; font-size: 45px;">
        #                                    <strong>{nome_selecionado.upper()}</strong>
        #                                </div>
        #                                """,
        #                                unsafe_allow_html=True
        #                            )

        html_br="""
            <br>
            """

        #st.markdown(html_br, unsafe_allow_html=True)
        #st.markdown(html_br, unsafe_allow_html=True)

        card_principal(pontuacao_aluno, pontuacao_media, nivel_aluno)

        with st.container():

            col1, col2, col3 = st.columns([0.001,10,0.001])

            with col2:

                st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

                st.markdown(
                                        """
                                        <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                            <strong>Pontuação semanal por esfera</strong>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                html_br="""
                        <br>
                        """

                st.markdown(html_br, unsafe_allow_html=True)

                esferas_unicas = sorted(gamificacao_semana6['Esfera'].unique())

                esferas_selecionadas = st.multiselect('Selecione a(s) esfera(s)', esferas_unicas)

                data_hoje_brasilia, hora_atual_brasilia = dia_hora()
                esferas_selecionadas_str = ", ".join(esferas_selecionadas)

                if esferas_selecionadas_str != '':
                    data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "Esferas Gráfico " + esferas_selecionadas_str, nome_selecionado, email]]
                    escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")

                grafico_pontuacao_semanal(gamificacao_semana6, nome_selecionado, esferas_selecionadas)

        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Progressão de Fase</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        
        #st.markdown(html_br, unsafe_allow_html=True)
        st.markdown(html_br, unsafe_allow_html=True)

        if int(nivel_aluno2) < (len(pont_niveis) + 1):
            pontos_para_proximo_nivel = pont_niveis[int(nivel_aluno2)-1] - pontuacao_aluno
        else:
            pontos_para_proximo_nivel = 0

        if nivel_aluno == '1ª | Exploration':

            progress = pontuacao_aluno / pont_niveis[0]
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '2ª | Discovery':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[0])  / (pont_niveis[1] - pont_niveis[0])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])  
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '3ª | Action':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[1])  / (pont_niveis[2] - pont_niveis[1])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '4ª | Confrontation':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[2])  / (pont_niveis[3] - pont_niveis[2])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            #st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '5ª | Resilience':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[3])  / (pont_niveis[4] - pont_niveis[3])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(0, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '6ª | Experience':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress = (pontuacao_aluno - pont_niveis[4])  / (pont_niveis[5] - pont_niveis[4])
            progress_bar(progress, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        if nivel_aluno == '7ª | Final Battle':   

            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 1, 0, pont_niveis[0])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 2, pont_niveis[0], pont_niveis[1])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 3, pont_niveis[1], pont_niveis[2])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 4, pont_niveis[2], pont_niveis[3])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 5, pont_niveis[3], pont_niveis[4])
            st.markdown(html_br, unsafe_allow_html=True)
            progress_bar(1, nivel_aluno, pontos_para_proximo_nivel, 6, pont_niveis[4], pont_niveis[5])

        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        st.markdown(
                            """
                            <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                <strong>Resultados por esfera</strong>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        st.markdown(html_br, unsafe_allow_html=True)
        st.markdown(html_br, unsafe_allow_html=True)

        with st.container():

            col1, col2, col3, col4, col5, col6, col7 = st.columns([1,10,1,10,1,10,1])

            with col2:

                mensagem_html_pres_aulas = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nas aulas</strong></p>
                </div>
                """
                st.markdown(mensagem_html_pres_aulas, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença nas aulas', gamificacao3_aluno['Pontuação_Presença_Aulas_Normalizada'][0], (100*gamificacao3['Pontuação_Presença_Aulas_Normalizada'].mean()).round(0).astype(int)/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_eng_plataforma = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Engajamento na plataforma</strong></p>
                </div>
                """
                st.markdown(mensagem_html_eng_plataforma, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Engajamento na plataforma', gamificacao3_aluno['Pontuação_Engajamento_Plataforma_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Engajamento_Plataforma_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

            with col4:

                mensagem_html_pres_mentorias = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nas mentorias</strong></p>
                </div>
                """
                st.markdown(mensagem_html_pres_mentorias, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença na mentoria', gamificacao3_aluno['Pontuação_Presença_Mentoria_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Presença_Mentoria_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_duvida_monitoria = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Dúvidas na monitoria</strong></p>
                </div>
                """
                st.markdown(mensagem_html_duvida_monitoria, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Dúvidas na monitoria', gamificacao3_aluno['Pontuação_Duvidas_Monitoria_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Duvidas_Monitoria_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

            with col6:

                mensagem_html_presenca_simulado = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Presença nos simulados</strong></p>
                </div>
                """
                st.markdown(mensagem_html_presenca_simulado, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Presença no simulado', gamificacao3_aluno['Pontuação_Presença_Simulado_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Presença_Simulado_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                mensagem_html_nota_simulado = f"""
                <div style="width: 100%; background-color: #ffffff; border-radius: 8px; padding: 10px;">
                    <p style="font-size: 16px; color: #333; margin: 0;"><strong style="color: #9E089E;">Nota nos simulados</strong></p>
                </div>
                """
                st.markdown(mensagem_html_nota_simulado, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)
                esferas_bar('Nota no simulado', gamificacao3_aluno['Pontuação_Nota_Simulado_Normalizada'][0], int(round((100*gamificacao3['Pontuação_Nota_Simulado_Normalizada'].fillna(0).mean()),0))/100)
                st.markdown(html_br, unsafe_allow_html=True)
                st.markdown(html_br, unsafe_allow_html=True)

        #gamificacao2['Pontuação_Engajamento_Plataforma_Normalizada'] = gamificacao2['Pontuação_Engajamento_Plataforma'] / gamificacao2['Pontuação_Engajamento_Plataforma'].max()
        #gamificacao2['Pontuação_Presença_Aulas_Normalizada'] = gamificacao2['Pontuação_Presença_Aulas'] / gamificacao2['Pontuação_Presença_Aulas'].max() 
        #gamificacao2['Pontuação_Presença_Mentoria_Normalizada'] = gamificacao2['Pontuação_Presença_Mentoria'] / gamificacao2['Pontuação_Presença_Mentoria'].max()    
        

        with st.container():

            col1, col2, col3 = st.columns([2,7,1])

            with col2: 

                categories = ['Pontuação_Engajamento_Plataforma_Normalizada', 'Pontuação_Presença_Aulas_Normalizada', 'Pontuação_Presença_Mentoria_Normalizada', 'Pontuação_Presença_Simulado_Normalizada', 'Pontuação_Nota_Simulado_Normalizada', 'Pontuação_Duvidas_Monitoria_Normalizada']
                #values = gamificacao3_aluno[categories].values.flatten().tolist()
                #medias = gamificacao3_medias.set_index('Métrica').loc[categories]['Média'].tolist()
                #create_radar_chart(categories, values, medias, nome_selecionado)

                gamificacao3_medias = gamificacao3_medias.set_index('Métrica')

                # Verifique se todas as categorias estão no índice
                if all(cat in gamificacao3_medias.index for cat in categories):
                    medias = gamificacao3_medias.loc[categories, 'Média'].tolist()

        st.markdown(
                                """
                                <div style="background-color: rgba(158, 8, 158, 0.8); color: white; padding: 10px; border-top-left-radius: 10px; border-top-right-radius: 10px; text-align: center; font-size: 24px;">
                                    <strong>Tabela de resultados</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
        
        html_br="""
                <br>
                """

        st.markdown(html_br, unsafe_allow_html=True)

        semanas_disponiveis = gamificacao_semana6['Semana'].unique()

        semanas_selecionadas = st.slider(
            'Selecione o intervalo de semanas',
            min_value=int(min(semanas_disponiveis)),
            max_value=max(int(max(semanas_disponiveis)), 2),
            value=(int(min(semanas_disponiveis)), max(int(max(semanas_disponiveis)), 2))
        )

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        semanas_selecionadas_str = ", ".join(map(str, semanas_selecionadas))

        min_semanas_disponiveis = int(min(semanas_disponiveis))
        max_semanas_disponiveis = max(int(max(semanas_disponiveis)), 2)

        if not (semanas_selecionadas[0] == min_semanas_disponiveis and semanas_selecionadas[1] == max_semanas_disponiveis):

            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "Semanas Tabela " + semanas_selecionadas_str, nome_selecionado, email]]
            escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")

        esferas_unicas = sorted(gamificacao_semana6['Esfera'].unique())

        esferas_selecionadas = st.multiselect('Selecione a(s) esfera(s)', esferas_unicas, key='esferas_selecionadas')

        data_hoje_brasilia, hora_atual_brasilia = dia_hora()
        esferas_selecionadas_str = ", ".join(esferas_selecionadas)

        if esferas_selecionadas_str != '':
            data_to_write = [[nome, permissao, data_hoje_brasilia, hora_atual_brasilia, get_estado()['pagina_atual'], "Esferas Tabela " + esferas_selecionadas_str, nome_selecionado, email]]
            escrever_planilha("1BFEw2OJ6wP_mULNBTHi13Rc-4LDBgscUIKiTKwVmQxU", data_to_write, "Logs | 2S25")
    
        if len(esferas_selecionadas) == 0:

            esferas_unicas = gamificacao_semana6['Esfera'].unique()

        else:

            esferas_unicas = esferas_selecionadas

        semana_inicial, semana_final = semanas_selecionadas
        gamificacao_semana7 = gamificacao_semana6[
            (gamificacao_semana6['Semana'] >= semana_inicial) & 
            (gamificacao_semana6['Semana'] <= semana_final)
        ] 

        gamificacao_semana7_aux = gamificacao_semana7[gamificacao_semana7['Esfera'].isin(esferas_unicas)].reset_index(drop = True)

        gamificacao_semana8 = gamificacao_semana7_aux.groupby(['Nome do aluno(a)','Turma']).sum().reset_index()

        gamificacao_semana9 = pd.merge(gamificacao3, gamificacao_semana8, on = ['Nome do aluno(a)','Turma'], how = 'left')
        gamificacao_semana9.rename(columns = {'Pontuação_y':'Pontuação selecionada'}, inplace = True)
        gamificacao_semana9['Pontuação selecionada'] = gamificacao_semana9['Pontuação selecionada'].fillna(0).astype(int)
        gamificacao_semana10 = gamificacao_semana9.sort_values(by = 'Pontuação selecionada', ascending = False)
        
        st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True)

        tabela_pontuacoes(gamificacao_semana10, nome_selecionado)

