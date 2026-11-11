import json
import os


CARPETA_DATOS = os.path.join(os.path.dirname(__file__), "data")
ARCHIVOS_PQRS = {
    "Petición": "Peticion.txt",
    "Queja": "Queja.txt",
    "Reclamo": "Reclamo.txt",
    "Sugerencia": "Sugerencia.txt",
}


def ruta_archivo_pqrs(tipo_solicitud):
    """Devuelve la ruta del archivo asignado a un tipo de PQRS."""
    return os.path.join(CARPETA_DATOS, ARCHIVOS_PQRS[tipo_solicitud])


def crear_registro_plano(id_registro, solicitante, tipo, canal, fecha_radicacion,
                         relacionado_con, campus, asunto, descripcion,
                         fecha_maxima_respuesta, estado="Registrada", radicado="",
                         fecha_respuesta=""):
    """Construye la estructura plana que se guarda en los archivos de texto."""
    return {
        "id": id_registro,
        "nombre_completo": solicitante.get("nombre", ""),
        "tipo_documento": solicitante.get("tipo_documento", ""),
        "numero_documento": solicitante.get("numero_documento", ""),
        "tipo_telefono": solicitante.get("tipo_telefono", ""),
        "telefono_contacto": solicitante.get("telefono", ""),
        "correo_electronico": solicitante.get("correo", ""),
        "direccion": solicitante.get("direccion", ""),
        "tipo_solicitud": tipo,
        "fecha_radicacion": fecha_radicacion,
        "canal_recepcion": canal,
        "asunto_titulo": asunto,
        "descripcion_detallada": descripcion,
        "tipo_mascota": relacionado_con,
        "campus_relacionado": campus,
        "fecha_maxima_respuesta": fecha_maxima_respuesta,
        "estado_peticion": estado,
        "fecha_respuesta": fecha_respuesta,
        "radicado": radicado,
    }


def siguiente_id_tipo(registros, tipo_solicitud):
    """Calcula el siguiente ID únicamente para el tipo de PQRS indicado."""
    ids_validos = [
        registro["id"]
        for registro in registros
        if registro.get("tipo_solicitud") == tipo_solicitud
        and isinstance(registro.get("id"), int)
        and not isinstance(registro.get("id"), bool)
    ]
    return max(ids_validos, default=0) + 1


def guardar_registro_plano(registro):
    """Agrega una PQRS como una línea JSON al archivo de su tipo."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    ruta_archivo = ruta_archivo_pqrs(registro["tipo_solicitud"])
    with open(ruta_archivo, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def cargar_registros():
    """Lee las cuatro listas de PQRS y migra JSON antiguos si existen."""
    registros = []

    os.makedirs(CARPETA_DATOS, exist_ok=True)
    for tipo, nombre_archivo in ARCHIVOS_PQRS.items():
        ruta_archivo = os.path.join(CARPETA_DATOS, nombre_archivo)
        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, "w", encoding="utf-8"):
                pass

        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                if not linea.strip():
                    continue
                try:
                    registro = json.loads(linea)
                except json.JSONDecodeError as error:
                    print(
                        f"No se pudo leer {nombre_archivo}, línea {numero_linea}: "
                        f"{error}"
                    )
                    continue

                if not isinstance(registro, dict):
                    print(
                        f"No se pudo leer {nombre_archivo}, línea {numero_linea}: "
                        "se esperaba un objeto JSON."
                    )
                    continue
                if registro.get("tipo_solicitud") != tipo:
                    print(
                        f"Registro ignorado en {nombre_archivo}, línea {numero_linea}: "
                        "el tipo de solicitud no corresponde al archivo."
                    )
                    continue
                registro.setdefault("fecha_respuesta", "")
                registros.append(registro)

    migrar_registros_json_antiguos(registros)
    return registros


def normalizar_tipo_solicitud(tipo):
    """Reconoce el tipo de una PQRS guardada en versiones anteriores."""
    if not isinstance(tipo, str):
        return None

    tipo_busqueda = tipo.strip().casefold()
    for tipo_conocido in ARCHIVOS_PQRS:
        if tipo_busqueda == tipo_conocido.casefold():
            return tipo_conocido
        if tipo_busqueda == tipo_conocido.replace("ó", "o").casefold():
            return tipo_conocido
    return None


def migrar_registros_json_antiguos(registros):
    """Copia registros JSON antiguos a su archivo de texto sin borrarlos."""
    radicados_existentes = {
        registro.get("radicado")
        for registro in registros
        if registro.get("radicado")
    }
    archivos_json = [
        nombre
        for nombre in os.listdir(CARPETA_DATOS)
        if nombre.lower().endswith(".json")
    ]
    registros_antiguos = []
    for nombre_archivo in archivos_json:
        ruta_archivo = os.path.join(CARPETA_DATOS, nombre_archivo)
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                registro_antiguo = json.load(archivo)
        except (OSError, json.JSONDecodeError) as error:
            print(f"No se pudo migrar {nombre_archivo}: {error}")
            continue

        if not isinstance(registro_antiguo, dict):
            print(f"No se pudo migrar {nombre_archivo}: el contenido no es un objeto.")
            continue

        tipo = normalizar_tipo_solicitud(registro_antiguo.get("tipo"))
        if tipo is None:
            print(
                f"No se pudo migrar {nombre_archivo}: "
                "el tipo de solicitud no es válido."
            )
            continue

        radicado = registro_antiguo.get("radicado", "")
        if not radicado:
            radicado = os.path.splitext(nombre_archivo)[0]
        if radicado in radicados_existentes:
            continue

        solicitante = registro_antiguo.get("solicitante", {})
        if not isinstance(solicitante, dict):
            solicitante = {}
        registros_antiguos.append(
            (tipo, registro_antiguo, solicitante, radicado)
        )

    registros_antiguos.sort(
        key=lambda elemento: (
            elemento[0],
            elemento[1].get("fecha_radicacion", ""),
            elemento[3],
        )
    )
    for tipo, antiguo, solicitante, radicado in registros_antiguos:
        id_registro = siguiente_id_tipo(registros, tipo)
        registro_nuevo = crear_registro_plano(
            id_registro,
            solicitante,
            tipo,
            antiguo.get("canal", ""),
            antiguo.get("fecha_radicacion", ""),
            antiguo.get("relacionado_con", ""),
            antiguo.get("campus", ""),
            antiguo.get("asunto", ""),
            antiguo.get("descripcion", ""),
            antiguo.get("fecha_maxima_respuesta", ""),
            estado=antiguo.get("estado", "Registrada"),
            radicado=radicado,
            fecha_respuesta=antiguo.get("fecha_respuesta", ""),
        )
        guardar_registro_plano(registro_nuevo)
        registros.append(registro_nuevo)
        radicados_existentes.add(radicado)


def actualizar_estado_pqrs(tipo_solicitud, id_buscado, estado_nuevo, fecha_respuesta=""):
    """Actualiza el estado de una PQRS en su archivo y devuelve si tuvo éxito."""
    ruta_archivo = ruta_archivo_pqrs(tipo_solicitud)
    lineas_actualizadas = []
    encontrado = False

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            if not linea.strip():
                lineas_actualizadas.append(linea)
                continue
            registro = json.loads(linea)
            if registro.get("id") == id_buscado:
                registro["estado_peticion"] = estado_nuevo
                if fecha_respuesta:
                    registro["fecha_respuesta"] = fecha_respuesta
                encontrado = True
            lineas_actualizadas.append(
                json.dumps(registro, ensure_ascii=False) + "\n"
            )

    if not encontrado:
        return False

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.writelines(lineas_actualizadas)
    return True
