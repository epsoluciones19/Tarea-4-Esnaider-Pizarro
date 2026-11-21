"""Clase abstracta que representa las entidades generales del sistema."""
import itertools  # Para generar números consecutivos (ids)
from abc import ABC, abstractmethod  # Herramientas para clases abstractas


class EntidadBase(ABC):  # ABC convierte esta clase en abstracta
    """Toda entidad (Cliente, Servicio, Reserva) tiene un id único y
    debe saber describirse a sí misma."""

    # Contador compartido por todas las entidades: 1, 2, 3, ...
    _contador = itertools.count(1)

    def __init__(self):
        # Toma el siguiente número del contador; '_id' es atributo privado
        self._id = next(EntidadBase._contador)

    @property  # Permite leer 'entidad.id' como si fuera un atributo
    def id(self) -> int:
        """Identificador de solo lectura."""
        return self._id  # No hay setter: el id no se puede modificar

    @abstractmethod  # Obliga a las subclases a implementar este método
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
