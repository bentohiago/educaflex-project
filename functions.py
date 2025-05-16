import boto3
import json
import uuid
from datetime import datetime
import os
import pandas as pd
import PyPDF2

PROFILE_NAME = os.environ.get('AWS_PROFILE', 'bento-grupo4')

def get_boto3_client(service_name, region_name='us-east-1', profile_name='bento-grupo4'):
    """
    Retorna um cliente do serviço AWS especificado.
    
    Tenta usar o perfil especificado para desenvolvimento local primeiro.
    Se falhar, assume que está em uma instância EC2 e usa as credenciais do IAM role.
    """
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region_name)
        client = session.client(service_name)
        if service_name == 'sts':
            caller_identity = client.get_caller_identity()
            print(f"DEBUG: Caller Identity: {caller_identity}")
        print(f"DEBUG: Using profile '{profile_name}' in region '{region_name}' for service '{service_name}'")
        return client
    except Exception as e:
        print(f"INFO: Não foi possível usar o perfil local '{profile_name}', tentando credenciais do IAM role: {str(e)}")
        try:
            session = boto3.Session(region_name=region_name)
            client = session.client(service_name)
            caller_identity = client.get_caller_identity()
            print(f"DEBUG: Caller Identity (IAM Role): {caller_identity}")
            print(f"DEBUG: Using IAM role in region '{region_name}' for service '{service_name}'")
            return client
        except Exception as e:
            print(f"ERRO: Falha ao criar cliente boto3: {str(e)}")
            return None

def read_pdf(file_path):
    """Lê o conteúdo de um arquivo PDF e retorna como string."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"

def read_txt(file_path):
    """Lê o conteúdo de um arquivo TXT e retorna como string."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Erro ao ler TXT: {str(e)}"

def read_csv(file_path):
    """Lê o conteúdo de um arquivo CSV e retorna como string."""
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except Exception as e:
        return f"Erro ao ler CSV: {str(e)}"
    
def format_context(context, source="Contexto Adicional"):
    """Formata o contexto para ser adicionado ao prompt."""
    return f"\n\n{source}:\n{context}\n\n"

#ALTERAR
def generate_chat_prompt(user_message, conversation_history=None, context=""):
    """
    Gera um prompt de chat completo com histórico de conversa e contexto opcional.
    """
    system_prompt = """
    Você é 'Astro', o amigo robô espacial super paciente, divertido e inteligente! Sua missão é ser o guia de crianças de 6 a 10 anos, especialmente aquelas que podem encontrar o aprendizado um pouco complicado, que se distraem fácil ou que precisam de um jeitinho diferente para entender as coisas.
    Você vai transformar o aprendizado em uma aventura espacial incrível e acessível para cada uma delas!
    Aqui estão suas diretrizes essenciais para criar respostas que faça sentido para esse público:
    Seja Sempre Astro - O Robô Amigão: Mantenha sua personalidade: use um tom entusiasta, amigável. Use palavras simples, curtas e diretas. Fale como um amigo confiável.
    Mega Paciente e Super Claro: Sua prioridade é a clareza e a paciência infinita.
    Quebre tudo: Divida qualquer explicação em passos muito pequenos e fáceis de seguir. Um passo por vez!
    Frases Curtas: Use frases bem curtinhas. Evite parágrafos longos.
    Repita (de outro jeito!): Se a criança parecer confusa ou pedir de novo, explique a mesma coisa usando palavras diferentes ou um novo exemplo. Não tenha medo de repetir, mas sempre de uma forma nova e mais clara.
    Confirme Entendimento: Pergunte ocasionalmente se eles entenderam o pedacinho que você explicou antes de passar para o próximo. Ex: "Faz sentido até aqui, pequeno astronauta?"
    Visualize o Invisível: Use descrições que ajudem a criança a "ver" a idéia na cabeça dela.
    Exemplos Concretos e do Dia a Dia: Conecte o que você está ensinando com coisas que eles já conhecem: brinquedos, animais, comida, atividades (correr, pular, desenhar), objetos da casa.
    Analogias Espaciais Simples: Use comparações com coisas do espaço (estrelas, planetas, foguetes, poeira estelar) de um jeito fácil de entender. Ex: "Pensar é como ligar os propulsores do seu foguete!"
    Incentive a Imaginação/Desenho: Sugira que eles imaginem algo ou até desenhem a ideia para ajudar a fixar. Ex: "Imagine que cada número é uma estrelinha. Quantas estrelinhas teriam juntado?"
    Foco na Diversão e no Estímulo: O aprendizado deve ser uma jornada legal!
    Perguntas Interativas: Faça perguntas simples para mantê-los engajados e pensando ativamente.
    Elogie o Esforço (Muito!): Reconheça e elogie cada tentativa, cada pergunta, cada pequena conquista. "Excelente pergunta! Isso mostra que seu cérebro de astronauta está a todo vapor!" "Muito bem pensado!” Transforme Erros em Aprendizado: Se eles errarem, mostre que isso faz parte da descoberta. "Opa! O foguete desviou um pouquinho, mas isso nos ensina algo novo! Vamos tentar ajustar a rota?"
    O Que EVITAR:
    Jargão ou Palavras Difíceis: NUNCA use termos técnicos ou palavras complicadas sem uma explicação MUITO simples logo em seguida (e, se possível, evite completamente).
    Sobrecarga de Informação: Não despeje um monte de informações de uma vez. Vá devagar, um conceito por explicação.
    Abstrações Puras: Sempre ancore idéias abstratas em exemplos concretos ou visuais.
    Lembre-se, Astro: sua missão é criar um ambiente seguro, divertido e claro onde cada criança, no seu ritmo, possa explorar, perguntar e sentir a alegria da descoberta. Seja um mentor no caminho do aprendizado para eles!
    """

    conversation_context = ""
    if conversation_history and len(conversation_history) > 0:
      conversation_context = "Histórico da conversa:\n"
      recent_messages = conversation_history[-8:]
      for message in recent_messages:
        role = "Usuário" if message.get('role') == 'user' else "Assistente"
        conversation_context += f"{role}: {message.get('content')}\n"
      conversation_context += "\n"

    full_prompt = f"{system_prompt}\n\n{conversation_context}{context}Usuário: {user_message}\n\nAssistente:"
    
    return full_prompt

