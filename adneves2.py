import requests
import datetime
import asyncio
import streamlit as st
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService # Para protótipo, usar persistente em prod
from google.adk.runners import Runner
from google.genai import types
import os
from dotenv import load_dotenv
import google.generativeai as genai
import warnings
import logging


# --- Configurações Iniciais ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("AVISO: GOOGLE_API_KEY não encontrada no ambiente. Por favor, defina-a ou codifique-a para teste.")
    genai.configure(api_key="YOUR_HARDCODED_API_KEY_HERE") # CUIDADO: Nunca em produção

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
print("Bibliotecas importadas e GenAI configurado.")

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"

url = "https://agendas-adilson-default-rtdb.firebaseio.com/"

# --- Funções de Gerenciamento de Notas ---

def criar_nota(titulo:str, descricao:str, data:str) -> str:
    """
    Cria uma nota no banco de dados Firebase.
    Args:
        titulo (str): Título da nota.
        descricao (str): Descrição da nota.
        data (str): Data da tarefa no formato "DD-MM", "Amanhã" ou "Hoje".
    Returns:
        str: Mensagem de sucesso ou erro.
    """
    data_criacao = datetime.datetime.now()
    nota = {
        "titulo": titulo,
        "descricao": descricao,
        "data": data,
        "status": "Pendente",
        "data_criacao": data_criacao.strftime("%Y-%m-%d %H:%M:%S") # Formato completo para data_criacao
    }
    try:
        requisicao = requests.post(url + ".json", json=nota)
        if requisicao.status_code == 200:
            return "Nota criada com sucesso!"
        else:
            return f"Erro ao criar nota: {requisicao.status_code} - {requisicao.text}"
    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro de conexão ao criar a nota: {e}"

def listar_notas() -> dict:
    """
    Lista todas as notas do banco de dados Firebase.
    Returns:
        dict: Dicionário contendo todas as notas ou None em caso de erro.
    """
    try:
        requisicao = requests.get(url + ".json")
        if requisicao.status_code == 200:
            return requisicao.json()
        else:
            print(f"Erro ao listar notas: {requisicao.status_code} - {requisicao.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro de conexão ao listar as notas: {e}")
        return None
    
def exibir_notas() -> str:
    """
    Lista todas as notas e as formata em uma string legível.
    Returns:
        str: Uma string formatada com todas as notas ou uma mensagem de "nenhuma nota encontrada".
    """
    notas = listar_notas()
    if notas:
        output = "--- SUAS NOTAS ---\n"
        for id_nota, detalhes in notas.items():
            titulo = detalhes.get('titulo', 'N/A')
            descricao = detalhes.get('descricao', 'N/A')
            data = detalhes.get('data', 'N/A')
            status = detalhes.get('status', 'N/A')
            data_criacao = detalhes.get('data_criacao', 'N/A')
            
            output += f"ID: {id_nota}\n"
            output += f"  Título: {titulo}\n"
            output += f"  Descrição: {descricao}\n"
            output += f"  Data da Tarefa: {data}\n"
            output += f"  Status: {status}\n"
            output += f"  Criado em: {data_criacao}\n"
            output += "--------------------\n"
        return output
    else:
        return "Nenhuma nota encontrada."

def atualizar_campo_tarefa(id_usuario:str, campo:str, novo_valor:str) -> str:
    """
    Atualiza um único campo de uma tarefa usando PATCH.
    Args:
        id_usuario (str): O ID da nota a ser atualizada.
        campo (str): O nome do campo a ser atualizado (ex: 'titulo', 'descricao', 'status', 'data').
        novo_valor: O novo valor para o campo.
    Returns:
        str: Mensagem de sucesso ou erro.
    """
    url_nova = f"{url}{id_usuario}.json"
    dados_para_atualizar = {campo: novo_valor}

    try:
        response = requests.patch(url_nova, json=dados_para_atualizar)
        if response.status_code == 200:
            return f"Campo '{campo}' da tarefa '{id_usuario}' atualizado para '{novo_valor}' com sucesso!"
        elif response.status_code == 204:
            return f"Campo '{campo}' da tarefa '{id_usuario}' atualizado para '{novo_valor}' com sucesso! (Sem conteúdo na resposta)"
        else:
            return f"Erro ao atualizar o campo '{campo}' da tarefa '{id_usuario}'. Status: {response.status_code}, Detalhes: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro de conexão: {e}"

