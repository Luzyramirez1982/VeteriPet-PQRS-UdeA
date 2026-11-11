from datetime import datetime

from archivos import ARCHIVOS_PQRS, cargar_registros


FORMATO_FECHA_RADICACION = "%Y-%m-%d %H:%M:%S"
ESTADOS_PQRS = ["Registrada", "En proceso", "Solucionada"]


def convertir_a_fecha(fecha_texto):
    """Interpreta las fechas del sistema en formato con hora o solo fecha."""
    if not isinstance(fecha_texto, str):
        return None

    for formato in (FORMATO_FECHA_RADICACION, "%Y-%m-%d"):
        try:
            return datetime.strptime(fecha_texto, formato)
        except ValueError:
            continue
    return None


def calcular_dias_respuesta(registro):
    """Devuelve los días calendario hasta la respuesta si ya fue solucionada."""
    if registro.get("estado_peticion") != "Solucionada":
        return None

    fecha_radicacion = convertir_a_fecha(registro.get("fecha_radicacion"))
    fecha_respuesta = convertir_a_fecha(registro.get("fecha_respuesta"))
    if fecha_radicacion is None or fecha_respuesta is None:
        return None

    dias = (fecha_respuesta.date() - fecha_radicacion.date()).days
    if dias < 0:
        return None
    return dias


def generar_estadisticas():
    """Muestra el promedio de respuesta y cinco estadísticas de gestión."""
    print("\n--- Estadísticas de gestión de PQRS ---")
    registros = cargar_registros()

    if not registros:
        print("Todavía no hay registros para analizar.\n")
        return

    tiempos_respuesta = []
    for registro in registros:
        dias = calcular_dias_respuesta(registro)
        if dias is not None:
            tiempos_respuesta.append(dias)
    if tiempos_respuesta:
        promedio = round(sum(tiempos_respuesta) / len(tiempos_respuesta))
        print(
            "1. Promedio de días para responder: "
            f"{promedio} día(s), basado en {len(tiempos_respuesta)} PQRS solucionada(s)."
        )
    else:
        print(
            "1. Promedio de días para responder: sin datos; "
            "aún no hay PQRS solucionadas con fecha de respuesta registrada."
        )

    print("\n2. PQRS registradas por tipo:")
    for tipo in ARCHIVOS_PQRS:
        cantidad = sum(
            1
            for registro in registros
            if registro.get("tipo_solicitud") == tipo
        )
        print(f"   {tipo}: {cantidad}")

    print("\n3. PQRS por estado:")
    for estado in ESTADOS_PQRS:
        cantidad = sum(
            1
            for registro in registros
            if registro.get("estado_peticion", "Registrada") == estado
        )
        print(f"   {estado}: {cantidad}")

    solucionadas = sum(
        1
        for registro in registros
        if registro.get("estado_peticion", "Registrada") == "Solucionada"
    )
    porcentaje_solucionadas = round(solucionadas * 100 / len(registros))
    print(
        "\n4. Porcentaje de PQRS solucionadas: "
        f"{porcentaje_solucionadas}% ({solucionadas} de {len(registros)})."
    )

    hoy = datetime.now().date()
    vencidas = 0
    for registro in registros:
        estado = registro.get("estado_peticion", "Registrada")
        fecha_limite = convertir_a_fecha(registro.get("fecha_maxima_respuesta"))
        if (
            estado in ("Registrada", "En proceso")
            and fecha_limite is not None
            and fecha_limite.date() < hoy
        ):
            vencidas += 1
    print(f"\n5. PQRS abiertas con plazo vencido: {vencidas}.")

    canales = {}
    for registro in registros:
        canal = registro.get("canal_recepcion", "Sin canal")
        canales[canal] = canales.get(canal, 0) + 1
    canal_mas_usado = sorted(
        canales.items(),
        key=lambda elemento: (-elemento[1], elemento[0]),
    )[0]
    print(
        "\n6. Canal de recepción más utilizado: "
        f"{canal_mas_usado[0]} ({canal_mas_usado[1]} PQRS)."
    )
    print()
