import re
from datetime import datetime


FORMATO_FECHA_RADICACION = "%Y-%m-%d %H:%M:%S"
PUNTUACION_ASUNTO = ".,;:!?¿¡'\"()-/"


def nombre_valido(nombre):
    """Comprueba longitud y caracteres permitidos para un nombre."""
    letras_permitidas = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        "ÁÉÍÓÚÑáéíóúñ"
    )
    return (
        3 <= len(nombre) <= 100
        and all(caracter in letras_permitidas or caracter in " '-" for caracter in nombre)
    )


def documento_valido(documento):
    """Comprueba que el documento tenga entre 3 y 15 dígitos."""
    return (
        3 <= len(documento) <= 15
        and documento.isascii()
        and documento.isdigit()
    )


def telefono_valido(telefono):
    """Comprueba que el teléfono tenga exactamente 10 dígitos."""
    return len(telefono) == 10 and telefono.isascii() and telefono.isdigit()


def correo_valido(correo):
    """Comprueba la estructura básica de un correo y su dominio."""
    if len(correo) > 254 or correo.count("@") != 1:
        return False

    usuario, dominio = correo.split("@")
    etiquetas_dominio = dominio.split(".")
    formato_usuario = r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    formato_dominio = (
        r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*"
        r"\.[A-Za-z]{2,}"
    )

    if not re.fullmatch(formato_usuario, usuario):
        return False
    if usuario.startswith(".") or usuario.endswith(".") or ".." in usuario:
        return False
    if len(dominio) > 253 or any(len(etiqueta) > 63 for etiqueta in etiquetas_dominio):
        return False
    return re.fullmatch(formato_dominio, dominio) is not None


def direccion_valida(direccion):
    """Permite letras, números, espacios y símbolos comunes de direcciones."""
    caracteres_permitidos = "#-./"
    return (
        5 <= len(direccion) <= 200
        and all(
            caracter.isalnum() or caracter == " " or caracter in caracteres_permitidos
            for caracter in direccion
        )
    )


def fecha_radicacion_valida(fecha_texto):
    """Comprueba que la fecha use el formato esperado y no sea futura."""
    try:
        fecha = datetime.strptime(fecha_texto, FORMATO_FECHA_RADICACION)
    except ValueError:
        return False

    return (
        fecha.strftime(FORMATO_FECHA_RADICACION) == fecha_texto
        and fecha <= datetime.now()
    )


def asunto_valido(asunto):
    """Comprueba longitud y caracteres permitidos para el asunto."""
    asunto = asunto.strip()
    return (
        5 <= len(asunto) <= 150
        and all(
            caracter.isalnum()
            or caracter == " "
            or caracter in PUNTUACION_ASUNTO
            for caracter in asunto
        )
    )


def descripcion_valida(descripcion):
    """Comprueba que la descripción tenga entre 20 y 2000 caracteres."""
    descripcion = descripcion.strip()
    return 20 <= len(descripcion) <= 2000