#ALTERAR
def invoke_bedrock_model(prompt, inference_profile_arn, model_params=None):
    """
    Invoca um modelo no Amazon Bedrock usando um Inference Profile.
    """
    if model_params is None:
        model_params = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 200,
            "max_tokens": 1024,
        }

    bedrock_runtime = get_boto3_client('bedrock-runtime')

    if not bedrock_runtime:
        return {
        "error": "Não foi possível conectar ao serviço Bedrock.",
        "answer": "Erro de conexão com o modelo.",
        "sessionId": str(uuid.uuid4())
        }

    try:
        body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": model_params["max_tokens"],
        "temperature": model_params["temperature"],
        "top_p": model_params["top_p"],
        "top_k": model_params["top_k"],
        "messages": [
        {
        "role": "user",
        "content": [
        {
        "type": "text",
        "text": prompt
        }
    ]
    }
    ]
    })

        response = bedrock_runtime.invoke_model(
        modelId=inference_profile_arn,  # Usando o ARN do Inference Profile
        body=body,
        contentType="application/json",
        accept="application/json"
    )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']
            
        return {
            "answer": answer,
            "sessionId": str(uuid.uuid4())
        }
        
    except Exception as e:
        print(f"ERRO: Falha na invocação do modelo Bedrock: {str(e)}")
        print(f"ERRO: Exception details: {e}")
        return {
            "error": str(e),
            "answer": f"Ocorreu um erro ao processar sua solicitação: {str(e)}. Por favor, tente novamente.",
            "sessionId": str(uuid.uuid4())
        }
def read_pdf_from_uploaded_file(uploaded_file):
    """Lê o conteúdo de um arquivo PDF carregado pelo Streamlit."""
    try:
        import io
        from PyPDF2 import PdfReader
        
        pdf_bytes = io.BytesIO(uploaded_file.getvalue())
        reader = PdfReader(pdf_bytes)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {str(e)}"

def read_txt_from_uploaded_file(uploaded_file):
    """Lê o conteúdo de um arquivo TXT carregado pelo Streamlit."""
    try:
        return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Erro ao ler TXT: {str(e)}"

def read_csv_from_uploaded_file(uploaded_file):
    """Lê o conteúdo de um arquivo CSV carregado pelo Streamlit."""
    try:
        import pandas as pd
        import io
        
        df = pd.read_csv(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        return df.to_string()
    except Exception as e:
        return f"Erro ao ler CSV: {str(e)}"