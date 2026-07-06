"""
Fase 2 - Punto de entrada: orquesta el flujo completo de descarga masiva.

Uso:
    python scripts/descarga_masiva.py
"""
import sys
import logging
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sat_downloader.config import load_config
from sat_downloader.auth import build_signer, build_sat_service
from sat_downloader.solicitudes import solicitar_descarga, verificar_estado, descargar_paquetes

# Configurar logging para ver todo en consola con timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    print("=== Fase 2: Descarga Masiva de CFDIs ===\n")

    # 1. Configuración y autenticación
    config = load_config()
    signer = build_signer(config)
    sat_service = build_sat_service(signer)
    logger.info(f"Autenticado como RFC: {signer.rfc}")

    # 2. Parámetros de descarga — ajusta el rango de fechas aquí (AAAA, M, D)
    fecha_inicial = date(2026, 1, 1)
    fecha_final   = date(2026, 7, 4)

    # 3. Solicitar
    id_solicitud = solicitar_descarga(sat_service, fecha_inicial, fecha_final)
    if not id_solicitud:
        logger.error("No se obtuvo IdSolicitud. Abortando.")
        sys.exit(1)

    # 4. Verificar (con el CSD de prueba esto retornará error del SAT — esperado)
    ids_paquetes = verificar_estado(
        sat_service,
        id_solicitud,
        intervalo_segundos=10,  # reducido para pruebas
        max_intentos=3,
    )

    # 5. Descargar
    if ids_paquetes:
        archivos = descargar_paquetes(sat_service, ids_paquetes)
        print(f"\n✅ Descarga completa. {len(archivos)} paquete(s) guardados en downloads/")
    else:
        print("\n⚠️  Sin paquetes que descargar (esperado con certificado de prueba).")
        print("    El flujo de código es correcto. Conecta tu FIEL real para datos reales.")


if __name__ == "__main__":
    main()
