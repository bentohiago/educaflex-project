import json
import random

class QuizManager:
    def __init__(self, quiz_file="quiz.json"):
        self.quiz_file = quiz_file
        self.quizzes = self._load_quizzes()
    
    def _load_quizzes(self):
        """Carrega as perguntas do arquivo JSON"""
        try:
            with open(self.quiz_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("quiz", [])
        except Exception as e:
            print(f"Erro ao carregar quizzes: {e}")
            return []
    
    def get_random_quiz(self, theme=None, difficulty=None):
        """Retorna um quiz aleatório, opcionalmente filtrado por tema/dificuldade"""
        filtered = self.quizzes
        
        if theme:
            filtered = [q for q in filtered if q["tema"].lower() == theme.lower()]
        
        if difficulty:
            filtered = [q for q in filtered if q["dificuldade"].lower() == difficulty.lower()]
        
        return random.choice(filtered) if filtered else None
    
    def find_quiz_by_question_text(self, question_text):
        """Tenta encontrar a pergunta exata no conteúdo da IA"""
        for quiz in self.quizzes:
            if quiz["pergunta"].strip().lower() in question_text.strip().lower():
                return quiz
        return None

    
    def check_answer(self, quiz_id, user_answer):
        """Verifica se a resposta do usuário está correta"""
        quiz = next((q for q in self.quizzes if q["id"] == quiz_id), None)
        if not quiz:
            return False
        
        return user_answer.upper() == quiz["resposta_correta"].upper()