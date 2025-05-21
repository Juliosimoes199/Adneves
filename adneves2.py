import streamlit as st
import google.generativeai as genai
import json
import os


# --- Informações do Serviço ---
info_servico = "Temos os seguintes serviços: personalização de t-shirt, personalização de panfleto, cópia preto e branco, cópia a cor, criação de toper, foto rápida, impressão de documento."

# --- Instruções do Sistema/Persona ---
SYSTEM_INSTRUCTION = f"""
Você é um especialista em design gráfico e atendimento ao cliente da empresa 'Adneves', localizada no Rocha Pinto. Seu principal objetivo é coletar todas as informações detalhadas que o cliente deseja para personalizar nossos serviços, garantindo a sua satisfação e fornecendo um atendimento personalizado e agradável.

Nossos serviços incluem: {info_servico}.

Siga estas diretrizes RIGOROSAMENTE:
1.  **Apresentação:** Comece sempre se apresentando como um especialista da Adneves, seu nome é Neves AI.
2.  **Personalização (T-shirt e Panfleto):** Se o cliente demonstrar interesse em **personalização de t-shirt** ou **panfleto**, peça todas as informações necessárias e detalhadas para a personalização e a quantidade desejada do produto. Seja EXTREMAMENTE específico sobre cores, imagens, textos, estilo, fontes, layout, tamanho da arte, local de aplicação (frente, costas, mangas para t-shirt), e a **quantidade exata** desejada para cada item.
3.  **Incentivo e Diferenciais:** Se o cliente estiver confuso ou hesitante, enfatize os diferenciais da Adneves:
    * Experiência dos profissionais altamente qualificados.
    * Qualidade dos produtos (ex: tecidos duráveis para t-shirts).
    * Atendimento personalizado focado nas necessidades individuais.
    Incentive a personalização.
4.  **Coleta de Dados para Agendamento:** Se o cliente expressar o desejo de aderir a um serviço de personalização (t-shirt ou panfleto), colete **nome completo** (primeiro e último nome), **tipo de serviço** e a **descrição detalhada da personalização** (todos os detalhes mencionados no ponto 2).
5.  **Confirmação da Personalização:** Continue coletando informações detalhadas até que o cliente **confirme explicitamente** que está **totalmente satisfeito** e que **não falta adicionar mais nenhum detalhe**. SOMENTE APÓS ESSA CONFIRMAÇÃO, confirme a personalização com uma mensagem clara e de agradecimento.
6.  **Outras Perguntas:** Ofereça-se para responder a outras perguntas sobre os serviços ou a localização da Adneves.
7.  **Tom:** Seja sempre amigável, informativo e prestativo.\n"""
SYSTEM_INSTRUCTION += """
8.  **Formato de Saída JSON:** Ao final da interação, ou sempre que for relevante para a próxima etapa da conversa (por exemplo, quando as informações essenciais estiverem sendo coletadas ou confirmadas), você deve retornar um dicionário JSON com as informações coletadas. Se uma informação não estiver presente, retorne "null".
    ```json
    {
        "nome": "null",
        "servico": "null",
        "quantidade": "null",
        "descricao": "null",
        "servico_agendado": "null"
    }
    ```
    * **nome:** Nome completo do cliente.
    * **servico:** Tipo de serviço de personalização (ex: "personalização de t-shirt", "personalização de panfleto").
    * **quantidade:** A quantidade desejada do produto.
    * **descricao:** Todos os detalhes específicos da personalização.
    * **servico_agendado:** `true` se o cliente confirmar que todos os detalhes estão corretos e completos; `false` caso contrário.
9.  **Tópicos Fora de Serviço:** Se a pergunta do cliente não estiver relacionada a nenhum dos serviços da Adneves, responda educadamente que você pode ajudar com informações sobre nossos serviços.

Lembre-se: seu objetivo é garantir que a personalização atenda exatamente às expectativas do cliente.
"""

# Configurar o Gemini uma única vez
genai.configure(api_key="AIzaSyArTog-quWD9Tqf-CkkFAq_-UOZfK1FTtA")

# --- Gerenciamento de Estado do Streamlit ---
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        'gemini-1.5-flash',
        system_instruction=SYSTEM_INSTRUCTION
    )

if "chat" not in st.session_state:
    st.session_state.chat = st.session_state.model.start_chat(history=[])


# --- Função para Enviar Mensagens ao Gemini ---
def send_message_to_gemini(user_message):
    try:
        response = st.session_state.chat.send_message(
            user_message,
            generation_config=genai.types.GenerationConfig(temperature=0.7)
        )
        
        # O chat.history é automaticamente atualizado pela API
        max_history_length = 20
        if len(st.session_state.chat.history) > max_history_length:
            st.session_state.chat.history = st.session_state.chat.history[-max_history_length:]
        
        return response.text
    except Exception as e:
        st.error(f"Ocorreu um erro ao comunicar com o Gemini: {e}")
        return "Desculpe, houve um problema. Por favor, tente novamente."

# --- Interface Streamlit ---
st.set_page_config(page_title="Adneves Design Gráfico", page_icon="🎨")

st.title("🎨 Adneves Design Gráfico - Assistente de Personalização")
st.markdown("Olá! Sou o especialista da Adneves, localizado no Rocha Pinto, e estou aqui para ajudar você a personalizar seus sonhos em design gráfico. Qual serviço você procura hoje?")

# Exibir o histórico da conversa
for message in st.session_state.chat.history:
    role = "user" if message.role == 'user' else "assistant"
    with st.chat_message(role):
        # Itera sobre as partes da mensagem.
        # Para mensagens de texto, 'part' será uma string.
        for part in message.parts:
            # Verifica se a 'part' é diretamente uma string ou se tem um atributo 'text'
            if isinstance(part, str):
                content = part
            elif hasattr(part, 'text'): # Verifica se a parte tem um atributo 'text' (como TextPart ou similar)
                content = part.text
            else: # Para outros tipos de conteúdo, converte para string
                content = str(part)

            # Tenta parsear a resposta do modelo como JSON
            if role == "assistant":
                try:
                    # Verifica se o conteúdo parece ser um JSON antes de tentar parsear
                    # (começa com '{' e termina com '}' e tem pelo menos alguns caracteres no meio)
                    if content.strip().startswith('{') and content.strip().endswith('}') and len(content.strip()) > 2:
                        resposta_json = json.loads(content)
                        st.json(resposta_json) # Exibe como JSON formatado
                    else:
                        st.markdown(content) # Exibe como texto normal
                except json.JSONDecodeError:
                    st.markdown(content) # Se não for JSON válido, exibe como texto normal
            else: # Mensagem do usuário
                st.markdown(content)


# Campo de entrada para o usuário
user_input = st.chat_input("Digite sua pergunta ou pedido:")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    response_text = send_message_to_gemini(user_input)
    st.rerun() # Força um rerun para exibir a nova mensagem imediatamente