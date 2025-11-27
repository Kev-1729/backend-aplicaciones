"""
Gemini Chat Service - Implementación con Google Gemini
"""
import google.generativeai as genai
import asyncio
import logging
from domain.interfaces.chat_service import IChatService
from infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


class GeminiChatService(IChatService):
    """
    Implementación de IChatService usando Google Gemini

    Genera respuestas usando gemini-2.0-flash-exp
    """

    def __init__(self):
        """Initialize Gemini AI client"""
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_CHAT_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"GeminiChatService initialized with model: {self.model_name}")

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
        """
        try:
            # System prompt por defecto
            if not system_prompt:
                system_prompt = self._get_default_system_prompt()

            # Construir prompt completo
            full_prompt = f"""{system_prompt}

CONTEXTO RECUPERADO:
{context}

PREGUNTA DEL USUARIO:
{query}

RESPUESTA:"""

            # Generar respuesta
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(full_prompt)
            )

            return response.text

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    async def generate_text(self, prompt: str) -> str:
        """
        Genera texto a partir de un prompt genérico

        Args:
            prompt: Prompt de entrada

        Returns:
            str: Texto generado
        """
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            return response.text

        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def _get_default_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema por defecto para RAG

        Returns:
            str: System prompt
        """
        return """Eres un asistente especializado en trámites municipales de Carabayllo, Perú.

INSTRUCCIONES IMPORTANTES:
1. SOLO responde usando información del CONTEXTO RECUPERADO proporcionado
2. Si el contexto NO contiene información relevante, indica claramente que no tienes esa información
3. NO inventes información ni uses conocimiento general
4. Cita las fuentes cuando sea posible
5. Responde en español formal pero amigable
6. Formatea tu respuesta en HTML para mejor legibilidad:
   - Usa <h3> para títulos
   - Usa <ul> y <li> para listas
   - Usa <strong> para resaltar información importante
   - Usa <p> para párrafos
   - Usa <div> con estilos inline para destacar advertencias o información crítica

TEMAS QUE MANEJAS:
- Licencias de funcionamiento (bodegas, comercio, establecimientos)
- Normativas municipales (ordenanzas, leyes, decretos)
- Formularios y procedimientos administrativos
- Requisitos y plazos
- Costos y pagos

Si la pregunta es sobre temas NO municipales, indica cortésmente que solo puedes ayudar con trámites municipales."""
