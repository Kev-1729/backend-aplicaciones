"""
Tests para la entidad Feedback y ExactitudMetrics
"""
import pytest
from datetime import datetime
from domain.entities.feedback import Feedback, ExactitudMetrics


class TestFeedback:
    """Tests para la entidad Feedback"""

    def test_create_basic_feedback(self):
        """Prueba creación básica de feedback"""
        feedback = Feedback(
            query="¿Cómo solicitar una licencia?",
            answer="Debes presentar DNI y formulario."
        )

        assert feedback.query == "¿Cómo solicitar una licencia?"
        assert feedback.answer == "Debes presentar DNI y formulario."
        assert feedback.is_correct is None
        assert feedback.rating is None
        assert feedback.created_at is not None
        assert feedback.updated_at is not None

    def test_create_feedback_with_all_fields(self):
        """Prueba creación de feedback con todos los campos"""
        now = datetime.now()
        feedback = Feedback(
            query="¿Requisitos?",
            answer="DNI y RUC",
            session_id="session-123",
            message_id="msg-456",
            is_correct=True,
            rating=5,
            comment="Muy útil",
            sources=["doc1.pdf", "doc2.pdf"],
            chunks_count=3,
            similarity_threshold=0.85,
            created_at=now,
            updated_at=now,
            metadata={"key": "value"}
        )

        assert feedback.session_id == "session-123"
        assert feedback.message_id == "msg-456"
        assert feedback.is_correct is True
        assert feedback.rating == 5
        assert feedback.comment == "Muy útil"
        assert len(feedback.sources) == 2
        assert feedback.chunks_count == 3
        assert feedback.similarity_threshold == 0.85
        assert feedback.metadata == {"key": "value"}

    def test_empty_query_raises_error(self):
        """Prueba que query vacía lanza error"""
        with pytest.raises(ValueError, match="La query no puede estar vacía"):
            Feedback(query="", answer="Respuesta")

    def test_whitespace_query_raises_error(self):
        """Prueba que query con solo espacios lanza error"""
        with pytest.raises(ValueError, match="La query no puede estar vacía"):
            Feedback(query="   ", answer="Respuesta")

    def test_empty_answer_raises_error(self):
        """Prueba que respuesta vacía lanza error"""
        with pytest.raises(ValueError, match="La respuesta no puede estar vacía"):
            Feedback(query="Pregunta", answer="")

    def test_whitespace_answer_raises_error(self):
        """Prueba que respuesta con solo espacios lanza error"""
        with pytest.raises(ValueError, match="La respuesta no puede estar vacía"):
            Feedback(query="Pregunta", answer="   ")

    def test_invalid_rating_raises_error(self):
        """Prueba que rating inválido lanza error"""
        with pytest.raises(ValueError, match="El rating debe ser un entero entre 1 y 5"):
            Feedback(query="Pregunta", answer="Respuesta", rating=6)

    def test_invalid_rating_zero_raises_error(self):
        """Prueba que rating cero lanza error"""
        with pytest.raises(ValueError, match="El rating debe ser un entero entre 1 y 5"):
            Feedback(query="Pregunta", answer="Respuesta", rating=0)

    def test_invalid_rating_negative_raises_error(self):
        """Prueba que rating negativo lanza error"""
        with pytest.raises(ValueError, match="El rating debe ser un entero entre 1 y 5"):
            Feedback(query="Pregunta", answer="Respuesta", rating=-1)

    def test_mark_as_correct(self):
        """Prueba marcar feedback como correcto"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        old_updated_at = feedback.updated_at

        feedback.mark_as_correct()

        assert feedback.is_correct is True
        assert feedback.updated_at > old_updated_at

    def test_mark_as_incorrect(self):
        """Prueba marcar feedback como incorrecto"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        old_updated_at = feedback.updated_at

        feedback.mark_as_incorrect()

        assert feedback.is_correct is False
        assert feedback.updated_at > old_updated_at

    def test_set_rating_valid(self):
        """Prueba establecer rating válido"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        old_updated_at = feedback.updated_at

        feedback.set_rating(4)

        assert feedback.rating == 4
        assert feedback.updated_at > old_updated_at

    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    def test_set_rating_all_valid_values(self, rating):
        """Prueba todos los valores válidos de rating"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        feedback.set_rating(rating)
        assert feedback.rating == rating

    def test_set_rating_invalid(self):
        """Prueba establecer rating inválido"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")

        with pytest.raises(ValueError, match="El rating debe ser un entero entre 1 y 5"):
            feedback.set_rating(6)

    def test_set_rating_invalid_type(self):
        """Prueba establecer rating con tipo inválido"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")

        with pytest.raises(ValueError, match="El rating debe ser un entero entre 1 y 5"):
            feedback.set_rating("5")

    def test_add_comment(self):
        """Prueba agregar comentario"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        old_updated_at = feedback.updated_at

        feedback.add_comment("Excelente respuesta")

        assert feedback.comment == "Excelente respuesta"
        assert feedback.updated_at > old_updated_at

    def test_add_comment_strips_whitespace(self):
        """Prueba que agregar comentario elimina espacios"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")

        feedback.add_comment("  Comentario con espacios  ")

        assert feedback.comment == "Comentario con espacios"

    def test_add_comment_empty_not_saved(self):
        """Prueba que comentario vacío no se guarda"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        old_updated_at = feedback.updated_at

        feedback.add_comment("   ")

        assert feedback.comment is None
        assert feedback.updated_at == old_updated_at

    def test_is_evaluated_true(self):
        """Prueba is_evaluated cuando está evaluado"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", is_correct=True)
        assert feedback.is_evaluated() is True

    def test_is_evaluated_false(self):
        """Prueba is_evaluated cuando no está evaluado"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        assert feedback.is_evaluated() is False

    def test_is_positive_true(self):
        """Prueba is_positive cuando es positivo"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", is_correct=True)
        assert feedback.is_positive() is True

    def test_is_positive_false(self):
        """Prueba is_positive cuando no es positivo"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", is_correct=False)
        assert feedback.is_positive() is False

    def test_is_negative_true(self):
        """Prueba is_negative cuando es negativo"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", is_correct=False)
        assert feedback.is_negative() is True

    def test_is_negative_false(self):
        """Prueba is_negative cuando no es negativo"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", is_correct=True)
        assert feedback.is_negative() is False

    def test_has_rating_true(self):
        """Prueba has_rating cuando tiene rating"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", rating=5)
        assert feedback.has_rating() is True

    def test_has_rating_false(self):
        """Prueba has_rating cuando no tiene rating"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        assert feedback.has_rating() is False

    def test_has_comment_true(self):
        """Prueba has_comment cuando tiene comentario"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", comment="Bueno")
        assert feedback.has_comment() is True

    def test_has_comment_false(self):
        """Prueba has_comment cuando no tiene comentario"""
        feedback = Feedback(query="Pregunta", answer="Respuesta")
        assert feedback.has_comment() is False

    def test_has_comment_false_empty(self):
        """Prueba has_comment cuando comentario está vacío"""
        feedback = Feedback(query="Pregunta", answer="Respuesta", comment="")
        assert feedback.has_comment() is False

    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        now = datetime.now()
        feedback = Feedback(
            query="Pregunta",
            answer="Respuesta",
            session_id="session-123",
            is_correct=True,
            rating=5,
            created_at=now,
            updated_at=now
        )

        result = feedback.to_dict()

        assert result['query'] == "Pregunta"
        assert result['answer'] == "Respuesta"
        assert result['session_id'] == "session-123"
        assert result['is_correct'] is True
        assert result['rating'] == 5
        assert result['created_at'] == now.isoformat()
        assert result['updated_at'] == now.isoformat()
        assert result['metadata'] == {}

    def test_to_dict_with_metadata(self):
        """Prueba conversión a diccionario con metadata"""
        feedback = Feedback(
            query="Pregunta",
            answer="Respuesta",
            metadata={"custom": "data"}
        )

        result = feedback.to_dict()

        assert result['metadata'] == {"custom": "data"}


