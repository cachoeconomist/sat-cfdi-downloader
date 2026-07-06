"""
Utilidad para parsear reportes tabulares del SAT (formato .txt delimitado por ~).
Este formato se genera cuando se descarga desde el portal web del SAT,
a diferencia de los XMLs del Web Service.

Uso:
    python scripts/parsear_reporte_sat.py /ruta/a/la/carpeta
    python scripts/parsear_reporte_sat.py /Users/isma/Downloads/cfdi_jose
"""
import sys
import io
import zipfile
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Mapeo de nombres originales del SAT a nombres legibles en español
RENOMBRAR = {
    "Uuid":                  "UUID",
    "RfcEmisor":             "RFC Emisor",
    "NombreEmisor":          "Nombre Emisor",
    "RfcReceptor":           "RFC Receptor",
    "NombreReceptor":        "Nombre Receptor",
    "PacCertifico":          "PAC",
    "FechaEmision":          "Fecha Emisión",
    "FechaCertificacionSat": "Fecha Certificación SAT",
    "Monto":                 "Monto",
    "EfectoComprobante":     "Efecto",
    "Estatus":               "Estatus",
    "FechaCancelacion":      "Fecha Cancelación",
}

# Orden final de columnas en el Excel
COLUMNAS = list(RENOMBRAR.values())

# El SAT codifica Efecto y Estatus con claves — las traducimos
EFECTO = {"I": "Ingreso", "E": "Egreso", "P": "Pago", "N": "Nómina", "T": "Traslado"}
ESTATUS = {"1": "Vigente", "0": "Cancelado"}


def parsear_txt(contenido: str, nombre_archivo: str) -> pd.DataFrame:
    """
    Lee el contenido de un .txt delimitado por ~ y retorna un DataFrame.
    """
    try:
        df = pd.read_csv(
            io.StringIO(contenido),
            sep="~",
            dtype=str,
            encoding="utf-8",
        )
        # Eliminar columnas vacías que el SAT a veces agrega al final
        df = df.dropna(axis=1, how="all")
        df = df.rename(columns=RENOMBRAR)

        # Traducir claves a valores legibles
        if "Efecto" in df.columns:
            df["Efecto"] = df["Efecto"].map(EFECTO).fillna(df["Efecto"])
        if "Estatus" in df.columns:
            df["Estatus"] = df["Estatus"].map(ESTATUS).fillna(df["Estatus"])

        # Convertir Monto a numérico
        if "Monto" in df.columns:
            df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")

        logger.info(f"{nombre_archivo}: {len(df)} registros")
        return df

    except Exception as e:
        logger.warning(f"Error parseando {nombre_archivo}: {type(e).__name__}: {e}")
        return pd.DataFrame()


def parsear_zips(carpeta: Path) -> pd.DataFrame:
    """
    Abre todos los .zip de la carpeta y parsea los .txt que contienen.
    """
    zips = sorted(carpeta.glob("*.zip"))
    if not zips:
        logger.error(f"No se encontraron archivos .zip en: {carpeta}")
        sys.exit(1)

    logger.info(f"Archivos .zip encontrados: {len(zips)}")
    frames = []

    for ruta_zip in zips:
        with zipfile.ZipFile(ruta_zip, "r") as zf:
            txts = [f for f in zf.namelist() if f.endswith(".txt")]
            for nombre in txts:
                with zf.open(nombre) as f:
                    contenido = f.read().decode("utf-8", errors="replace")
                    df = parsear_txt(contenido, nombre)
                    if not df.empty:
                        frames.append(df)

    if not frames:
        logger.error("No se extrajo ningún registro.")
        sys.exit(1)

    return pd.concat(frames, ignore_index=True)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python scripts/parsear_reporte_sat.py /ruta/a/la/carpeta")
        sys.exit(1)

    carpeta = Path(sys.argv[1])
    if not carpeta.exists() or not carpeta.is_dir():
        logger.error(f"Carpeta no válida: {carpeta}")
        sys.exit(1)

    print(f"\n=== Parser de Reportes SAT (formato ~) ===")
    print(f"Carpeta: {carpeta}\n")

    df = parsear_zips(carpeta)

    # Solo conservar columnas que existan en el DataFrame
    columnas_finales = [c for c in COLUMNAS if c in df.columns]
    df = df[columnas_finales]

    salida = carpeta / "reporte_consolidado.xlsx"
    with pd.ExcelWriter(salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="CFDIs")

    logger.info(f"Total registros: {len(df)}")
    logger.info(f"Vigentes: {(df['Estatus'] == 'Vigente').sum()}")
    logger.info(f"Cancelados: {(df['Estatus'] == 'Cancelado').sum()}")
    logger.info(f"Archivo exportado: {salida}")
    print(f"\n✅ Listo. Abre reporte_consolidado.xlsx en Excel o Numbers.")


if __name__ == "__main__":
    main()