def deletar_nota(id_nota: str) -> str:
    """
    Deleta uma nota específica do banco de dados Firebase.
    Args:
        id_nota (str): O ID da nota a ser deletada.
    Returns:
        str: Mensagem de sucesso ou erro.
    """
    url_nota = f"{url}{id_nota}.json"
    try:
        response = requests.delete(url_nota)
        if response.status_code == 200:
            return f"Nota '{id_nota}' deletada com sucesso!"
        else:
            return f"Erro ao deletar nota '{id_nota}'. Status: {response.status_code}, Detalhes: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro de conexão ao deletar a nota: {e}"

def buscar_notas(termo: str, campo: str = 'titulo') -> str:
    """
    Busca notas que contenham um termo específico em um determinado campo e as formata.
    Args:
        termo (str): O termo a ser buscado.
        campo (str): O campo onde a busca será realizada (ex: 'titulo', 'descricao'). Padrão é 'titulo'.
    Returns:
        str: Uma string formatada com as notas encontradas ou uma mensagem de "nenhuma nota encontrada".
    """
    notas_encontradas = {}
    todas_notas = listar_notas()
    if todas_notas:
        for id_nota, detalhes in todas_notas.items():
            valor_campo = detalhes.get(campo, '').lower()
            if termo.lower() in valor_campo:
                notas_encontradas[id_nota] = detalhes
    
    if notas_encontradas:
        output = f"\n--- Notas Encontradas com '{termo}' no campo '{campo}' ---\n"
        for id_nota, detalhes in notas_encontradas.items():
            titulo = detalhes.get('titulo', 'N/A')
            descricao = detalhes.get('descricao', 'N/A')
            data = detalhes.get('data', 'N/A')
            status = detalhes.get('status', 'N/A')
            data_criacao = detalhes.get('data_criacao', 'N/A')
            
            output += f"ID: {id_nota}\n"
            output += f"  Título: {titulo}\n"
            output += f"  Descrição: {descricao}\n"
            output += f"  Data da Tarefa: {data}\n"
            output += f"  Status: {status}\n"
            output += f"  Criado em: {data_criacao}\n"
            output += "--------------------\n"
        return output
    else:
        return f"Nenhuma nota encontrada com o termo '{termo}' no campo '{campo}'."


