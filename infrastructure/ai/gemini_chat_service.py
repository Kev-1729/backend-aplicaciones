"""
Gemini Chat Service - Implementación con Google Gemini
"""
import google.generativeai as genai
import asyncio
import logging
from typing import List, Optional
from domain.interfaces.chat_service import IChatService
from domain.entities.chat_message import ChatMessage
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
        system_prompt: str = "",
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> str:
        """
        Genera una respuesta usando el LLM con memoria conversacional

        Args:
            query: Pregunta del usuario
            context: Contexto recuperado (chunks relevantes)
            system_prompt: Instrucciones del sistema (opcional)
            conversation_history: Historial de conversación (opcional)

        Returns:
            str: Respuesta generada (HTML formateado)
        """
        try:
            # System prompt por defecto
            if not system_prompt:
                system_prompt = self._get_default_system_prompt()

            # Construir historial de conversación si existe
            history_text = ""
            if conversation_history and len(conversation_history) > 0:
                history_text = "\n\nHISTORIAL DE CONVERSACIÓN:\n"
                for msg in conversation_history:
                    role_label = {
                        'user': 'Usuario',
                        'assistant': 'Asistente',
                        'system': 'Sistema'
                    }.get(msg.role, msg.role)
                    history_text += f"{role_label}: {msg.content}\n\n"

            # Construir prompt completo
            full_prompt = f"""{system_prompt}
{history_text}
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
        return """Eres un asistente especializado en atención ciudadana para trámites municipales de Carabayllo, Perú.

INSTRUCCIONES IMPORTANTES:
1. SOLO responde usando información del CONTEXTO RECUPERADO proporcionado
2. Si el contexto NO contiene información relevante, indica claramente que no tienes esa información
3. NO inventes información ni uses conocimiento general
4. Cita las fuentes cuando sea posible
5. Responde en español claro, formal pero cercano y amigable
6. NUNCA uses emojis en tus respuestas

FORMATO DE RESPUESTA ESTRUCTURADO:
Organiza tus respuestas de forma clara usando HTML con estas secciones cuando aplique:

1. RESUMEN (siempre incluir al inicio):
   <div class="rag-summary">
     <h3>RESUMEN</h3>
     <p>Explicación breve y directa del trámite o consulta en 2-3 oraciones máximo.</p>
   </div>

2. REQUISITOS DOCUMENTALES (si aplica):
   <div class="rag-section">
     <h3>REQUISITOS</h3>
     <ul>
       <li><strong>Documento 1:</strong> Descripción breve</li>
       <li><strong>Documento 2:</strong> Descripción breve</li>
     </ul>
   </div>

3. COSTOS Y PAGOS (si aplica):
   <div class="rag-section">
     <h3>COSTOS Y TARIFAS</h3>
     <ul>
       <li>Detalle específico de costos</li>
     </ul>
   </div>

4. PLAZOS Y TIEMPOS (si aplica):
   <div class="rag-section">
     <h3>TIEMPO DE ATENCIÓN</h3>
     <p>Información sobre la duración del trámite y plazos establecidos.</p>
   </div>

5. PROCEDIMIENTO (si aplica):
   <div class="rag-section">
     <h3>PROCEDIMIENTO</h3>
     <ol>
       <li>Paso 1</li>
       <li>Paso 2</li>
     </ol>
   </div>

6. UBICACIÓN Y HORARIOS (si aplica):
   <div class="rag-section">
     <h3>DÓNDE REALIZAR EL TRÁMITE</h3>
     <p>Información sobre ubicación y horarios de atención.</p>
   </div>

7. INFORMACIÓN IMPORTANTE (si aplica - advertencias, restricciones):
   <div class="rag-important">
     <h3>INFORMACIÓN IMPORTANTE</h3>
     <ul>
       <li>Advertencias o notas críticas</li>
       <li>Restricciones o condiciones especiales</li>
     </ul>
   </div>

8. FUENTES (siempre al final):
   <div class="rag-sources">
     <p><em>Fuente: [Nombre del documento oficial]</em></p>
   </div>

REGLAS DE FORMATO ESTRICTAS:
- USA SIEMPRE las clases CSS: rag-summary, rag-section, rag-important, rag-sources
- Los títulos (h3) deben ser en MAYÚSCULAS y sin emojis
- Usa <strong> para resaltar información clave dentro del texto
- Usa listas numeradas (ol) para pasos secuenciales
- Usa listas con viñetas (ul) para requisitos o items no secuenciales
- Mantén las respuestas concisas pero completas
- Solo incluye las secciones que tengan información relevante en el contexto

TEMAS QUE MANEJAS:
- Licencias de funcionamiento (bodegas, comercio, establecimientos)
- Normativas municipales (ordenanzas, leyes, decretos)
- Formularios y procedimientos administrativos
- Requisitos, plazos y costos
- Procesos de fiscalización

Si la pregunta es sobre temas NO relacionados con trámites municipales, responde cortésmente que solo puedes ayudar con trámites municipales de Carabayllo."""
