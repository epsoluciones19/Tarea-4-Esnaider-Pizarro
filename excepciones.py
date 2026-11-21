"""Excepciones personalizadas de Software FJ.

Todas heredan de ErrorSoftwareFJ para poder capturarlas de forma
unificada, sin perder la posibilidad de tratar cada caso por separado.
"""


# Excepción base: al heredar de Exception, es una excepción estándar de Python
class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema."""  # Docstring que documenta la clase
    # No necesita más código: 'Exception' ya aporta el comportamiento básico


# Se lanza cuando falta un dato obligatorio (None o texto vacío)
class ParametroFaltanteError(ErrorSoftwareFJ):
    """Se omitió un parámetro obligatorio (None o vacío)."""


# Se lanza cuando los datos de un cliente no cumplen las reglas
class ClienteInvalidoError(ErrorSoftwareFJ):
    """Los datos de un cliente no cumplen las validaciones."""


# Se lanza cuando los datos o parámetros de un servicio son incorrectos
class ServicioInvalidoError(ErrorSoftwareFJ):
    """Los datos o parámetros de un servicio son inválidos."""


# Se lanza cuando se intenta usar un servicio marcado como no disponible
class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio solicitado no está disponible."""


# Se lanza cuando una reserva no puede crearse o procesarse
class ReservaInvalidaError(ErrorSoftwareFJ):
    """La reserva no pudo crearse o procesarse correctamente."""


# Se lanza cuando una operación no es válida para el estado actual
class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """La operación no es válida para el estado actual del objeto."""


# Se lanza cuando un cálculo de costos da un resultado absurdo
class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Un cálculo de costos produjo un resultado inconsistente."""
