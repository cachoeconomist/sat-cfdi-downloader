"""
Fase 3 - Parsea todos los .zip en downloads/ y exporta un .xlsx consolidado.

Uso:
    python scripts/parsear_cfdis.py
"""
import sys
import logging
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sat_downloader.parser import parsear_zip

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

COLUMNAS = [
    "Folio", "Fecha", "Método de Pago", "Lugar de Expedición",
    "RFC Emisor", "Nombre Emisor", "Cantidad", "Descripción",
    "IVA", "Subtotal", "Total",
]


def main() -> None:
    print("=== Fase 3: Parser y exportación de CFDIs ===\n")

    zips = list(Path("downloads").glob("*.zip"))
    if not zips:
        logger.error("No se encontraron archivos .zip en downloads/")
        sys.exit(1)

    logger.info(f"Archivos .zip a procesar: {len(zips)}")

    todas_las_filas = []
    for ruta_zip in zips:
        filas = parsear_zip(ruta_zip)
        todas_las_filas.extend(filas)

    if not todas_las_filas:
        logger.error("No se extrajo ninguna fila. Revisa el formato de los XMLs.")
        sys.exit(1)

    df = pd.DataFrame(todas_las_filas, columns=COLUMNAS)

    salida = Path("downloads/cfdis_consolidado.xlsx")
    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Comprobantes")

    logger.info(f"Archivo exportado: {salida}")
    logger.info(f"Total filas (conceptos): {len(df)}")
    logger.info(f"Total CFDIs únicos: {df['Folio'].nunique()}")
    print(f"\n✅ Listo. Abre downloads/cfdis_consolidado.xlsx en Excel o Numbers.")


if __name__ == "__main__":
    main()
