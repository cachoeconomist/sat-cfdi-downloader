"""
Encapsula la creación del Signer (FIEL/CSD en memoria) y el
handshake de autenticación contra el Web Service del SAT.
"""
from satcfdi.models import Signer
from satcfdi.pacs.sat import SAT

from .config import SATConfig


def build_signer(config: SATConfig) -> Signer:
    """
    Lee los bytes del certificado y la llave desde disco, y los combina
    con la contraseña para desencriptar la llave privada EN MEMORIA.
    En ningún momento la llave privada se escribe en texto plano a disco.
    """
    return Signer.load(
        certificate=config.cert_path.read_bytes(),
        key=config.key_path.read_bytes(),
        password=config.password,
    )


def build_sat_service(signer: Signer) -> SAT:
    """
    Crea el cliente del Web Service del SAT. Esta clase de `satcfdi`
    es la que internamente arma las peticiones SOAP firmadas con WS-Security.
    """
    return SAT(signer=signer)