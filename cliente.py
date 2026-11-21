# Proyecto Software FJ - Curso Programación 213023 UNAD
"""Clase Cliente con encapsulación y validaciones estrictas."""
import re  # Expresiones regulares para validar formatos de texto

from entidad import EntidadBase  # Clase abstracta de la que hereda Cliente
from excepciones import ClienteInvalidoError, ParametroFaltanteError

# Patrón del nombre: solo letras (con tildes y ñ) y espacios
_PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")
# Patrón del correo: texto@dominio.extensión
_PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class Cliente(EntidadBase):
    """Cliente de Software FJ. Los datos personales son privados y solo
    se modifican a través de propiedades que validan el valor."""

    def __init__(self, nombre, documento, correo, telefono):
        super().__init__()  # Genera el id llamando al constructor del padre
        # Cada asignación activa el setter correspondiente, que valida
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono

    @staticmethod  # No usa 'self': es una función auxiliar de la clase
    def _requerido(valor, campo):
        """Verifica que el parámetro no falte."""
        # Falta si es None o es un texto vacío/solo espacios
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'")
        return str(valor).strip()  # Devuelve el valor limpio como texto

    @property  # Getter: lee el nombre
    def nombre(self):
        return self._nombre

    @nombre.setter  # Setter: valida antes de guardar el nombre
    def nombre(self, valor):
        valor = self._requerido(valor, "nombre")  # Comprueba que exista
        # Mínimo 3 caracteres y solo letras/espacios
        if len(valor) < 3 or not _PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(f"Nombre inválido: '{valor}'")
        self._nombre = valor  # Guarda en el atributo privado

    @property  # Getter del documento
    def documento(self):
        return self._documento

    @documento.setter  # Setter con validación del documento
    def documento(self, valor):
        valor = self._requerido(valor, "documento")
        # Debe ser numérico y tener entre 6 y 12 dígitos
        if not (valor.isdigit() and 6 <= len(valor) <= 12):
            raise ClienteInvalidoError(
                f"Documento inválido (6-12 dígitos): '{valor}'")
        self._documento = valor

    @property  # Getter del correo
    def correo(self):
        return self._correo

    @correo.setter  # Setter con validación del correo
    def correo(self, valor):
        valor = self._requerido(valor, "correo")
        # Debe cumplir el patrón de correo electrónico
        if not _PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"Correo inválido: '{valor}'")
        self._correo = valor

    @property  # Getter del teléfono
    def telefono(self):
        return self._telefono

    @telefono.setter  # Setter con validación del teléfono
    def telefono(self, valor):
        valor = self._requerido(valor, "telefono")
        # Debe ser numérico y de exactamente 10 dígitos
        if not (valor.isdigit() and len(valor) == 10):
            raise ClienteInvalidoError(
                f"Teléfono inválido (10 dígitos): '{valor}'")
        self._telefono = valor

    def describir(self) -> str:
        """Implementa el método abstracto de EntidadBase."""
        # Devuelve una línea de texto con todos los datos del cliente
        return (f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} "
                f"| {self.correo} | Tel: {self.telefono}")
