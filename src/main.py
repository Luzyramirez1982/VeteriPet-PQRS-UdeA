"""
main.py
-------
Este es el PUNTO DE ENTRADA del programa VeteriPet UdeA (el archivo que
se ejecuta para arrancar todo).

Aqui solo ponemos la logica del MENU de consola: mostrar preguntas al
usuario, leer lo que escribe, y avisarle si algo esta mal. Toda la logica
"pesada" vive en los otros 3 archivos, para que el codigo quede ordenado
en partes pequeñas y faciles de explicar:

    - validaciones.py -> revisa que los datos esten bien escritos.
    - archivos.py      -> guarda y lee la informacion en los .txt
    - reportes.py      -> arma el comprobante y calcula las estadisticas.

Para ejecutar el programa (desde una terminal):
    cd src
    python main.py
"""

from datetime import datetime, timedelta

import archivos
import validaciones as val
import reportes

FORMATO_FECHA = val.FORMATO_FECHA

# Mensaje de bienvenida en letras grandes (arte ASCII) que se muestra
# cada vez que se abre el menu principal.
BANNER = r"""
 __     _______ _____ _____ ____  ___ ____  _____ _____
 \ \   / / ____|_   _| ____|  _ \|_ _|  _ \| ____|_   _|
  \ \ / /|  _|   | | |  _| | |_) || || |_) |  _|   | |
   \ V / | |___  | | | |___|  _ < | ||  __/| |___  | |
    \_/  |_____| |_| |_____|_| \_\___|_|   |_____| |_|

          Gestion de PQRS VeteriPet - UdeA
          Atencion de perros y gatos en la Universidad de Antioquia
"""


# -----------------------------------------------------------------
# Funciones de apoyo para pedir datos por consola
# -----------------------------------------------------------------

def pedir_dato_validado(mensaje, funcion_de_validacion, es_opcional=False):
    """
    Muestra 'mensaje' en pantalla, lee lo que escribe el usuario, y lo
    valida usando 'funcion_de_validacion' (una funcion de
    validaciones.py). Si el dato no es valido, muestra el error y vuelve
    a preguntar, una y otra vez, hasta que el usuario escriba algo
    correcto.

    Si 'es_opcional' es True y el usuario deja el campo vacio (solo
    presiona ENTER), se acepta sin validar (se usa para la Direccion).
    """
    while True:
        valor_escrito = input(mensaje).strip()

        if es_opcional and valor_escrito == "":
            return ""

        es_valido, mensaje_error = funcion_de_validacion(valor_escrito)

        if es_valido:
            return valor_escrito

        print("  >> Dato invalido: " + mensaje_error)
        print("")  # linea en blanco para que se vea mas ordenado


def elegir_opcion_de_lista(mensaje, lista_de_opciones):
    """
    Muestra una lista numerada de opciones y obliga al usuario a elegir
    una escribiendo el numero correspondiente. Devuelve el TEXTO de la
    opcion elegida (no el numero).
    """
    print(mensaje)

    numero = 1
    for opcion in lista_de_opciones:
        print("   " + str(numero) + ". " + opcion)
        numero = numero + 1

    while True:
        texto_escrito = input("Escriba el numero de la opcion: ").strip()

        if texto_escrito.isdigit():
            numero_elegido = int(texto_escrito)
            if 1 <= numero_elegido <= len(lista_de_opciones):
                posicion_en_la_lista = numero_elegido - 1
                return lista_de_opciones[posicion_en_la_lista]

        print("  >> Opcion invalida, intente de nuevo.")
        print("")


def pausar():
    """Detiene el programa hasta que el usuario presione ENTER. Sirve
    para que la persona alcance a leer el resultado antes de que la
    pantalla se limpie con el siguiente menu."""
    input("\nPresione ENTER para continuar...")


# -----------------------------------------------------------------
# Opcion 1: Registrar PQRS
# -----------------------------------------------------------------

