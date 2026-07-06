"""
Fase 2 - Flujo completo de Descarga Masiva del SAT:
  1. Solicitar descarga (obtiene IdSolicitud)
  2. Verificar estado (polling hasta TERMINADA)
  3. Descargar paquetes .zip
"""
import time
import logging
import base64
from datetime import date
from pathlib import Path

from satcfdi.pacs.sat import (
    SAT,
    TipoDescargaMasivaTerceros,
    EstadoSolicitud,
    EstadoComprobante,
)

logger = logging.getLogger(__name__)


def solicitar_descarga(
    sat_service: SAT,
    fecha_inicial: date,
    fecha_final: date,
    tipo: TipoDescargaMasivaTerceros = TipoDescargaMasivaTerceros.CFDI,
) -> str | None:
    """
    Paso 1: Presenta la solicitud al SAT y devuelve el IdSolicitud.
    Retorna None si el SAT rechaza la solicitud.
    """
    logger.info(f"Solicitando descarga: {fecha_inicial} → {fecha_final}, tipo={tipo.name}")
    try:
        response = sat_service.recover_comprobante_received_request(
            fecha_inicial=fecha_inicial,
            fecha_final=fecha_final,
            rfc_receptor=sat_service.signer.rfc,
            tipo_solicitud=tipo,
            estado_comprobante=EstadoComprobante.VIGENTE,
        )
        id_solicitud = response.get("IdSolicitud")
        cod_estatus = response.get("CodEstatus", "")
        mensaje = response.get("Mensaje", "")

        logger.info(f"Respuesta SAT: CodEstatus={cod_estatus} | Mensaje={mensaje}")

        if id_solicitud:
            logger.info(f"IdSolicitud obtenido: {id_solicitud}")
            return id_solicitud
        else:
            logger.warning(f"SAT no devolvió IdSolicitud. Respuesta completa: {response}")
            return None

    except Exception as e:
        logger.error(f"Error al solicitar descarga: {type(e).__name__}: {e}")
        return None


def verificar_estado(
    sat_service: SAT,
    id_solicitud: str,
    intervalo_segundos: int = 60,
    max_intentos: int = 10,
) -> list[str]:
    """
    Paso 2: Consulta el estado de la solicitud en loop hasta que
    el SAT la tenga lista. Devuelve lista de IdsPaquetes para descargar.
    """
    logger.info(f"Verificando estado de solicitud: {id_solicitud}")

    for intento in range(1, max_intentos + 1):
        try:
            response = sat_service.recover_comprobante_status(id_solicitud)
            estado = response.get("EstadoSolicitud")
            cod_estatus = response.get("CodEstatus", "")
            mensaje = response.get("Mensaje", "")

            logger.info(
                f"Intento {intento}/{max_intentos} | "
                f"Estado={estado} | CodEstatus={cod_estatus} | {mensaje}"
            )

            if estado == EstadoSolicitud.TERMINADA:
                paquetes = response.get("IdsPaquetes", [])
                logger.info(f"Solicitud terminada. Paquetes disponibles: {len(paquetes)}")
                return paquetes

            elif estado in (EstadoSolicitud.ERROR, EstadoSolicitud.RECHAZADA, EstadoSolicitud.VENCIDA):
                logger.error(f"Solicitud terminó con estado no recuperable: {estado}")
                return []

            # Estados ACEPTADA o EN_PROCESO: seguimos esperando
            logger.info(f"Esperando {intervalo_segundos}s antes del siguiente intento...")
            time.sleep(intervalo_segundos)

        except Exception as e:
            logger.error(f"Error al verificar estado (intento {intento}): {type(e).__name__}: {e}")
            time.sleep(intervalo_segundos)

    logger.error(f"Se agotaron los {max_intentos} intentos sin obtener respuesta TERMINADA.")
    return []


def descargar_paquetes(
    sat_service: SAT,
    ids_paquetes: list[str],
    directorio_destino: Path = Path("downloads"),
) -> list[Path]:
    """
    Paso 3: Descarga cada paquete .zip y lo guarda en disco.
    Devuelve lista de rutas de archivos descargados.
    """
    directorio_destino.mkdir(parents=True, exist_ok=True)
    archivos_descargados = []

    for id_paquete in ids_paquetes:
        logger.info(f"Descargando paquete: {id_paquete}")
        try:
            response, datos = sat_service.recover_comprobante_download(
            id_paquete=id_paquete
            )
            ruta = directorio_destino / f"{id_paquete}.zip"
            # La librería puede devolver base64 string o bytes según la versión
            if isinstance(datos, str):
                datos = base64.b64decode(datos)
            ruta.write_bytes(datos)
            archivos_descargados.append(ruta)

        except Exception as e:
            logger.error(f"Error al descargar paquete {id_paquete}: {type(e).__name__}: {e}")

    return archivos_descargados
