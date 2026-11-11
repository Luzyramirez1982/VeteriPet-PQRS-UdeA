import os
import textwrap
import unicodedata
from datetime import datetime, timedelta

from archivos import (
    ARCHIVOS_PQRS,
    CARPETA_DATOS,
    actualizar_estado_pqrs,
    cargar_registros,
    crear_registro_plano,
    guardar_registro_plano,
    siguiente_id_tipo,
)
from reportes import generar_estadisticas
from validaciones import (
    FORMATO_FECHA_RADICACION,
    asunto_valido,
    correo_valido,
    descripcion_valida,
    direccion_valida,
    documento_valido,
    fecha_radicacion_valida,
    nombre_valido,
    telefono_valido,
)

ANCHO_COMPROBANTE = 120

TIPOS_DOCUMENTO = {
    "Cédula de ciudadanía (CC)": "CC",
    "Tarjeta de identidad (TI)": "TI",
    "Cédula de extranjería (CE)": "CE",
    "Pasaporte (PP)": "PP",
    "NIT": "NIT",
}
TIPOS_MASCOTA = ["Perro", "Gato"]
CAMPUS_UDEA = [
    "Campus Medellín - Ciudad Universitaria",
    "Campus Medellín - Ciudadela Robledo",
    "Campus en el Área de la salud",
    "Campus Medellín - Sede de Posgrado",
    "Campus Medellín - Edificio San Ignacio",
    "Campus Medellín - Antigua Escuela de Derecho",
    "Campus Medellín - Edificio Antioquia",
    "Campus Medellín - Casas Patrimoniales",
    "Campus Medellín - Edificio de Extensión",
]
ESTADOS_PQRS = ["Registrada", "En proceso", "Solucionada"]


def pedir_texto(mensaje):
    """Solicita un texto que no esté vacío."""
    while True:
        respuesta = input(mensaje).strip()
        if respuesta:
            return respuesta
        print("Este campo es obligatorio. Intenta de nuevo.")


def pedir_texto_validado(mensaje, es_valido, mensaje_error, opcional=False):
    """Repite la pregunta hasta recibir un texto válido."""
    while True:
        respuesta = input(mensaje).strip()
        if opcional and not respuesta:
            return ""
        if es_valido(respuesta):
            return respuesta
        print(mensaje_error)


def pedir_opcion(mensaje, opciones):
    """Muestra opciones numeradas y devuelve la opción elegida."""
    while True:
        print(mensaje)
        for numero, opcion in enumerate(opciones, start=1):
            print(f"{numero}. {opcion}")

        seleccion = input("Elige una opción: ").strip()
        if seleccion.isdigit():
            numero = int(seleccion)
            if 1 <= numero <= len(opciones):
                return opciones[numero - 1]

        print("Opción no válida. Intenta de nuevo.\n")


