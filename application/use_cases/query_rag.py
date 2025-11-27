"""
Query RAG Use Case - Procesa consultas del usuario usando RAG
"""
import logging
from typing import List, Dict
from application.dtos.query_dto import QueryInput, QueryOutput
from domain.interfaces.embedding_service import IEmbeddingService
from domain.interfaces.vector_store import IVectorStore
from domain.interfaces.chat_service import IChatService
from domain.entities.query_result import SimilarChunk

logger = logging.getLogger(__name__)


class QueryRAGUseCase:
    """
    Caso de uso: Consultar el sistema RAG

    Orquesta el flujo completo:
    1. Generar embedding de la query
    2. Buscar chunks similares en vector store
    3. Construir contexto
    4. Generar respuesta con LLM
    """

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        chat_service: IChatService,
        similarity_threshold: float = 0.4,
        top_k: int = 5
    ):
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._chat_service = chat_service
        self._similarity_threshold = similarity_threshold
        self._top_k = top_k

    async def execute(self, input_dto: QueryInput) -> QueryOutput:
        """
        Ejecuta la consulta RAG

        Args:
            input_dto: QueryInput con la consulta del usuario

        Returns:
            QueryOutput: Respuesta con answer, sources, etc.
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"[STEP 1] User query: '{input_dto.query}'")

        try:
            # Detectar comandos especiales (ayuda, FAQ, etc.)
            special_response = self._handle_special_commands(input_dto.query)
            if special_response:
                return special_response

            # 1. Generar embedding de la query
            logger.info("[STEP 2] Generating query embedding...")
            query_embedding = await self._embedding_service.generate_query_embedding(
                input_dto.query
            )
            logger.info(f"[STEP 2] Generated embedding with {len(query_embedding)} dimensions")

            # 2. Buscar chunks similares
            logger.info(
                f"[STEP 3] Searching similar chunks (threshold={self._similarity_threshold}, "
                f"limit={self._top_k})..."
            )
            similar_chunks = await self._vector_store.search_similar_chunks(
                embedding=query_embedding,
                threshold=self._similarity_threshold,
                limit=self._top_k
            )
            logger.info(f"[STEP 3] Found {len(similar_chunks)} similar chunks")

            # 3. Verificar si se encontraron resultados
            if not similar_chunks:
                logger.warning("[STEP 3] No similar chunks found")
                return QueryOutput(
                    answer=self._get_no_results_message(),
                    sources=[]
                )

            # 4. Construir contexto
            logger.info("[STEP 4] Building context from chunks...")
            context = self._build_context(similar_chunks)
            logger.info(f"[STEP 4] Context built: {len(context)} characters")

            # 5. Generar respuesta
            logger.info("[STEP 5] Generating answer with LLM...")
            answer = await self._chat_service.generate_answer(
                query=input_dto.query,
                context=context
            )
            logger.info(f"[STEP 5] Answer generated: {len(answer)} characters")

            # 6. Extraer fuentes únicas
            sources = list(set(chunk.get('filename', '') for chunk in similar_chunks))

            logger.info(f"[STEP 6] Query completed successfully")
            logger.info(f"{'='*50}\n")

            return QueryOutput(
                answer=answer,
                sources=sources,
                document_name=sources[0] if sources else None
            )

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            raise

    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Construye contexto a partir de chunks similares

        Args:
            chunks: Lista de chunks con metadata

        Returns:
            str: Contexto formateado para el LLM
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_name = chunk.get('filename', 'Documento Desconocido')
            text = chunk.get('chunk_text', '')
            context_parts.append(f"[Fuente {i}: {doc_name}]\n{text}\n")

        return "\n".join(context_parts)

    def _handle_special_commands(self, query: str) -> QueryOutput | None:
        """
        Maneja comandos especiales (ayuda, FAQ, temas disponibles)

        Args:
            query: Query del usuario

        Returns:
            QueryOutput si es comando especial, None si no
        """
        query_lower = query.lower().strip()

        # 1. Ayuda con el RAG (debe ir ANTES que ayuda general)
        if 'ayuda con el rag' in query_lower or 'cómo preguntar' in query_lower:
            logger.info("[RAG_HELP] RAG help requested")
            return QueryOutput(
                answer=self._get_rag_help_message(),
                sources=[],
                document_name="Guía Técnica RAG"
            )

        # 2. FAQ
        if 'faq' in query_lower or 'preguntas frecuentes' in query_lower:
            logger.info("[FAQ] FAQ requested")
            return QueryOutput(
                answer=self._get_faq_message(),
                sources=[],
                document_name="Preguntas Frecuentes"
            )

        # 3. Temas disponibles
        if 'temas disponibles' in query_lower or 'qué temas' in query_lower:
            logger.info("[TOPICS] Topics list requested")
            return QueryOutput(
                answer=self._get_topics_message(),
                sources=[],
                document_name="Temas Disponibles"
            )

        # 4. Ayuda general (debe ir al FINAL)
        help_keywords = ['ayuda', 'ayúdame', 'qué puedes hacer', 'que puedes hacer',
                        'qué temas', 'que temas', 'sobre qué', 'sobre que',
                        'de qué', 'de que', 'help', 'opciones', 'menú', 'menu']

        if any(keyword in query_lower for keyword in help_keywords):
            logger.info("[HELP] Help message requested")
            return QueryOutput(
                answer=self._get_help_message(),
                sources=[],
                document_name="Sistema de Ayuda"
            )

        return None

    def _get_help_message(self) -> str:
        """Mensaje de ayuda general"""
        return """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin-bottom: 15px;">
            <h2 style="margin: 0 0 10px 0; font-size: 24px;">Asistente de Trámites Municipales</h2>
            <p style="margin: 0; opacity: 0.9;">Tu guía inteligente para procedimientos del municipio</p>
        </div>

        <p><strong>📋 CONSULTAS FRECUENTES</strong></p>
        <p>Haz clic o escribe una de estas opciones para obtener ayuda rápida:</p>

        <div style="display: grid; gap: 10px; margin: 15px 0;">
            <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong>1️⃣ Preguntas Frecuentes</strong><br/>
                <em style="color: #64748b;">Consultas más comunes sobre trámites</em>
            </div>

            <div style="background: #fef3c7; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <strong>2️⃣ Ayuda con el RAG</strong><br/>
                <em style="color: #64748b;">Aprende a hacer mejores preguntas</em>
            </div>

            <div style="background: #f0fdf4; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981;">
                <strong>3️⃣ Temas disponibles</strong><br/>
                <em style="color: #64748b;">Lista de todos los temas que manejo</em>
            </div>
        </div>

        <p style="margin-top: 20px;"><strong>💡 Ejemplos de preguntas directas:</strong></p>
        <ul style="line-height: 1.8;">
            <li>"¿Cómo saco una licencia de funcionamiento para una bodega?"</li>
            <li>"¿Qué requisitos necesito para comercio ambulatorio?"</li>
            <li>"¿Cuánto cuesta una licencia provisional?"</li>
            <li>"¿Dónde descargo el formato de solicitud?"</li>
        </ul>

        <p style="background: #fef2f2; padding: 10px; border-radius: 6px; border-left: 3px solid #ef4444;">
            ⚠️ <strong>Importante:</strong> Solo puedo responder preguntas sobre trámites municipales basándome en los documentos oficiales cargados.
        </p>
        """

    def _get_faq_message(self) -> str:
        """Mensaje de FAQ"""
        return """
        <h3 style="color: #3b82f6; margin-bottom: 15px;">❓ Preguntas Frecuentes</h3>

        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <strong>1. ¿Qué es una licencia de funcionamiento?</strong>
            <p>Es la autorización municipal para realizar actividades económicas en un establecimiento.</p>
        </div>

        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <strong>2. ¿Cuánto tiempo demora el trámite?</strong>
            <p>Depende del tipo: licencias automáticas (1 día), con inspección (15 días hábiles).</p>
        </div>

        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <strong>3. ¿Dónde presento los documentos?</strong>
            <p>En la Oficina de Trámite Documentario del municipio o virtualmente según disponibilidad.</p>
        </div>

        <p style="margin-top: 20px;"><strong>💬 Para consultas específicas, escribe tu pregunta directamente.</strong></p>
        """

    def _get_topics_message(self) -> str:
        """Mensaje de temas disponibles"""
        return """
        <h3 style="color: #10b981; margin-bottom: 15px;">📚 Temas Disponibles</h3>

        <div style="display: grid; gap: 15px;">
            <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong>🏪 Licencias de Funcionamiento</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Licencias para bodegas y comercio menor</li>
                    <li>Licencias para establecimientos medianos y grandes</li>
                    <li>Licencias provisionales</li>
                    <li>Requisitos y procedimientos</li>
                </ul>
            </div>

            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <strong>📋 Normativas Municipales</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Ordenanzas municipales</li>
                    <li>Ley de tributación municipal</li>
                    <li>Reglamentos y decretos</li>
                </ul>
            </div>

            <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; border-left: 4px solid #10b981;">
                <strong>📝 Formularios y Guías</strong>
                <ul style="margin: 10px 0 0 20px;">
                    <li>Formatos de solicitud</li>
                    <li>Guías paso a paso</li>
                    <li>Declaraciones juradas</li>
                </ul>
            </div>
        </div>

        <p style="margin-top: 20px;"><strong>💡 Escribe tu pregunta sobre cualquiera de estos temas.</strong></p>
        """

    def _get_rag_help_message(self) -> str:
        """Mensaje de ayuda sobre cómo usar el RAG"""
        return """
        <h3>De qué trata este sistema RAG</h3>

        <p>Este es un sistema de consulta inteligente que busca en documentos municipales para responder tus preguntas. Funciona en 3 pasos:</p>

        <ol>
            <li>Recibes tu pregunta y la analiza</li>
            <li>Busca los documentos más relevantes en la base de datos</li>
            <li>Genera una respuesta basándose en la información encontrada</li>
        </ol>

        <h4>Cómo hacer buenas preguntas</h4>

        <p><strong>Preguntas que funcionan bien:</strong></p>
        <ul>
            <li>"¿Qué requisitos necesito para una licencia de funcionamiento?"</li>
            <li>"¿Cuánto cuesta renovar una licencia comercial?"</li>
            <li>"¿Dónde puedo descargar el formulario de declaración jurada?"</li>
            <li>"¿Qué documentos necesito para abrir una bodega?"</li>
        </ul>

        <p><strong>Preguntas poco efectivas:</strong></p>
        <ul>
            <li>"Licencia" - Muy general, no especifica qué necesitas saber</li>
            <li>"Ayuda" - No indica sobre qué tema</li>
            <li>"Información" - Demasiado vago</li>
        </ul>

        <h4>Consejos para mejores resultados</h4>
        <ul>
            <li>Sé específico sobre el trámite que te interesa</li>
            <li>Menciona el tipo de negocio o establecimiento si aplica</li>
            <li>Pregunta por algo concreto: requisitos, costos, plazos, formularios</li>
            <li>Usa preguntas completas en lugar de palabras sueltas</li>
        </ul>

        <h4>Importante saber</h4>
        <ul>
            <li>Solo puedo responder con información que está en los documentos cargados</li>
            <li>No invento respuestas - si no encuentro información, te lo indicaré</li>
            <li>Entre más específica sea tu pregunta, mejor será la respuesta</li>
        </ul>
        """

    def _get_no_results_message(self) -> str:
        """Mensaje cuando no se encuentran resultados"""
        return """
        <div style="background: #fef2f2; padding: 20px; border-radius: 10px; border-left: 4px solid #ef4444;">
            <h3 style="color: #ef4444; margin-top: 0;">❌ No se encontraron resultados</h3>
            <p>Lo siento, no encontré información relevante para tu consulta en los documentos disponibles.</p>

            <p><strong>💡 Sugerencias:</strong></p>
            <ul>
                <li>Reformula tu pregunta con otros términos</li>
                <li>Sé más específico sobre el trámite que buscas</li>
                <li>Escribe <strong>"ayuda"</strong> para ver los temas disponibles</li>
            </ul>
        </div>
        """
