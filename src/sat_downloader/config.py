"""
Carga y valida la configuración del proyecto desde variables de entorno.
Este es el ÚNICO archivo que debe leer el .env directamente.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Busca el archivo .env en la raíz del proyecto y lo carga en el entorno


@dataclass(frozen=True)
class SATConfig:
    rfc: str
    cert_path: Path
    key_path: Path
    password: str

    def validate(self) -> None:
        """Falla rápido si algo falta, en lugar de fallar a medio proceso."""
        if not self.rfc:
            raise ValueError("SAT_RFC no está definido en el .env")
        if not self.cert_path.exists():
            raise FileNotFoundError(f"No se encontró el certificado en: {self.cert_path}")
        if not self.key_path.exists():
            raise FileNotFoundError(f"No se encontró la llave privada en: {self.key_path}")
        if not self.password:
            raise ValueError("SAT_CSD_PASSWORD no está definido en el .env")


def load_config() -> SATConfig:
    config = SATConfig(
        rfc=os.getenv("SAT_RFC", ""),
        cert_path=Path(os.getenv("SAT_CSD_CERT_PATH", "")),
        key_path=Path(os.getenv("SAT_CSD_KEY_PATH", "")),
        password=os.getenv("SAT_CSD_PASSWORD", ""),
    )
    config.validate()
    return config