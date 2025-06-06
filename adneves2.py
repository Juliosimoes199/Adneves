import requests
import json
import google.generativeai as genai
import asyncio
import streamlit as st
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService # Para protótipo, usar persistente em prod
from google.adk.runners import Runner
from google.genai import types
import os
import warnings
import logging
import dotenv
# --- Configurações Iniciais ---
dotenv.load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key) # osapi vm




def registar_paciente(numero_identificacao:str, nome_completo:str, data_nascimento:str, contacto_telefonico:str, id_sexo:int):
    """
    Regista um novo paciente na unidade hospitalar.
    Args:
        numero_identificacao (str): O numero de bilhete do paciente.
        nome_completo (str): O nome completo do paciente.
        data_nascimento (str): A data de nascimento do paciente (ex: 1990-01-01).
        contacto_telefonico (int): O contacto telefonico do paciente.
        id_sexo (int): O ID do sexo do paciente (1 para masculino, 2 para feminino).

    Returns:
        dict: O JSON da resposta se o login for bem-sucedido e as informações do novo paciente como o id e um dicionário de mais algumas informações uteis, Erro caso contrário.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": "mlisa@gmail.com",
        "senha": "mli2025"
    }

    try:
        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/pacients"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        data = {
            "numero_identificacao": numero_identificacao,
            "nome_completo": nome_completo,
            "data_nascimento": data_nascimento,
            "contacto_telefonico": contacto_telefonico,
            "id_sexo": id_sexo
        }
        requisicao = requests.post(url_acesso, headers=headers, json=data)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
def criar_agendamento(id_paciente:str, id_tipo_exame:int, data_agendamento:str, hora_agendamento:str):
    """
    Faz uma requisição de login para a URL fornecida com as credenciais.

    Args:
        id_paciente (str): O ID do paciente.
        id_tipo_exame (int): O ID do tipo de exame(ex: 1 para Covide-19, 2 para Hepatite B...).
        data_agendamento (str): A data do agendamento no formato 'YYYY-MM-DD'.
        hora_agendamento (str): A hora do agendamento no formato 'HH:MM'.

    Returns:
        dict: retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": "mlisa@gmail.com",
        "senha": "mli2025"
    }

    try:

        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/schedulings/set-schedule"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }
        data = {
            "id_paciente": id_paciente,
            "id_unidade_de_saude": health_unit_ref,
            "exames_paciente": [
        {
            "id_tipo_exame": id_tipo_exame,
            "data_agendamento": data_agendamento,
            "hora_agendamento": hora_agendamento
        }]

        }
        requisicao = requests.post(url_acesso, headers=headers, json=data)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
