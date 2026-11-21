"""Clase abstracta Servicio y tres servicios especializados."""
from abc import ABC, abstractmethod  # Para definir clases/métodos abstractos
from functools import singledispatchmethod  # Sobrecarga según el tipo de dato

from entidad import EntidadBase  # Clase base de todas las entidades
from excepciones import (CalculoInconsistenteError, ParametroFaltanteError,
                         ServicioInvalidoError)

IVA = 0.19  # Impuesto por defecto (19 %)


class Servicio(EntidadBase, ABC):
    """Servicio genérico. Las subclases definen costo, descripción y
    validación de parámetros (polimorfismo)."""

    def __init__(self, nombre, tarifa_hora, disponible=True):
        super().__init__()  # Genera el id único
        # El nombre es obligatorio y no puede ser solo espacios
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("Falta el nombre del servicio")
        # La tarifa debe ser un número positivo
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise ServicioInvalidoError(
                f"Tarifa por hora inválida: {tarifa_hora!r}")
        self._nombre = str(nombre).strip()  # Atributo privado: nombre
        self._tarifa_hora = float(tarifa_hora)  # Atributo privado: tarifa
        self._disponible = bool(disponible)  # Atributo privado: disponibilidad

    @property  # Lectura del nombre
    def nombre(self):
        return self._nombre

    @property  # Lectura de la tarifa
    def tarifa_hora(self):
        return self._tarifa_hora

    @property  # Lectura de la disponibilidad
    def disponible(self):
        return self._disponible

    @disponible.setter  # Permite cambiar la disponibilidad
    def disponible(self, valor):
        self._disponible = bool(valor)  # Fuerza a True/False

    # ---- métodos abstractos (se sobrescriben en cada servicio) ----
    @abstractmethod
    def calcular_costo(self, horas) -> float:
        """Subtotal sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, horas) -> None:
        """Lanza ServicioInvalidoError si los parámetros no son válidos."""

    # ---- "sobrecarga" de métodos (Python usa parámetros opcionales) ----
    def calcular_costo_total(self, horas, impuesto=0.0, descuento=0.0):
        """Variantes de cálculo:
        - calcular_costo_total(h)                       -> subtotal
        - calcular_costo_total(h, impuesto=0.19)        -> con IVA
        - calcular_costo_total(h, 0.19, descuento=0.1)  -> IVA + descuento
        """
        self.validar_parametros(horas)  # Polimorfismo: cada hijo valida a su modo
        # Impuesto y descuento deben ser proporciones entre 0 y 1
        if not (0 <= impuesto <= 1) or not (0 <= descuento <= 1):
            raise CalculoInconsistenteError(
                "Impuesto y descuento deben estar entre 0 y 1")
        subtotal = self.calcular_costo(horas)  # Polimorfismo: costo del hijo
        # Aplica primero el descuento y luego el impuesto
        total = subtotal * (1 - descuento) * (1 + impuesto)
        if total <= 0:  # Un total no positivo es un cálculo inconsistente
            raise CalculoInconsistenteError(
                f"Total inconsistente: {total}")
        return round(total, 2)  # Redondea a 2 decimales

    @singledispatchmethod  # Elige la versión del método según el tipo del 1.er argumento
    def aplicar_descuento(self, descuento, monto):
        """Sobrecarga por tipo: float/int = porcentaje, str = código."""
        # Versión por defecto: tipo no soportado
        raise ServicioInvalidoError(
            f"Tipo de descuento no soportado: {type(descuento).__name__}")

    @aplicar_descuento.register(float)  # Se usa si 'descuento' es float...
    @aplicar_descuento.register(int)  # ...o int
    def _(self, descuento, monto):
        if not 0 <= descuento <= 100:  # Porcentaje válido: 0 a 100
            raise CalculoInconsistenteError("Porcentaje fuera de rango")
        return round(monto * (1 - descuento / 100), 2)  # Resta el porcentaje

    @aplicar_descuento.register(str)  # Se usa si 'descuento' es un texto
    def _(self, descuento, monto):
        codigos = {"PROMO10": 10, "PROMO20": 20}  # Códigos y su porcentaje
        if descuento not in codigos:  # Código desconocido
            raise ServicioInvalidoError(f"Código inválido: {descuento}")
        return round(monto * (1 - codigos[descuento] / 100), 2)

    @staticmethod  # Función auxiliar compartida por las subclases
    def _validar_horas(horas, minimo, maximo):
        if horas is None:  # No se envió la duración
            raise ParametroFaltanteError("Falta la duración")
        # Debe ser número (y no booleano, que en Python también es int)
        if not isinstance(horas, (int, float)) or isinstance(horas, bool):
            raise ServicioInvalidoError(f"Duración inválida: {horas!r}")
        if not minimo <= horas <= maximo:  # Debe estar en el rango permitido
            raise ServicioInvalidoError(
                f"La duración debe estar entre {minimo} y {maximo} horas")


class ReservaSala(Servicio):  # Hereda de Servicio
    """Reserva de salas de reuniones."""

    def __init__(self, nombre, tarifa_hora, capacidad, asistentes=1,
                 disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)  # Datos comunes
        # La capacidad debe ser un entero positivo
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}")
        self._capacidad = capacidad  # Máximo de personas de la sala
        self._asistentes = asistentes  # Personas que asistirán

    def validar_parametros(self, horas):  # Sobrescribe el método abstracto
        self._validar_horas(horas, 1, 12)  # Entre 1 y 12 horas
        if self._asistentes > self._capacidad:  # No exceder la capacidad
            raise ServicioInvalidoError(
                f"{self._asistentes} asistentes superan la capacidad "
                f"({self._capacidad})")

    def calcular_costo(self, horas):  # Sobrescribe el cálculo del costo
        return self.tarifa_hora * horas  # Tarifa por hora x horas

    def describir(self):  # Sobrescribe la descripción
        return (f"Sala '{self.nombre}' | capacidad {self._capacidad} | "
                f"${self.tarifa_hora:,.0f}/h")


class AlquilerEquipo(Servicio):  # Hereda de Servicio
    """Alquiler de equipos (con seguro opcional del 10 %)."""

    def __init__(self, nombre, tarifa_hora, tipo_equipo, seguro=False,
                 disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not tipo_equipo:  # El tipo de equipo es obligatorio
            raise ParametroFaltanteError("Falta el tipo de equipo")
        self._tipo_equipo = tipo_equipo  # Ej.: "Portátil", "Proyector"
        self._seguro = bool(seguro)  # True si incluye seguro

    def validar_parametros(self, horas):
        self._validar_horas(horas, 1, 72)  # Entre 1 y 72 horas

    def calcular_costo(self, horas):
        costo = self.tarifa_hora * horas  # Costo base
        return costo * 1.10 if self._seguro else costo  # +10 % si hay seguro

    def describir(self):
        seguro = "con seguro" if self._seguro else "sin seguro"
        return (f"Equipo '{self.nombre}' ({self._tipo_equipo}) {seguro} | "
                f"${self.tarifa_hora:,.0f}/h")


class AsesoriaEspecializada(Servicio):  # Hereda de Servicio
    """Asesoría con recargo según el nivel del experto."""

    # Multiplicador de la tarifa según el nivel del asesor
    _NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior",
                 disponible=True):
        super().__init__(nombre, tarifa_hora, disponible)
        if not especialidad:  # La especialidad es obligatoria
            raise ParametroFaltanteError("Falta la especialidad")
        if nivel not in self._NIVELES:  # El nivel debe existir en el diccionario
            raise ServicioInvalidoError(f"Nivel inválido: '{nivel}'")
        self._especialidad = especialidad  # Ej.: "Cloud"
        self._nivel = nivel  # junior / senior / experto

    def validar_parametros(self, horas):
        self._validar_horas(horas, 1, 8)  # Entre 1 y 8 horas

    def calcular_costo(self, horas):
        # Tarifa x horas x multiplicador del nivel
        return self.tarifa_hora * horas * self._NIVELES[self._nivel]

    def describir(self):
        return (f"Asesoría '{self.nombre}' de {self._especialidad} "
                f"(nivel {self._nivel}) | ${self.tarifa_hora:,.0f}/h")