def registrar_pqrs():
    print("")
    print("=" * 60)
    print(" REGISTRAR NUEVA PQRS ".center(60, "="))
    print("=" * 60)

    # --- Datos del solicitante ---
    nombre_completo = pedir_dato_validado("Nombre completo: ", val.validar_nombre)

    opcion_de_documento = elegir_opcion_de_lista(
        "\nTipo de documento:",
        ["Cedula de ciudadania (CC)", "Tarjeta de identidad (TI)",
         "Cedula de extranjeria (CE)", "Pasaporte (PP)", "NIT"]
    )
    # Traducimos la opcion "legible" al codigo corto que pide el enunciado.
    tipos_de_documento = {
        "Cedula de ciudadania (CC)": "CC",
        "Tarjeta de identidad (TI)": "TI",
        "Cedula de extranjeria (CE)": "CE",
        "Pasaporte (PP)": "PP",
        "NIT": "NIT",
    }
    tipo_documento = tipos_de_documento[opcion_de_documento]

    numero_documento = pedir_dato_validado("Numero de documento: ", val.validar_numero_documento)

    tipo_telefono = elegir_opcion_de_lista(
        "\nTipo de telefono:", ["Celular", "Fijo", "Corporativo", "Otro"]
    )
    telefono_contacto = pedir_dato_validado(
        "Telefono de contacto (10 digitos): ", val.validar_telefono
    )

    correo_electronico = pedir_dato_validado("Correo electronico: ", val.validar_correo)

    print("\nDireccion (OPCIONAL, presione ENTER para dejarla en blanco):")
    direccion = pedir_dato_validado("Direccion: ", val.validar_direccion, es_opcional=True)
    if direccion == "":
        direccion = "N/A"

    # --- Informacion de la PQRS ---
    tipo_solicitud = elegir_opcion_de_lista(
        "\nTipo de solicitud:", ["Peticion", "Queja", "Reclamo", "Sugerencia"]
    )

    # Sugerimos la fecha de hoy, pero dejamos que el usuario la cambie
    # (por ejemplo, si la PQRS llego hace unos dias por correo).
    fecha_de_hoy_como_texto = datetime.now().strftime(FORMATO_FECHA)
    print("\nFecha de radicacion (formato AAAA-MM-DD).")
    print("Presione ENTER para usar la fecha de hoy (" + fecha_de_hoy_como_texto + "):")

    while True:
        fecha_escrita = input("Fecha de radicacion: ").strip()
        if fecha_escrita == "":
            fecha_escrita = fecha_de_hoy_como_texto

        es_valida, mensaje_error, fecha_convertida = val.validar_fecha_radicacion(fecha_escrita)
        if es_valida:
            fecha_radicacion = fecha_escrita
            break
        print("  >> Dato invalido: " + mensaje_error)
        print("")

    canal_recepcion = elegir_opcion_de_lista(
        "\nCanal de recepcion:",
        ["Presencial", "Correo electronico", "Pagina web", "Telefono",
         "Redes sociales", "Otro"]
    )

    asunto_titulo = pedir_dato_validado(
        "\nAsunto o titulo (entre 5 y 150 caracteres): ", val.validar_asunto
    )

    print("\nDescripcion detallada (minimo 20 caracteres):")
    descripcion_detallada = pedir_dato_validado("Descripcion: ", val.validar_descripcion)

    # --- Informacion relacionada ---
    tipo_mascota = elegir_opcion_de_lista("\nTipo de mascota:", ["Perro", "Gato"])

    lista_de_campus_ordenada = sorted(val.CAMPUS_VALIDOS)
    campus_relacionado = elegir_opcion_de_lista("\nCampus relacionado:", lista_de_campus_ordenada)

    # --- Gestion de tiempos: esto se CALCULA, no se le pregunta al usuario ---
    fecha_maxima_respuesta = fecha_convertida + timedelta(days=30)
    fecha_maxima_respuesta_texto = fecha_maxima_respuesta.strftime(FORMATO_FECHA)

    # --- Armamos el registro completo como un diccionario ---
    siguiente_id = archivos.obtener_siguiente_id(tipo_solicitud)

    registro_nuevo = {
        "id": siguiente_id,
        "nombre_completo": nombre_completo,
        "tipo_documento": tipo_documento,
        "numero_documento": numero_documento,
        "tipo_telefono": tipo_telefono.upper(),
        "telefono_contacto": telefono_contacto,
        "correo_electronico": correo_electronico,
        "direccion": direccion,
        "tipo_solicitud": tipo_solicitud.upper(),
        "fecha_radicacion": fecha_radicacion,
        "canal_recepcion": canal_recepcion.upper(),
        "asunto_titulo": asunto_titulo,
        "descripcion_detallada": descripcion_detallada,
        "tipo_mascota": tipo_mascota.upper(),
        "campus_relacionado": campus_relacionado.upper(),
        "fecha_maxima_respuesta": fecha_maxima_respuesta_texto,
        "estado_peticion": "REGISTRADA",  # Todas las PQRS inician asi.
        "fecha_solucion": "N/A",          # Se llena cuando pase a "Solucionada".
    }

    archivos.guardar_registro(tipo_solicitud, registro_nuevo)

    print("\n>> PQRS registrada con exito.")

    ruta_del_comprobante = reportes.guardar_comprobante_en_archivo(registro_nuevo, tipo_solicitud)
    print(">> Se genero el comprobante en: " + ruta_del_comprobante)
    print("")
    print(reportes.generar_comprobante(registro_nuevo))

    pausar()


