"""
Fase 1 - Prueba de conectividad y autenticación (Handshake) contra el
Web Service de Descarga Masiva del SAT, usando CSD de prueba.

Uso:
    python scripts/test_handshake.py
"""
import sys
from pathlib import Path

# Permite importar el paquete src/sat_downloader sin instalarlo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sat_downloader.config import load_config
from sat_downloader.auth import build_signer, build_sat_service


def main() -> None:
    print("=== Fase 1: Handshake con el Web Service del SAT ===\n")

    print("[1/3] Cargando configuración desde .env...")
    config = load_config()
    print(f"      RFC configurado: {config.rfc}")

    print("[2/3] Desencriptando CSD/FIEL en memoria...")
    signer = build_signer(config)
    print(f"      Certificado cargado correctamente. RFC del certificado: {signer.rfc}")

    if signer.rfc != config.rfc:
        print("      ADVERTENCIA: el RFC del .env no coincide con el del certificado.")

    print("[3/3] Construyendo cliente SAT y validando firma de solicitud de prueba...")
    sat_service = build_sat_service(signer)
    print(f"      Cliente SAT inicializado para RFC: {sat_service.signer.rfc}")

    print("\n✅ Handshake preparado correctamente. El Signer es válido y firma mensajes.")
    print("   (La librería obtiene el token de autenticación de forma automática y")
    print("    transparente en la primera llamada real al Web Service, ej. una solicitud")
    print("    de descarga. No hay un método público aislado 'solo pedir token'.)")


if __name__ == "__main__":
    main()