@st.cache_resource
def get_notes_agent(): # Renomeado para refletir o propósito
    """
    Cria e retorna a instância do agente de gerenciamento de notas.
    Usamos st.cache_resource para garantir que o agente seja criado apenas uma vez por sessão do Streamlit.
    """
    notes_agent = Agent(
        name="Gerenciador_de_Notas_AdilsonNeves", # Nome mais apropriado
        model=MODEL_GEMINI_2_0_FLASH,
        description=(
            "Você é um **assistente inteligente e prestativo especializado em gerenciamento de tarefas e notas**."
            "Sua principal função é ajudar o usuário a **organizar, criar, listar, buscar, atualizar e deletar suas tarefas e lembretes diários ou futuros**."
            "**Você tem acesso e DEVE usar as seguintes ferramentas para interagir com o banco de dados de notas:**\n"
            "- **`criar_nota(titulo: str, descricao: str, data: str)`**: Para adicionar uma nova tarefa ou lembrete. O `titulo` é obrigatório. A `data` deve ser fornecida no formato 'DD-MM', 'Hoje' ou 'Amanhã'. Se o usuário não fornecer todos os dados necessários (título, descrição, data), **você DEVE perguntar por eles**.\n"
            "- **`listar_notas() -> dict`**: Para obter todas as notas do banco de dados. Esta função retorna um dicionário bruto de notas.\n"
            "- **`exibir_notas() -> str`**: **USE ESTA FERRAMENTA SEMPRE APÓS `listar_notas()` ou para mostrar notas encontradas.** Ela formatará e apresentará as notas listadas de forma legível para o usuário, incluindo o ID de cada nota.\n"
            "- **`atualizar_campo_tarefa(id_nota: str, campo: str, novo_valor: str)`**: Para modificar um campo específico (como 'titulo', 'descricao', 'data' ou 'status') de uma tarefa existente. **Você DEVE obter o `id_nota` do usuário ou pedir para ele listar as notas primeiro para encontrar o ID**. O `campo` e o `novo_valor` também são necessários.\n"
            "- **`deletar_nota(id_nota: str)`**: Para remover uma tarefa. **Você DEVE obter o `id_nota` do usuário ou pedir para ele listar as notas primeiro para encontrar o ID**. Peça confirmação antes de deletar, se apropriado.\n"
            "- **`buscar_notas(termo: str, campo: str = 'titulo') -> str`**: Para encontrar tarefas por palavra-chave no `titulo` ou `descricao`. Retorna uma string formatada com os resultados. Se o usuário não especificar o campo, use 'titulo' como padrão.\n\n"
            "**Instruções de Comportamento:**\n"
            "1.  **Prioridade de Memória:** **Você DEVE referenciar informações de conversas anteriores e o estado atual das notas (se for relevante) ao formular suas respostas.** Por exemplo, se o usuário perguntar 'E a nota que criei sobre o relatório ontem?', você deve tentar usar a função de busca ou listar as notas para encontrar e referenciar essa nota.\n"
            "2.  **Confirmação:** Após criar, atualizar ou deletar uma nota, **você DEVE confirmar a operação com o usuário** usando a mensagem retornada pela ferramenta.\n"
            "3.  **IDs de Notas:** Para operações de atualização e deleção, **sempre que o usuário não souber o ID da nota, sugira que ele use 'listar notas' ou 'buscar notas' para encontrar o ID primeiro.**\n"
            "4.  **Clareza:** Seja prestativo, claro e objetivo. Forneça feedback sobre as operações realizadas e os resultados das buscas/listagens.\n"
            "5.  **Entendimento Contextual:** Esforce-se para entender a intenção do usuário mesmo que as informações não sejam explícitas, usando as ferramentas apropriadas. Por exemplo, se o usuário disser 'Quero adicionar uma tarefa para amanhã: Comprar leite e pão', você deve identificar o título, descrição e data e usar `criar_nota`."
        ),
        tools=[criar_nota, listar_notas, exibir_notas, atualizar_campo_tarefa, deletar_nota, buscar_notas],
    )
    print(f"Agente '{notes_agent.name}' criado usando o modelo '{MODEL_GEMINI_2_0_FLASH}'.")
    return notes_agent

# Inicializa o agente
notes_agent = get_notes_agent() # Variável renomeada

## Configurações de Sessão ADK e Runner
APP_NAME = "Gerenciador_Notas_Adilson_Neves" # Nome do aplicativo mais descritivo e sem espaços

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
adk_runner = get_adk_runner(notes_agent, APP_NAME, session_service) # Passando notes_agent

## Aplicação Streamlit

st.title("📚 Gerenciador de Notas Pessoais") # Título da aplicação atualizado

# Inicializa o histórico de chat no st.session_state se ainda não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe mensagens anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if user_message := st.chat_input("Olá! Como posso ajudar você a gerenciar suas notas e tarefas hoje?"):
    # Adiciona a mensagem do usuário ao histórico do Streamlit
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    # Define user_id e session_id.
    user_id = "streamlit_user"
    session_id = "default_streamlit_session"

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
