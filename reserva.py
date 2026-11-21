# Proyecto Software FJ - Curso Programación 213023 UNAD
"""Clase Reserva: integra cliente, servicio, duración y estado."""
from enum import Enum  # Para definir los estados como constantes

from cliente import Cliente
from entidad import EntidadBase
from excepciones import (ErrorSoftwareFJ, OperacionNoPermitidaError,
                         ReservaInvalidaError, ServicioInvalidoError,
                         ServicioNoDisponibleError)
from logger_fj import log  # Logger para registrar eventos
from servicios import IVA, Servicio


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""
    PENDIENTE = "PENDIENTE"  # Recién creada
    CONFIRMADA = "CONFIRMADA"  # Aprobada
    CANCELADA = "CANCELADA"  # Anulada
    PROCESADA = "PROCESADA"  # Cobrada


class Reserva(EntidadBase):
    def __init__(self, cliente, servicio, horas):
        super().__init__()  # Genera el id
        # El cliente debe ser un objeto Cliente
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un Cliente válido")
        # El servicio debe ser un objeto Servicio
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un Servicio válido")
        try:
            servicio.validar_parametros(horas)  # Valida duración, etc.
        except ServicioInvalidoError as e:
            # Encadenamiento de excepciones: 'from e' conserva la causa original
            raise ReservaInvalidaError(
                f"No se puede reservar '{servicio.nombre}'") from e
        self._cliente = cliente  # Cliente que reserva
        self._servicio = servicio  # Servicio reservado
        self._horas = horas  # Duración en horas
        self._estado = EstadoReserva.PENDIENTE  # Estado inicial

    @property  # Lectura del estado
    def estado(self):
        return self._estado

    @property  # Lectura del cliente
    def cliente(self):
        return self._cliente

    @property  # Lectura del servicio
    def servicio(self):
        return self._servicio

    def confirmar(self):
        # Solo se puede confirmar una reserva pendiente
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva {self._estado.value}")
        # El servicio debe estar disponible
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"'{self._servicio.nombre}' no está disponible")
        self._estado = EstadoReserva.CONFIRMADA  # Cambia el estado
        log.info("Reserva #%s confirmada", self.id)  # Registra el evento

    def cancelar(self):
        # No se cancela una reserva ya cancelada o procesada
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self._estado.value}")
        self._estado = EstadoReserva.CANCELADA
        log.info("Reserva #%s cancelada", self.id)

    def procesar(self, descuento=0.0):
        """Procesa la reserva y devuelve el total con IVA."""
        try:  # Bloque donde puede ocurrir un error
            # Solo se procesan reservas confirmadas
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    "Solo se procesan reservas CONFIRMADAS")
            # Calcula el total con IVA y descuento opcional
            total = self._servicio.calcular_costo_total(
                self._horas, impuesto=IVA, descuento=descuento)
        except ErrorSoftwareFJ as e:  # Captura cualquier error del sistema
            log.error("Fallo al procesar reserva #%s: %s", self.id, e)
            # Relanza con un mensaje más claro, conservando la causa (from e)
            raise ReservaInvalidaError(
                f"No se pudo procesar la reserva #{self.id}") from e
        else:
            # Solo se ejecuta si NO hubo excepción
            self._estado = EstadoReserva.PROCESADA
            log.info("Reserva #%s procesada. Total: $%s", self.id, total)
            return total
        finally:
            # Se ejecuta SIEMPRE, haya o no error
            log.info("Fin del intento de procesamiento de reserva #%s",
                     self.id)

    def describir(self):
        """Resumen de la reserva en una línea."""
        return (f"Reserva #{self.id} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._horas}h | "
                f"{self._estado.value}")