# -----------------------------------------------------------------
# Opcion 2: Consultar PQRS
# -----------------------------------------------------------------

def consultar_pqrs():
    print("")
    print("=" * 60)
    print(" CONSULTAR PQRS ".center(60, "="))
    print("=" * 60)
    print("1. Ver los registros ACTIVOS (Registrada / En proceso)")
    print("2. Ver TODOS los registros (incluye Solucionadas)")
    print("3. Buscar un radicado por numero de ID y tipo de solicitud")
    print("4. Volver al menu principal")

    opcion_elegida = input("Seleccione una opcion: ").strip()

    if opcion_elegida == "1":
        todos_los_registros = archivos.leer_todos_los_registros()
        registros_activos = []
        for registro in todos_los_registros:
            if registro.get("estado_peticion", "").upper() != "SOLUCIONADA":
                registros_activos.append(registro)
        _mostrar_lista_de_registros(registros_activos)

    elif opcion_elegida == "2":
        todos_los_registros = archivos.leer_todos_los_registros()
        _mostrar_lista_de_registros(todos_los_registros)

    elif opcion_elegida == "3":
        tipo_solicitud = elegir_opcion_de_lista(
            "\nTipo de solicitud del radicado:",
            ["Peticion", "Queja", "Reclamo", "Sugerencia"]
        )
        id_escrito = input("Numero de radicado (ID): ").strip()

        if not id_escrito.isdigit():
            print("  >> El ID debe ser un numero entero.")
        else:
            registro = archivos.buscar_registro_por_id(tipo_solicitud, int(id_escrito))
            if registro is None:
                print("  >> No se encontro ningun registro con ese ID en ese archivo.")
            else:
                print("")
                print(reportes.generar_comprobante(registro))

    elif opcion_elegida == "4":
        return  # Salimos de la funcion sin hacer nada mas.

    else:
        print("  >> Opcion invalida.")

    pausar()


def _mostrar_lista_de_registros(lista_de_registros):
    """Imprime una tabla sencilla (una fila por registro) en la
    consola."""
    if len(lista_de_registros) == 0:
        print("\nNo hay registros para mostrar.")
        return

    encabezado = (
        "ID".ljust(5) + "TIPO".ljust(12) + "NOMBRE".ljust(25)
        + "ESTADO".ljust(14) + "RADICACION".ljust(13) + "VENCE".ljust(13)
    )
    print("")
    print(encabezado)
    print("-" * len(encabezado))

    for registro in lista_de_registros:
        nombre_recortado = registro.get("nombre_completo", "")[0:24]
        fila = (
            str(registro.get("id", "")).ljust(5)
            + str(registro.get("tipo_solicitud", "")).ljust(12)
            + nombre_recortado.ljust(25)
            + str(registro.get("estado_peticion", "")).ljust(14)
            + str(registro.get("fecha_radicacion", "")).ljust(13)
            + str(registro.get("fecha_maxima_respuesta", "")).ljust(13)
        )
        print(fila)

    print("\nTotal de registros mostrados: " + str(len(lista_de_registros)))


# -----------------------------------------------------------------
# Opcion 3: Registrar Cambio en PQRS (cambio de estado)
# -----------------------------------------------------------------

# El enunciado exige que el estado SOLO avance en este orden:
#   Registrada -> En proceso -> Solucionada
# Este diccionario dice "si estoy en tal estado, el siguiente es tal otro".
SIGUIENTE_ESTADO = {
    "REGISTRADA": "EN PROCESO",
    "EN PROCESO": "SOLUCIONADA",
}


