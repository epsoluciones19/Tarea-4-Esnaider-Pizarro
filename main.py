"""Software FJ - Sistema integral de gestión de clientes, servicios y
reservas. Ejecuta una simulación de operaciones (válidas e inválidas)."""
from cliente import Cliente
from excepciones import ErrorSoftwareFJ, ReservaInvalidaError
from logger_fj import ARCHIVO_LOG, log
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


class GestorFJ:
    """Administra las listas internas."""

    def __init__(self):
        # Tres listas en memoria: clientes, servicios y reservas
        self.clientes, self.servicios, self.reservas = [], [], []

    def _ejecutar(self, titulo, funcion, *args, **kwargs):
        """Ejecuta una operación; ante cualquier error lo registra y el
        programa continúa."""
        print(f"\n>> {titulo}")  # Muestra el nombre de la operación
        try:
            resultado = funcion(*args, **kwargs)  # Ejecuta la operación
        except ErrorSoftwareFJ as e:  # Errores propios del sistema
            # Si hay causa encadenada, la mostramos
            causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
            print(f"   [ERROR CONTROLADO] {e}{causa}")
            log.error("%s | %s%s", titulo, e, causa)  # Registra en el log
            return None
        except Exception as e:  # Cualquier error inesperado: no se cae
            print(f"   [ERROR INESPERADO] {type(e).__name__}: {e}")
            log.critical("%s | inesperado: %r", titulo, e)
            return None
        else:
            # Solo si no hubo error: muestra el resultado
            print(f"   [OK] {resultado if resultado is not None else ''}")
            log.info("%s | OK", titulo)
            return resultado
        finally:
            # Siempre se ejecuta, con o sin error
            log.info("Operación finalizada: %s", titulo)

    def registrar_cliente(self, *datos):
        c = Cliente(*datos)  # Puede lanzar ClienteInvalidoError
        self.clientes.append(c)  # Solo se agrega si fue válido
        return c.describir()

    def registrar_servicio(self, clase, *args, **kwargs):
        s = clase(*args, **kwargs)  # Crea el servicio indicado (polimorfismo)
        self.servicios.append(s)
        return s.describir()

    def reservar(self, cliente, servicio, horas, confirmar=True):
        if isinstance(horas, str):  # Si la duración llegó como texto...
            try:
                horas = float(horas)  # ...intenta convertirla a número
            except ValueError as e:
                # Encadena el error original de Python con el del sistema
                raise ReservaInvalidaError(
                    f"Duración no numérica: '{horas}'") from e
        r = Reserva(cliente, servicio, horas)  # Crea la reserva (valida)
        self.reservas.append(r)
        if confirmar:
            r.confirmar()  # Confirma (puede fallar si no hay disponibilidad)
        return r.describir()


def main():
    log.info("===== INICIO DE SIMULACIÓN =====")
    g = GestorFJ()  # Crea el gestor con sus listas vacías

    # 1-4: clientes (válidos e inválidos)
    g._ejecutar("1. Cliente válido", g.registrar_cliente,
                "Esnaider Pizarro MEza", "1083003685", "epsoluciones19@gmail.com", "3101234567")
    g._ejecutar("2. Cliente con correo inválido", g.registrar_cliente,
                "Margarita Lopez", "79876543", "mrlopez-p", "333274651")
    g._ejecutar("3. Cliente sin nombre", g.registrar_cliente,
                None, "57438338", "you@bangla.com", "3003001122")
    g._ejecutar("4. Segundo cliente válido", g.registrar_cliente,
                "Mariana Pizarro", "8704348", "mlope@cgmail.com", "3159998877")

    # 5-8: servicios (válidos e inválidos)
    g._ejecutar("5. Sala válida", g.registrar_servicio, ReservaSala,
                "Sala Entrenosotros", 50000, 10, 6)
    g._ejecutar("6. Equipo con tarifa negativa", g.registrar_servicio,
                AlquilerEquipo, "Portátil ProMax", -100, "Portátil")
    g._ejecutar("7. Asesoría válida", g.registrar_servicio,
                AsesoriaEspecializada, "Arquitectura Cloud", 80000,
                "Cloud", "experto")
    g._ejecutar("8. Equipo válido", g.registrar_servicio, AlquilerEquipo,
                "Proyector 4K", 20000, "Proyector", True)

    # Recupera los objetos creados válidamente (los inválidos no se guardaron)
    ana, carlos = g.clientes[0], g.clientes[1]
    sala, asesoria, equipo = g.servicios[0], g.servicios[1], g.servicios[2]

    # 9-12: reservas exitosas y fallidas
    g._ejecutar("9. Reserva exitosa de sala", g.reservar, ana, sala, 3)
    g._ejecutar("10. Reserva con duración excesiva", g.reservar,
                carlos, asesoria, 20)
    g._ejecutar("11. Reserva con duración no numérica", g.reservar,
                carlos, equipo, "abc")
    equipo.disponible = False  # Simula que el equipo deja de estar disponible
    g._ejecutar("12. Reserva con servicio no disponible", g.reservar,
                carlos, equipo, 5)
    equipo.disponible = True  # Vuelve a estar disponible

    # Procesamiento y cancelación
    r_ok = g.reservas[0]  # Primera reserva (la exitosa)
    g._ejecutar("13. Procesar reserva con IVA y 10% desc.",
                r_ok.procesar, descuento=0.10)
    g._ejecutar("14. Cancelar reserva ya procesada", r_ok.cancelar)
    # Reserva y cancela en una sola operación
    g._ejecutar("15. Reservar y cancelar asesoría", lambda: (
        g.reservar(carlos, asesoria, 2) and g.reservas[-1].cancelar()))
    g._ejecutar("16. Procesar reserva cancelada",
                g.reservas[-1].procesar)

    # Demostración de sobrecarga (distintas variantes del cálculo)
    print("\n>> Variantes de cálculo de costo (sala, 3h)")
    print("   Subtotal         :", sala.calcular_costo_total(3))
    print("   Con IVA          :", sala.calcular_costo_total(3, 0.19))
    print("   Con IVA y desc.  :", sala.calcular_costo_total(3, 0.19, 0.10))
    print("   Desc. 15% sobre 100000:", sala.aplicar_descuento(15, 100000))
    print("   Código PROMO20 sobre 100000:",
          sala.aplicar_descuento("PROMO20", 100000))

    print("\n== Reservas registradas ==")
    for r in g.reservas:  # Recorre la lista de reservas
        print("  ", r.describir())

    log.info("===== FIN DE SIMULACIÓN =====")
    print(f"\nSimulación terminada sin interrupciones. Log: {ARCHIVO_LOG}")


# Solo ejecuta main() si el archivo se corre directamente (no al importarlo)
if __name__ == "__main__":
    main()
