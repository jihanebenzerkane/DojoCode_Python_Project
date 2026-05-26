"""
groq_worker.py — QThread pour les appels Groq API.
L'UI reste réactive pendant que Groq répond (2-5 secondes).
"""
from PySide6.QtCore import QThread, Signal


class GroqWorker(QThread):
    """
    Worker qui exécute l'appel à GroqService dans un thread séparé.
    L'UI reste réactive pendant que Groq répond.

    Signals :
        response_ready(str)  — émis quand la réponse est disponible
        error_occurred(str)  — émis si l'API renvoie une erreur
    """

    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, groq_service, user_message: str, challenge,
                 submitted_code: str = "", conversation_history: list = None,
                 difficulty: str = "beginner"):
        super().__init__()
        self.groq_service = groq_service
        self.user_message = user_message
        self.challenge = challenge
        self.submitted_code = submitted_code
        self.conversation_history = conversation_history or []
        self.difficulty = difficulty

    def run(self):
        """Appelé automatiquement par QThread.start() dans un thread séparé."""
        try:
            response = self.groq_service.ask_sensei(
                user_message=self.user_message,
                challenge=self.challenge,
                submitted_code=self.submitted_code,
                conversation_history=self.conversation_history,
                difficulty=self.difficulty
            )
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(f"Erreur Groq : {str(e)}")