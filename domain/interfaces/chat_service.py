"""
Interface: Chat Service

Contrato abstracto para servicios de generación de respuestas con LLM.
Las implementaciones concretas estarán en infrastructure/
"""
from abc import ABC, abstractmethod


class IChatService(ABC):
    """
    Interfaz para servicios de chat/LLM

    Define el contrato que deben cumplir todas las implementaciones
    (Gemini, OpenAI GPT, Claude, etc.)
    """

    @abstractmethod
    async def generate_answer(
        self,
        query: str,
        context: str,
        system_prompt: str = ""
    ) -> str:
        """
        Genera una respuesta usando el LLM

        Args:
            query: Pregunta del usuario
            context: Contexto recuperado (chunks relevantes)
            system_prompt: Instrucciones del sistema (opcional)

        Returns:
            str: Respuesta generada (HTML formateado)

        Raises:
            ChatGenerationError: Si falla la generación
        """
        pass

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Genera texto a partir de un prompt genérico

        Args:
            prompt: Prompt de entrada

        Returns:
            str: Texto generado

        Raises:
            ChatGenerationError: Si falla la generación
        """
        pass