class TestExactitudMetrics:
    """Tests para ExactitudMetrics"""

    def test_create_metrics(self):
        """Prueba creación básica de métricas"""
        metrics = ExactitudMetrics(
            total_evaluaciones=100,
            respuestas_correctas=85,
            respuestas_incorrectas=15,
            sin_evaluar=20,
            exactitud_porcentaje=85.0
        )

        assert metrics.total_evaluaciones == 100
        assert metrics.respuestas_correctas == 85
        assert metrics.respuestas_incorrectas == 15
        assert metrics.sin_evaluar == 20
        assert metrics.exactitud_porcentaje == 85.0

    def test_negative_total_raises_error(self):
        """Prueba que total negativo lanza error"""
        with pytest.raises(ValueError, match="total_evaluaciones no puede ser negativo"):
            ExactitudMetrics(
                total_evaluaciones=-1,
                respuestas_correctas=0,
                respuestas_incorrectas=0,
                sin_evaluar=0,
                exactitud_porcentaje=0.0
            )

    def test_negative_correctas_raises_error(self):
        """Prueba que respuestas correctas negativas lanzan error"""
        with pytest.raises(ValueError, match="Las cantidades no pueden ser negativas"):
            ExactitudMetrics(
                total_evaluaciones=10,
                respuestas_correctas=-1,
                respuestas_incorrectas=0,
                sin_evaluar=0,
                exactitud_porcentaje=0.0
            )

    def test_negative_incorrectas_raises_error(self):
        """Prueba que respuestas incorrectas negativas lanzan error"""
        with pytest.raises(ValueError, match="Las cantidades no pueden ser negativas"):
            ExactitudMetrics(
                total_evaluaciones=10,
                respuestas_correctas=0,
                respuestas_incorrectas=-1,
                sin_evaluar=0,
                exactitud_porcentaje=0.0
            )

    def test_exactitud_below_zero_raises_error(self):
        """Prueba que exactitud menor a 0 lanza error"""
        with pytest.raises(ValueError, match="La exactitud debe estar entre 0 y 100"):
            ExactitudMetrics(
                total_evaluaciones=10,
                respuestas_correctas=5,
                respuestas_incorrectas=5,
                sin_evaluar=0,
                exactitud_porcentaje=-1.0
            )

    def test_exactitud_above_100_raises_error(self):
        """Prueba que exactitud mayor a 100 lanza error"""
        with pytest.raises(ValueError, match="La exactitud debe estar entre 0 y 100"):
            ExactitudMetrics(
                total_evaluaciones=10,
                respuestas_correctas=5,
                respuestas_incorrectas=5,
                sin_evaluar=0,
                exactitud_porcentaje=101.0
            )

    @pytest.mark.parametrize("exactitud,expected_label", [
        (95.0, "Excelente"),
        (90.0, "Excelente"),
        (89.9, "Buena"),
        (85.0, "Buena"),
        (75.0, "Buena"),
        (74.9, "Regular"),
        (65.0, "Regular"),
        (60.0, "Regular"),
        (59.9, "Necesita mejora"),
        (50.0, "Necesita mejora"),
        (0.0, "Necesita mejora"),
    ])
    def test_get_exactitud_label(self, exactitud, expected_label):
        """Prueba etiquetas de exactitud para diferentes valores"""
        metrics = ExactitudMetrics(
            total_evaluaciones=100,
            respuestas_correctas=int(exactitud),
            respuestas_incorrectas=int(100-exactitud),
            sin_evaluar=0,
            exactitud_porcentaje=exactitud
        )

        assert metrics.get_exactitud_label() == expected_label

    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        metrics = ExactitudMetrics(
            total_evaluaciones=100,
            respuestas_correctas=85,
            respuestas_incorrectas=15,
            sin_evaluar=20,
            exactitud_porcentaje=85.5,
            rating_promedio=4.3
        )

        result = metrics.to_dict()

        assert result['total_evaluaciones'] == 100
        assert result['respuestas_correctas'] == 85
        assert result['respuestas_incorrectas'] == 15
        assert result['sin_evaluar'] == 20
        assert result['exactitud_porcentaje'] == 85.5
        assert result['rating_promedio'] == 4.3
        assert result['exactitud_label'] == "Buena"

    def test_to_dict_without_rating(self):
        """Prueba conversión a diccionario sin rating promedio"""
        metrics = ExactitudMetrics(
            total_evaluaciones=100,
            respuestas_correctas=90,
            respuestas_incorrectas=10,
            sin_evaluar=0,
            exactitud_porcentaje=90.0
        )

        result = metrics.to_dict()

        assert result['rating_promedio'] is None
        assert result['exactitud_label'] == "Excelente"

    def test_to_dict_rounds_decimals(self):
        """Prueba que to_dict redondea decimales"""
        metrics = ExactitudMetrics(
            total_evaluaciones=100,
            respuestas_correctas=85,
            respuestas_incorrectas=15,
            sin_evaluar=0,
            exactitud_porcentaje=85.666666,
            rating_promedio=4.333333
        )

        result = metrics.to_dict()

        assert result['exactitud_porcentaje'] == 85.67
        assert result['rating_promedio'] == 4.33