def registrar_cambio_pqrs():
    print("")
    print("=" * 60)
    print(" REGISTRAR CAMBIO EN PQRS (cambio de estado) ".center(60, "="))
    print("=" * 60)

    tipo_solicitud = elegir_opcion_de_lista(
        "\nTipo de solicitud del radicado a modificar:",
        ["Peticion", "Queja", "Reclamo", "Sugerencia"]
    )
    id_escrito = input("Numero de radicado (ID): ").strip()

    if not id_escrito.isdigit():
        print("  >> El ID debe ser un numero entero.")
        pausar()
        return

    registro = archivos.buscar_registro_por_id(tipo_solicitud, int(id_escrito))
    if registro is None:
        print("  >> No se encontro ningun registro con ese ID en ese archivo.")
        pausar()
        return

    estado_actual = registro.get("estado_peticion", "").upper()
    print("\nEstado actual: " + estado_actual)

    if estado_actual not in SIGUIENTE_ESTADO:
        print("  >> Esta PQRS ya esta en su estado final (Solucionada).")
        print("  >> No se permiten mas cambios de estado.")
        pausar()
        return

    siguiente_estado = SIGUIENTE_ESTADO[estado_actual]
    pregunta = "¿Desea cambiar el estado de '" + estado_actual + "' a '" + siguiente_estado + "'? (S/N): "
    respuesta = input(pregunta).strip().upper()

    if respuesta != "S":
        print("  >> Operacion cancelada.")
        pausar()
        return

    cambios_a_aplicar = {"estado_peticion": siguiente_estado}

    # Si el nuevo estado es SOLUCIONADA, guardamos la fecha real en la
    # que ocurrio el cambio. Este dato es el que usa la estadistica
    # obligatoria del promedio de dias de respuesta.
    if siguiente_estado == "SOLUCIONADA":
        cambios_a_aplicar["fecha_solucion"] = datetime.now().strftime(FORMATO_FECHA)

    se_pudo_actualizar = archivos.actualizar_registro(tipo_solicitud, int(id_escrito), cambios_a_aplicar)

    if se_pudo_actualizar:
        print("\n>> Estado actualizado correctamente a '" + siguiente_estado + "'.")
    else:
        print("\n>> No se pudo actualizar el registro (error inesperado).")

    pausar()


# -----------------------------------------------------------------
# Opcion 4: Estadisticas
# -----------------------------------------------------------------

def mostrar_estadisticas():
    todos_los_registros = archivos.leer_todos_los_registros()
    print("")
    print(reportes.generar_reporte_de_estadisticas(todos_los_registros))
    pausar()


# -----------------------------------------------------------------
# Menu principal (aqui arranca y se queda corriendo el programa)
# -----------------------------------------------------------------

def menu_principal():
    # Nos aseguramos de que existan la carpeta "data" y los 4 archivos
    # de texto ANTES de mostrar el menu por primera vez.
    archivos.inicializar_archivos()

    programa_encendido = True

    while programa_encendido:
        print(BANNER)
        print("Bienvenido a VeteriPet UdeA - Gestion de PQRS")
        print("   1. Registrar PQRS")
        print("   2. Consultar PQRS")
        print("   3. Registrar Cambio en PQRS")
        print("   4. Estadisticas")
        print("   5. Salir")

        opcion_elegida = input("\nSeleccione una opcion (1-5): ").strip()

        if opcion_elegida == "1":
            registrar_pqrs()
        elif opcion_elegida == "2":
            consultar_pqrs()
        elif opcion_elegida == "3":
            registrar_cambio_pqrs()
        elif opcion_elegida == "4":
            mostrar_estadisticas()
        elif opcion_elegida == "5":
            print("\nGracias por usar VeteriPet UdeA. ¡Hasta pronto!")
            programa_encendido = False  # Esto hace que el "while" termine.
        else:
            print("\n>> Opcion invalida, intente de nuevo.")


# Esta linea hace que el menu principal solo se ejecute cuando corremos
# este archivo directamente (python main.py), y no si alguien "importa"
# este archivo desde otro programa.
if __name__ == "__main__":
    menu_principal()
