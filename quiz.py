import streamlit as st
import json
import random
import os

QUIZ_FILE = "quiz.json"
USER_FILE = "users.json"


def carregar_usuarios():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_usuarios(usuarios):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=2, ensure_ascii=False)


def encontrar_usuario(username):
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["user"] == username:
            return u
    return None


def atualizar_ranking(username, acertou):
    usuarios = carregar_usuarios()
    for u in usuarios:
        if u["user"] == username:
            if "ranking" not in u:
                u["ranking"] = {
                    "pontos": 0,
                    "quizzes_respondidos": 0,
                    "quizzes_corretos": 0
                }
            u["ranking"]["quizzes_respondidos"] += 1
            if acertou:
                u["ranking"]["quizzes_corretos"] += 1
                u["ranking"]["pontos"] += 10
            salvar_usuarios(usuarios)
            return


def exibir_quiz():
    st.title("🧠 Quiz de Conhecimentos")

    username = st.session_state.get("auth_cookie", {}).get("user", None)
    if not username:
        st.warning("Você precisa estar logado para acessar o quiz.")
        return

    with open(QUIZ_FILE, "r", encoding="utf-8") as f:
        dados = json.load(f)

    perguntas = dados.get("quiz", [])
    if not perguntas:
        st.info("Nenhuma pergunta disponível no momento.")
        return

    # Inicializa a pergunta atual, se necessário
    if "pergunta_atual" not in st.session_state:
        st.session_state.pergunta_atual = random.choice(perguntas)
        st.session_state.quiz_etapa = "responder"  # etapas: responder, resultado
        st.session_state.resposta_usuario = None
        st.session_state.acertou = None

    pergunta = st.session_state.pergunta_atual
    pergunta_id = pergunta["id"]

    st.markdown(f"**Pergunta:** {pergunta['pergunta']}")

    if st.session_state.quiz_etapa == "responder":
        resposta = st.radio(
            "Escolha a resposta:",
            list(pergunta["alternativas"].items()),
            format_func=lambda x: f"{x[0]}) {x[1]}",
            key=f"resposta_{pergunta_id}"
        )

        if st.button("Responder", key=f"responder_{pergunta_id}"):
            alternativa_escolhida = resposta[0]
            correta = pergunta["resposta_correta"]
            st.session_state.resposta_usuario = alternativa_escolhida
            st.session_state.acertou = (alternativa_escolhida == correta)
            atualizar_ranking(username, st.session_state.acertou)
            st.session_state.quiz_etapa = "resultado"
            st.rerun()

    elif st.session_state.quiz_etapa == "resultado":
        correta = pergunta["resposta_correta"]
        if st.session_state.acertou:
            st.success("✅ Resposta correta!")
        else:
            st.error(f"❌ Resposta errada. A correta era: {correta}) {pergunta['alternativas'][correta]}")

        if st.button("Próxima Pergunta", key=f"proxima_{pergunta_id}"):
            st.session_state.pergunta_atual = random.choice(perguntas)
            st.session_state.quiz_etapa = "responder"
            st.session_state.resposta_usuario = None
            st.session_state.acertou = None
            st.rerun()
