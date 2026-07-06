"""
Fase 3 - Parser de CFDIs recibidos.
Extrae campos clave de cada XML dentro de un .zip descargado del SAT.
Cada concepto genera una fila independiente en el resultado final.
"""
import zipfile
import logging
from pathlib import Path
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
}


def parsear_cfdi(xml_bytes: bytes, nombre_archivo: str = "") -> list[dict]:
    """
    Parsea un XML de CFDI y retorna una lista de filas —
    una por cada concepto dentro del comprobante.
    Si el XML no tiene el formato esperado, retorna lista vacía.
    """
    try:
        root = ET.fromstring(xml_bytes)

        # Datos del comprobante
        fecha            = root.get("Fecha", "")
        folio            = root.get("Folio", "")
        metodo_pago      = root.get("MetodoPago", "")
        lugar_expedicion = root.get("LugarExpedicion", "")
        subtotal         = root.get("SubTotal", "")
        total            = root.get("Total", "")

        # Datos del emisor
        emisor        = root.find("cfdi:Emisor", NS)
        rfc_emisor    = emisor.get("Rfc", "")    if emisor is not None else ""
        nombre_emisor = emisor.get("Nombre", "") if emisor is not None else ""

        # Conceptos — cada uno genera una fila
        filas = []
        for concepto in root.findall("cfdi:Conceptos/cfdi:Concepto", NS):
            cantidad    = concepto.get("Cantidad", "")
            descripcion = concepto.get("Descripcion", "")

            # IVA del concepto (puede no existir)
            iva = ""
            impuestos = concepto.find("cfdi:Impuestos", NS)
            if impuestos is not None:
                traslados = impuestos.find("cfdi:Traslados", NS)
                if traslados is not None:
                    traslado = traslados.find("cfdi:Traslado", NS)
                    if traslado is not None:
                        iva = traslado.get("Importe", "")

            filas.append({
                "Folio":              folio,
                "Fecha":              fecha,
                "Método de Pago":     metodo_pago,
                "Lugar de Expedición": lugar_expedicion,
                "RFC Emisor":         rfc_emisor,
                "Nombre Emisor":      nombre_emisor,
                "Cantidad":           cantidad,
                "Descripción":        descripcion,
                "IVA":                iva,
                "Subtotal":           subtotal,
                "Total":              total,
            })

        if not filas:
            logger.warning(f"CFDI sin conceptos: {nombre_archivo}")

        return filas

    except Exception as e:
        logger.warning(f"Error parseando {nombre_archivo}: {type(e).__name__}: {e}")
        return []


def parsear_zip(ruta_zip: Path) -> list[dict]:
    """
    Abre un .zip descargado del SAT y parsea todos los XMLs dentro.
    Retorna lista de filas (una por concepto por CFDI).
    """
    todas_las_filas = []

    with zipfile.ZipFile(ruta_zip, "r") as zf:
        xmls = [f for f in zf.namelist() if f.endswith(".xml")]
        logger.info(f"Encontrados {len(xmls)} XMLs en {ruta_zip.name}")

        for nombre in xmls:
            with zf.open(nombre) as f:
                filas = parsear_cfdi(f.read(), nombre_archivo=nombre)
                todas_las_filas.extend(filas)

    logger.info(f"Total filas extraídas de {ruta_zip.name}: {len(todas_las_filas)}")
    return todas_las_filas
