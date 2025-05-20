import streamlit as st
import json
import os

USER_FILE = "users.json"

def carregar_usuarios():
    if not os.path.exists(USER_FILE):
        return []
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def exibir_painel_professor():
    st.title("📊 Painel do Professor")

    username = st.session_state.get("auth_cookie", {}).get("user", None)
    if username != "admin":
        st.warning("Acesso restrito! Apenas o usuário administrador pode ver esta página.")
        return

    usuarios = carregar_usuarios()

    st.markdown("### 👥 Desempenho dos Alunos")

    for u in usuarios:
        if u["user"] == "admin":
            continue  # pula o próprio admin

        ranking = u.get("ranking", {
            "pontos": 0,
            "quizzes_respondidos": 0,
            "quizzes_corretos": 0
        })

        st.markdown(f"**🧑 Aluno:** `{u['user']}`")
        st.markdown(f"- Pontos: **{ranking.get('pontos', 0)}**")
        st.markdown(f"- Respondidas: **{ranking.get('quizzes_respondidos', 0)}**")
        st.markdown(f"- Corretas: **{ranking.get('quizzes_corretos', 0)}**")
        st.divider()
