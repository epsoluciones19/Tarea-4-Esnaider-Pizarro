# Proyecto Software FJ - Curso Programación 213023 UNAD
"""Configuración del archivo de logs (eventos y errores)."""
import logging  # Módulo estándar de Python para registrar mensajes
import os  # Módulo para trabajar con rutas y carpetas

# Carpeta 'logs' ubicada junto a este archivo (ruta absoluta)
RUTA_LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
# Ruta completa del archivo donde se guardarán los registros
ARCHIVO_LOG = os.path.join(RUTA_LOGS, "software_fj.log")


def obtener_logger() -> logging.Logger:
    """Devuelve un logger que escribe en archivo (y no duplica handlers)."""
    os.makedirs(RUTA_LOGS, exist_ok=True)  # Crea la carpeta si no existe
    logger = logging.getLogger("software_fj")  # Obtiene/crea el logger por nombre
    if not logger.handlers:  # Solo configura si aún no tiene destinos
        logger.setLevel(logging.INFO)  # Registra desde nivel INFO hacia arriba
        # Handler que escribe en el archivo, con codificación UTF-8 (tildes)
        handler = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")
        # Formato de cada línea: fecha | nivel | mensaje
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s"))
        logger.addHandler(handler)  # Conecta el handler al logger
    return logger  # Devuelve el logger ya configurado


# Logger global que importan los demás módulos para registrar eventos
log = obtener_logger()