def get_exames():
    """
    Faz uma requisição para obter o id correspondente ao tipo de exame, o nome dos exames e descrição dos tipos de exames disponíveis.


    Returns:
        dict: retorna um dicionário com o status da requisição e a resposta JSON, ou None em caso de erro.
    """
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "email": "mlisa@gmail.com",
        "senha": "mli2025"
    }

    try:
        url = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/auth/local/signin"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        #return response.json()
        resposta_login = response.json()
        access_token = resposta_login.get("access_token")
        health_unit_ref = resposta_login.get("health_unit_ref")
        url_acesso = "https://magnetic-buzzard-osapicare-a83d5229.koyeb.app/exam-types"
        headers = {
            "Authorization": f"Bearer {access_token}",
                   }

        requisicao = requests.get(url_acesso, headers=headers)
        return {"Status": requisicao.status_code, "Requisição": requisicao.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Resposta do servidor: {response.text}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erro de Timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro inesperado ocorreu: {req_err}")
        return None
    
@st.cache_resource
def agent_osapi():
    root_agent = Agent(
        name = "osapicare",
        #model="gemini-2.0-flash-exp",
        model= "gemini-2.0-flash-exp",
        # Combine a descrição e as instruções aqui, ou adicione um novo campo se o ADK suportar explicitamente instruções do sistema
        description="""
        Você é um **assistente inteligente e prestativo especializado em gestão de dos processos laboratorias da plataforma OsapiCare, você torna as actividades laboratoriais mas simples e fácil de ser realizado**.
        Você pode ajudar os usuários a **registar pacientes, agendar exames e obter informações sobre tipos de exames disponíveis**.
        Você pode usar as seguintes ferramentas:
        - **registar_paciente**: Registra um novo paciente na unidade hospitalar.
        - **criar_agendamento**: Cria um agendamento de exame para um paciente.
        - **get_exames**: Obtém os tipos de exames disponíveis, incluindo o ID, nome e descrição dos exames para ser usado na criação de novo agendamento.
        """,
        tools=[registar_paciente,criar_agendamento, get_exames],  # Certifique-se de que essas ferramentas estejam definidas corretamente
        # Se houver um campo para instruções específicas do modelo, ele seria algo como 'system_instruction' ou 'model_instructions'
        # system_instruction="""Siga as diretrizes de segurança e bem-estar do usuário.""" # Exemplo, verifique a documentação do ADK
    )
    print(f"Agente '{root_agent.name}'.")
    return root_agent

root_agent = agent_osapi()

APP_NAME = "OSAPICARE"


@st.cache_resource
def get_session_service():
    """
    Cria e retorna o serviço de sessão.
    O InMemorySessionService gerencia o histórico da conversa automaticamente para a sessão.
    """
    return InMemorySessionService()

session_service = get_session_service()

@st.cache_resource
def get_adk_runner(_agent, _app_name, _session_service):
    """
    Cria e retorna o runner do ADK.
    """
    adk_runner = Runner(
        agent=_agent,
        app_name=_app_name,
        session_service=_session_service
    )
    print("ADK Runner criado globalmente.")
    return adk_runner

# Passa o agente de notas para o runner
adk_runner = get_adk_runner(root_agent, APP_NAME, session_service) # Passando notes_agent

## Aplicação Streamlit

st.title("🩺 Gerenciador laboratorial") # Título da aplicação atualizado

# Inicializa o histórico de chat no st.session_state se ainda não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if user_message := st.chat_input("Olá! Como posso ajudar você a gerenciar suas actividades hoje?"):
    # Adiciona a mensagem do usuário ao histórico do Streamlit
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    # Define user_id e session_id.
    user_id = "streamlit_usuario"
    session_id = "default_streamlit_usuario"

    try:
        # Garante que a sessão exista no ADK
        # O InMemorySessionService manterá o estado da sessão.
        # Não é ideal tentar criar uma sessão que já existe, mas para InMemorySessionService,
        # get_session pode ser suficiente para verificar a existência.
        existing_session = asyncio.run(session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id))
        if not existing_session:
            asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id))
            print(f"Sessão '{session_id}' criada para '{user_id}'.")
        else:
            print(f"Sessão '{session_id}' já existe para '{user_id}'.")

        # A nova mensagem do usuário a ser enviada ao agente
        new_user_content = types.Content(role='user', parts=[types.Part(text=user_message)])

        async def run_agent_and_get_response(current_user_id, current_session_id, new_content):
            """
            Executa o agente e retorna a resposta final.
            """
            response_text = "Agente não produziu uma resposta final." 
            async for event in adk_runner.run_async(
                user_id=current_user_id,
                session_id=current_session_id,
                new_message=new_content,
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        response_text = f"Agente escalou: {event.error_message or 'Sem mensagem específica.'}"
                    break 
            return response_text

        # Executa a função assíncrona e obtém o resultado
        response = asyncio.run(run_agent_and_get_response(user_id, session_id, new_user_content))

        # Adiciona a resposta do agente ao histórico do Streamlit
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    except Exception as e:
        st.error(f"Erro ao processar a requisição: {e}")
        st.session_state.messages.append({"role": "assistant", "content": f"Desculpe, ocorreu um erro: {e}"})