def texto_ascii(texto):
    """Convierte texto a ASCII y reemplaza saltos de línea por espacios."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return " ".join(texto.split())


def agregar_linea_comprobante(lineas, texto="", centrar=False):
    """Agrega una o más líneas de contenido dentro del marco de 120 columnas."""
    contenido = texto_ascii(texto)
    if not contenido:
        lineas.append("|" + " " * (ANCHO_COMPROBANTE - 2) + "|")
        return

    if centrar:
        partes = textwrap.wrap(contenido, width=ANCHO_COMPROBANTE - 4)
        lineas.extend(
            "| " + parte.center(ANCHO_COMPROBANTE - 4) + " |"
            for parte in partes
        )
        return

    partes = textwrap.wrap(
        contenido,
        width=ANCHO_COMPROBANTE - 4,
        subsequent_indent="    ",
        break_long_words=True,
        break_on_hyphens=False,
    )
    lineas.extend(
        "| " + parte.ljust(ANCHO_COMPROBANTE - 4) + " |"
        for parte in partes
    )


def generar_comprobante(registro):
    """Crea el comprobante ASCII con ancho fijo de 120 caracteres."""
    borde = "+" + "-" * (ANCHO_COMPROBANTE - 2) + "+"
    lineas = [borde]

    agregar_linea_comprobante(lineas, "COMPROBANTE DE RADICACION PQRS", centrar=True)
    agregar_linea_comprobante(
        lineas,
        "UNIVERSIDAD DE ANTIOQUIA - SISTEMA DE GESTION PQRS",
        centrar=True,
    )
    agregar_linea_comprobante(lineas)
    agregar_linea_comprobante(lineas, "DATOS DEL RADICADO", centrar=True)

    id_registro = registro.get("id", "N/A")
    if isinstance(id_registro, int) and not isinstance(id_registro, bool):
        id_registro = f"{id_registro:06d}"
    campos = [
        ("ID DE REGISTRO", id_registro),
        ("RADICADO", registro.get("radicado", "N/A")),
        ("FECHA Y HORA DE RADICACION", registro.get("fecha_radicacion", "N/A")),
        ("ESTADO DE LA PQRS", registro.get("estado_peticion", "Registrada")),
        ("FECHA MAXIMA DE RESPUESTA", registro.get("fecha_maxima_respuesta", "N/A")),
    ]
    for etiqueta, valor in campos:
        agregar_linea_comprobante(lineas, f"{etiqueta}: {valor}")

    agregar_linea_comprobante(lineas)
    agregar_linea_comprobante(lineas, "DATOS DEL SOLICITANTE", centrar=True)
    direccion = registro.get("direccion") or "N/A"
    campos = [
        ("NOMBRE COMPLETO", registro.get("nombre_completo", "N/A")),
        ("TIPO DE DOCUMENTO", registro.get("tipo_documento", "N/A")),
        ("NUMERO DE DOCUMENTO", registro.get("numero_documento", "N/A")),
        (
            "TELEFONO DE CONTACTO",
            f"{registro.get('tipo_telefono', 'N/A')} - "
            f"{registro.get('telefono_contacto', 'N/A')}",
        ),
        ("CORREO ELECTRONICO", registro.get("correo_electronico", "N/A")),
        ("DIRECCION", direccion),
    ]
    for etiqueta, valor in campos:
        agregar_linea_comprobante(lineas, f"{etiqueta}: {valor}")

    agregar_linea_comprobante(lineas)
    agregar_linea_comprobante(lineas, "CLASIFICACION", centrar=True)
    campos = [
        ("TIPO DE SOLICITUD", registro.get("tipo_solicitud", "N/A")),
        ("CANAL DE RECEPCION", registro.get("canal_recepcion", "N/A")),
        ("TIPO DE MASCOTA", registro.get("tipo_mascota", "N/A")),
        ("CAMPUS RELACIONADO", registro.get("campus_relacionado", "N/A")),
    ]
    for etiqueta, valor in campos:
        agregar_linea_comprobante(lineas, f"{etiqueta}: {valor}")

    agregar_linea_comprobante(lineas)
    agregar_linea_comprobante(lineas, "RESUMEN DE LA SOLICITUD", centrar=True)
    agregar_linea_comprobante(
        lineas,
        f"ASUNTO / TITULO: {registro.get('asunto_titulo', 'N/A')}",
    )
    agregar_linea_comprobante(lineas)
    agregar_linea_comprobante(
        lineas,
        "Este comprobante certifica el registro de la solicitud en el sistema PQRS.",
        centrar=True,
    )
    lineas.append(borde)

    return "\n".join(lineas) + "\n"


def imprimir_comprobante(registro, sufijo=""):
    """Guarda el comprobante TXT y también lo imprime en la consola."""
    tipo_archivo = os.path.splitext(
        ARCHIVOS_PQRS[registro["tipo_solicitud"]]
    )[0]
    id_registro = registro.get("id", 0)
    nombre_archivo = f"Radicado_{tipo_archivo}_{id_registro:06d}{sufijo}.txt"
    ruta_archivo = os.path.join(CARPETA_DATOS, nombre_archivo)
    comprobante = generar_comprobante(registro)

    with open(ruta_archivo, "w", encoding="ascii", newline="\n") as archivo:
        archivo.write(comprobante)

    print("\n" + comprobante)
    print(f"Comprobante guardado en: {ruta_archivo}\n")


def registrar_pqrs():
    """Pide los datos, calcula las fechas y guarda la PQRS en un archivo plano."""
    print("\n--- Registrar una nueva PQRS ---")

    # Primero reunimos los datos personales del solicitante.
    nombre = pedir_texto_validado(
        "Nombre completo: ",
        nombre_valido,
        "Usa de 3 a 100 caracteres: solo letras, espacios, apóstrofes o guiones.",
    )
    tipo_documento = pedir_opcion(
        "\nTipo de documento:",
        list(TIPOS_DOCUMENTO.keys()),
    )
    numero_documento = pedir_texto_validado(
        "Número de documento: ",
        documento_valido,
        "El documento debe tener entre 3 y 15 dígitos, sin letras ni símbolos.",
    )
    tipo_telefono = pedir_opcion(
        "\nTipo de teléfono:",
        ["Celular", "Fijo", "Corporativo", "Otro"],
    )
    telefono = pedir_texto_validado(
        "Teléfono de contacto: ",
        telefono_valido,
        "El teléfono debe tener exactamente 10 dígitos.",
    )
    correo = pedir_texto_validado(
        "Correo electrónico: ",
        correo_valido,
        "Escribe un correo válido, por ejemplo usuario@correo.com "
        "(máximo 254 caracteres).",
    )
    direccion = pedir_texto_validado(
        "Dirección (opcional, presiona Enter para omitir): ",
        direccion_valida,
        "La dirección debe tener entre 5 y 200 caracteres y usar solo letras, "
        "números, espacios o # - . /.",
        opcional=True,
    )

    solicitante = {
        "nombre": nombre,
        "tipo_documento": TIPOS_DOCUMENTO[tipo_documento],
        "numero_documento": numero_documento,
        "tipo_telefono": tipo_telefono,
        "telefono": telefono,
        "correo": correo,
        "direccion": direccion,
    }

    # Luego pedimos la información específica de la solicitud.
    tipo = pedir_opcion(
        "\nTipo de solicitud:",
        ["Petición", "Queja", "Reclamo", "Sugerencia"],
    )
    canal = pedir_opcion(
        "\nCanal de recepción:",
        [
            "Presencial",
            "Correo electrónico",
            "Página web",
            "Teléfono",
            "Redes sociales",
            "Otro",
        ],
    )
    relacionado_con = pedir_opcion(
        "\nTipo de mascota relacionada:",
        TIPOS_MASCOTA,
    )
    campus = pedir_opcion(
        "\nCampus relacionado:",
        CAMPUS_UDEA,
    )
    asunto = pedir_texto_validado(
        "Asunto o título: ",
        asunto_valido,
        "El asunto debe tener entre 5 y 150 caracteres y contener solo letras, "
        "números, espacios o puntuación básica.",
    )
    descripcion = pedir_texto_validado(
        "Descripción detallada: ",
        descripcion_valida,
        "La descripción debe tener entre 20 y 2000 caracteres.",
    )

    # La fecha límite se calcula sumando 30 días calendario a la radicación.
    fecha_radicacion = datetime.now().replace(microsecond=0)
    fecha_radicacion_texto = fecha_radicacion.strftime(FORMATO_FECHA_RADICACION)
    if not fecha_radicacion_valida(fecha_radicacion_texto):
        print("No se pudo validar la fecha de radicación. La PQRS no fue guardada.\n")
        return

    fecha_maxima_respuesta = fecha_radicacion + timedelta(days=30)
    radicado = "PQRS-" + fecha_radicacion.strftime("%Y%m%d-%H%M%S-%f")
    registros = cargar_registros()
    id_registro = siguiente_id_tipo(registros, tipo)
    fecha_maxima_texto = fecha_maxima_respuesta.strftime(FORMATO_FECHA_RADICACION)

    pqrs = crear_registro_plano(
        id_registro,
        solicitante,
        tipo,
        canal,
        fecha_radicacion_texto,
        relacionado_con,
        campus,
        asunto,
        descripcion,
        fecha_maxima_texto,
        radicado=radicado,
    )
    guardar_registro_plano(pqrs)
    imprimir_comprobante(pqrs)

    print(f"\nPQRS guardada correctamente. ID: {id_registro}. Radicado: {radicado}")
    print(f"Archivo: {ARCHIVOS_PQRS[tipo]}")
    print(f"Fecha máxima de respuesta: {fecha_maxima_texto}\n")


def mostrar_resumen_pqrs(registro):
    """Muestra los datos principales de una PQRS."""
    print(f"\nID de registro: {registro.get('id', 'Anterior sin ID')}")
    print(f"Radicado: {registro.get('radicado', 'Sin radicado')}")
    print(f"Tipo: {registro.get('tipo_solicitud', 'Sin tipo')}")
    print(f"Solicitante: {registro.get('nombre_completo', 'Sin nombre')}")
    print(f"Mascota: {registro.get('tipo_mascota', 'Sin dato')}")
    print(f"Campus: {registro.get('campus_relacionado', 'Sin dato')}")
    print(f"Asunto: {registro.get('asunto_titulo', 'Sin asunto')}")
    print(f"Estado: {registro.get('estado_peticion', 'Registrada')}")


def mostrar_detalle_pqrs(registro):
    """Muestra todos los datos guardados de una PQRS."""
    print("\n--- Detalle de la PQRS ---")
    print(f"ID de registro: {registro.get('id', 'Anterior sin ID')}")
    print(f"Radicado: {registro.get('radicado', 'Sin radicado')}")
    print("\nDatos del solicitante:")
    print(f"  Nombre: {registro.get('nombre_completo', 'Sin nombre')}")
    print(f"  Tipo de documento: {registro.get('tipo_documento', 'Sin dato')}")
    print(f"  Número de documento: {registro.get('numero_documento', 'Sin dato')}")
    print(f"  Tipo de teléfono: {registro.get('tipo_telefono', 'Sin dato')}")
    print(f"  Teléfono: {registro.get('telefono_contacto', 'Sin dato')}")
    print(f"  Correo: {registro.get('correo_electronico', 'Sin dato')}")
    print(f"  Dirección: {registro.get('direccion') or 'Sin dirección'}")
    print("\nInformación de la solicitud:")
    print(f"  Tipo: {registro.get('tipo_solicitud', 'Sin tipo')}")
    print(f"  Canal: {registro.get('canal_recepcion', 'Sin canal')}")
    print(f"  Mascota: {registro.get('tipo_mascota', 'Sin dato')}")
    print(f"  Campus: {registro.get('campus_relacionado', 'Sin dato')}")
    print(f"  Asunto: {registro.get('asunto_titulo', 'Sin asunto')}")
    print(f"  Descripción: {registro.get('descripcion_detallada', 'Sin descripción')}")
    print(f"  Fecha de radicación: {registro.get('fecha_radicacion', 'Sin fecha')}")
    print(
        "  Fecha máxima de respuesta: "
        f"{registro.get('fecha_maxima_respuesta', 'Sin fecha')}"
    )
    print(f"  Estado: {registro.get('estado_peticion', 'Registrada')}\n")


def listar_pqrs(registros):
    """Muestra un resumen de todas las PQRS."""
    print("\n--- Registros existentes ---")
    for registro in registros:
        mostrar_resumen_pqrs(registro)
    print()


def buscar_pqrs(registros):
    """Busca una PQRS por ID numérico o radicado exacto."""
    identificador = pedir_texto("Escribe el ID o el radicado de la PQRS: ")
    coincidencias = []
    for registro in registros:
        id_registro = registro.get("id")
        radicado = registro.get("radicado", "")
        coincide_id = (
            identificador.isascii()
            and identificador.isdigit()
            and isinstance(id_registro, int)
            and not isinstance(id_registro, bool)
            and id_registro == int(identificador)
        )
        coincide_radicado = (
            isinstance(radicado, str)
            and radicado.casefold() == identificador.casefold()
        )
        if coincide_id or coincide_radicado:
            coincidencias.append(registro)

    if not coincidencias:
        print("No se encontró una PQRS con ese ID o radicado.\n")
        return

    if len(coincidencias) > 1:
        tipos_disponibles = [
            registro["tipo_solicitud"] for registro in coincidencias
        ]
        print("Ese ID existe en más de un archivo. Selecciona el tipo de PQRS:")
        tipo_elegido = pedir_opcion("Tipos encontrados:", tipos_disponibles)
        coincidencias = [
            registro
            for registro in coincidencias
            if registro["tipo_solicitud"] == tipo_elegido
        ]

    mostrar_detalle_pqrs(coincidencias[0])


def consultar_registros():
    """Permite listar PQRS o buscar una por su ID o radicado."""
    while True:
        print("\n--- Consultar PQRS ---")
        opcion = pedir_opcion(
            "Selecciona cómo deseas consultar:",
            [
                "Listar todas las PQRS",
                "Buscar por ID o radicado",
                "Volver al menú principal",
            ],
        )

        if opcion == "Volver al menú principal":
            return

        registros = cargar_registros()
        if not registros:
            print("Todavía no hay registros guardados.\n")
            return

        if opcion == "Listar todas las PQRS":
            listar_pqrs(registros)
        else:
            buscar_pqrs(registros)


def consultar_estado_general_pqrs():
    """Imprime un radicado actualizado para cada PQRS registrada."""
    print("\n--- Estado general de las PQRS ---")
    registros = cargar_registros()
    if not registros:
        print("Todavía no hay registros guardados.\n")
        return

    registros.sort(
        key=lambda registro: (
            registro.get("tipo_solicitud", ""),
            registro.get("id", 0),
        )
    )
    for registro in registros:
        imprimir_comprobante(registro, sufijo="_estado")


def siguiente_estado(estado_actual):
    """Devuelve el único estado permitido después del estado actual."""
    if estado_actual == "Registrada":
        return "En proceso"
    if estado_actual == "En proceso":
        return "Solucionada"
    return None


def cambiar_estado_pqrs():
    """Avanza el estado de una PQRS siguiendo el flujo permitido."""
    print("\n--- Cambiar estado de una PQRS ---")
    registros = cargar_registros()
    if not registros:
        print("Todavía no hay registros para actualizar.\n")
        return

    tipo_solicitud = pedir_opcion(
        "Selecciona el archivo de la PQRS:",
        list(ARCHIVOS_PQRS.keys()),
    )
    identificador = pedir_texto("Escribe el ID numérico de la PQRS: ")
    if not identificador.isascii() or not identificador.isdigit():
        print("El ID debe ser un número entero.\n")
        return

    id_buscado = int(identificador)
    registro_encontrado = None
    for registro in registros:
        if (
            registro.get("id") == id_buscado
            and registro.get("tipo_solicitud") == tipo_solicitud
        ):
            registro_encontrado = registro
            break

    if registro_encontrado is None:
        print(
            f"No se encontró una PQRS con el ID {id_buscado} "
            f"en el archivo {ARCHIVOS_PQRS[tipo_solicitud]}.\n"
        )
        return

    estado_actual = registro_encontrado.get("estado_peticion", "Registrada")
    if estado_actual not in ESTADOS_PQRS:
        print(f"El registro tiene un estado no válido: {estado_actual}.\n")
        return

    estado_nuevo = siguiente_estado(estado_actual)
    if estado_nuevo is None:
        print("La PQRS ya está Solucionada y no puede avanzar a otro estado.\n")
        return

    print(f"Estado actual: {estado_actual}")
    confirmacion = pedir_opcion(
        f"El siguiente estado permitido es {estado_nuevo}. ¿Deseas aplicarlo?",
        ["Sí", "No"],
    )
    if confirmacion == "No":
        print("El estado no se modificó.\n")
        return

    fecha_respuesta = ""
    if estado_nuevo == "Solucionada":
        fecha_respuesta = datetime.now().strftime(FORMATO_FECHA_RADICACION)
    if not actualizar_estado_pqrs(
        tipo_solicitud,
        id_buscado,
        estado_nuevo,
        fecha_respuesta,
    ):
        print("No se pudo guardar el cambio: no se encontró el registro en el archivo.\n")
        return

    print(f"Estado actualizado: {estado_actual} -> {estado_nuevo}.\n")


def mostrar_menu():
    """Mantiene el menú activo hasta que la persona elija salir."""
    while True:
        print("=== Sistema de gestión de PQRS ===")
        print("1. Registrar PQRS")
        print("2. Consultar PQRS")
        print("3. Registrar cambio en PQRS")
        print("4. Generar estadísticas")
        print("5. Consultar estado general de PQRS")
        print("6. Salir")

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            registrar_pqrs()
        elif opcion == "2":
            consultar_registros()
        elif opcion == "3":
            cambiar_estado_pqrs()
        elif opcion == "4":
            generar_estadisticas()
        elif opcion == "5":
            consultar_estado_general_pqrs()
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Elige un número del 1 al 6.\n")


if __name__ == "__main__":
    mostrar_menu()
