# 🧾 SAT CFDI Downloader

Herramienta de automatización en Python para la **descarga masiva de CFDIs recibidos** directamente desde el Web Service oficial del SAT, usando la librería open-source [`satcfdi`](https://github.com/SAT-CFDI/python-satcfdi). Los comprobantes descargados se parsean y exportan a un archivo `.xlsx` listo para análisis contable o financiero.

> **Nota de seguridad:** Este proyecto nunca usa Web Scraping, Selenium ni Playwright. Toda la comunicación es vía el Web Service oficial del SAT (protocolo SOAP + WS-Security). Ninguna credencial o archivo fiscal se almacena en el repositorio.

---

## 📋 Tabla de Contenidos

- [¿Qué problema resuelve?](#-qué-problema-resuelve)
- [Arquitectura del proyecto](#-arquitectura-del-proyecto)
- [Flujo de operación](#-flujo-de-operación)
- [Requisitos](#-requisitos)
- [Instalación y configuración](#-instalación-y-configuración)
- [Uso](#-uso)
- [Personalización](#-personalización)
- [Seguridad](#-seguridad)
- [Créditos](#-créditos)
- [Licencia](#-licencia)

---

## ❓ ¿Qué problema resuelve?

Descargar CFDIs uno por uno desde el portal del SAT es un proceso manual, lento e impráctico para cualquier persona física o moral con volumen medio-alto de facturas. Este proyecto automatiza el ciclo completo:

1. **Autenticación** ante el SAT usando tu e.firma (FIEL)
2. **Solicitud** de descarga masiva por rango de fechas
3. **Verificación** del estado de la solicitud (polling automático)
4. **Descarga** de los paquetes `.zip` con los XMLs
5. **Parseo** de cada CFDI y extracción de campos clave
6. **Exportación** a un archivo `.xlsx` listo para Excel o Numbers

El resultado es una hoja de cálculo consolidada con todos tus comprobantes organizados por folio, emisor, conceptos, IVA y montos — sin intervención manual.

---

## 🗂 Arquitectura del proyecto

```
sat-cfdi-downloader/
│
├── .env                          # Credenciales locales (NUNCA se sube a Git)
├── .env.example                  # Plantilla pública de variables requeridas
├── .gitignore                    # Blindado contra fuga de credenciales y CFDIs
├── requirements.txt              # Dependencias del proyecto
├── README.md                     # Este archivo
│
├── credentials/                  # Archivos de e.firma (NUNCA se suben a Git)
│   ├── .gitkeep                  # Marcador para que Git registre la carpeta vacía
│   ├── tu_certificado.cer        # Certificado público de tu e.firma
│   └── tu_llave.key              # Llave privada de tu e.firma (cifrada)
│
├── downloads/                    # Paquetes y reportes generados (NUNCA se suben a Git)
│   ├── .gitkeep
│   ├── <ID_PAQUETE>.zip          # ZIP descargado del SAT con los XMLs
│   └── cfdis_consolidado.xlsx    # Reporte final exportado
│
├── src/
│   └── sat_downloader/           # Paquete principal (lógica de negocio)
│       ├── __init__.py
│       ├── config.py             # Carga y valida variables del .env
│       ├── auth.py               # Construye el Signer y el cliente SAT
│       ├── solicitudes.py        # Ciclo: solicitar → verificar → descargar
│       ├── parser.py             # Parsea XMLs y extrae campos clave
│       └── utils/
│           └── __init__.py
│
├── scripts/                      # Puntos de entrada ejecutables
│   ├── test_handshake.py         # Prueba de autenticación (Fase 1)
│   ├── descarga_masiva.py        # Descarga de CFDIs (Fase 2)
│   └── parsear_cfdis.py          # Parser y exportación a Excel (Fase 3)
│
└── tests/
    └── __init__.py
```

### Responsabilidad de cada módulo

| Módulo | Responsabilidad |
|---|---|
| `config.py` | Leer el `.env` y validar que todas las variables estén presentes antes de ejecutar cualquier cosa. Falla rápido con mensajes claros. |
| `auth.py` | Cargar el certificado y la llave privada en memoria, desencriptarla con la contraseña y construir el cliente del Web Service del SAT. |
| `solicitudes.py` | Implementar el ciclo de tres pasos del SAT: solicitar descarga → consultar estado en loop → descargar paquetes ZIP. |
| `parser.py` | Abrir cada ZIP, leer los XMLs, extraer los campos de interés y devolver una lista de filas listas para exportar. |

---

## 🔄 Flujo de operación

```
.env (credenciales)
      │
      ▼
config.py ──► Validación de variables
      │
      ▼
auth.py ──► Signer (FIEL desencriptada en memoria)
      │
      ▼
SAT Web Service (SOAP + WS-Security)
      │
      ├── solicitar_descarga() ──► IdSolicitud
      │
      ├── verificar_estado()   ──► polling hasta TERMINADA
      │                              │
      │                              ▼
      └── descargar_paquetes() ──► .zip en downloads/
                                       │
                                       ▼
                                  parser.py
                                       │
                                       ▼
                              cfdis_consolidado.xlsx
```

---

## 🛠 Requisitos

- Python 3.11 o superior
- macOS, Linux o Windows (WSL recomendado en Windows)
- e.firma (FIEL) vigente emitida por el SAT
- Los archivos `.cer` y `.key` de tu e.firma y su contraseña

---

## ⚙️ Instalación y configuración

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/sat-cfdi-downloader.git
cd sat-cfdi-downloader
```

### 2. Crea el entorno virtual e instala dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configura tus credenciales

Copia la plantilla del archivo de entorno:

```bash
cp .env.example .env
```

Coloca los archivos de tu e.firma en la carpeta `credentials/`:

```bash
cp /ruta/a/tu_certificado.cer credentials/
cp /ruta/a/tu_llave.key credentials/
```

Edita el archivo `.env` con tus datos reales:

```env
SAT_RFC=TURF123456XX
SAT_CSD_CERT_PATH=credentials/tu_certificado.cer
SAT_CSD_KEY_PATH=credentials/tu_llave.key
SAT_CSD_PASSWORD=tu_contraseña_de_efirma
```

> ⚠️ Nunca compartas tu archivo `.env` ni tus archivos `.cer` o `.key`. El `.gitignore` ya los excluye del repositorio.

### 4. Verifica la autenticación

```bash
python scripts/test_handshake.py
```

Si todo está bien verás:
```
✅ Handshake preparado correctamente. El Signer es válido y firma mensajes.
```

---

## 🚀 Uso

### Paso 1 — Descarga masiva de CFDIs

Edita el rango de fechas en `scripts/descarga_masiva.py`:

```python
fecha_inicial = date(2025, 1, 1)
fecha_final   = date(2025, 12, 31)
```

Ejecuta:

```bash
python scripts/descarga_masiva.py
```

El script solicitará la descarga al SAT, esperará a que esté lista y guardará el `.zip` en `downloads/`.

### Paso 2 — Parsear y exportar a Excel

```bash
python scripts/parsear_cfdis.py
```

Esto procesará todos los `.zip` en `downloads/` y generará `downloads/cfdis_consolidado.xlsx` con las siguientes columnas:

| Columna | Descripción |
|---|---|
| Folio | Folio del comprobante |
| Fecha | Fecha de emisión |
| Método de Pago | PUE, PPD, etc. |
| Lugar de Expedición | CP de expedición |
| RFC Emisor | RFC de quien emitió la factura |
| Nombre Emisor | Razón social del emisor |
| Cantidad | Cantidad del concepto |
| Descripción | Descripción del concepto |
| IVA | Importe de IVA del concepto |
| Subtotal | Subtotal del comprobante |
| Total | Total del comprobante |

> Cada concepto dentro de un CFDI genera una fila independiente, por lo que el total de filas puede ser mayor al total de CFDIs.

---

## 🔧 Personalización

### Cambiar el rango de fechas

En `scripts/descarga_masiva.py`, modifica:

```python
fecha_inicial = date(2025, 1, 1)   # Año, mes, día
fecha_final   = date(2025, 6, 30)
```

### Descargar CFDIs emitidos en lugar de recibidos

En `src/sat_downloader/solicitudes.py`, en la función `solicitar_descarga`, cambia:

```python
# Recibidos (default)
response = sat_service.recover_comprobante_received_request(...)

# Emitidos
response = sat_service.recover_comprobante_issued_request(...)
```

### Agregar más campos al Excel

En `src/sat_downloader/parser.py`, dentro de `parsear_cfdi()`, agrega los campos que necesites al diccionario de cada fila. Consulta la [especificación técnica del CFDI 4.0](https://www.sat.gob.mx/consulta/65884/conoce-las-caracteristicas-del-cfdi-version-4.0) para ver todos los atributos disponibles.

En `scripts/parsear_cfdis.py`, agrega el nombre de la nueva columna a la lista `COLUMNAS`.

### Ajustar el tiempo de espera del polling

En `scripts/descarga_masiva.py`:

```python
ids_paquetes = verificar_estado(
    sat_service,
    id_solicitud,
    intervalo_segundos=60,   # Segundos entre cada consulta al SAT
    max_intentos=10,         # Número máximo de intentos antes de abortar
)
```

---

## 🔒 Seguridad

Este proyecto fue diseñado con seguridad como prioridad desde el primer commit:

- **Cero hardcoding:** ninguna credencial, RFC o ruta sensible está escrita en el código fuente.
- **`python-dotenv`:** todas las credenciales viven exclusivamente en el archivo `.env` local.
- **`.gitignore` blindado:** excluye `.env`, `*.cer`, `*.key`, `*.pem`, el contenido de `downloads/` y cachés de Python. Ningún dato sensible puede llegar al repositorio remoto de forma accidental.
- **Desencriptado en memoria:** la llave privada de la e.firma se desencripta en RAM y nunca se escribe en texto plano a disco.
- **Sin dependencias de navegador:** no se usa Selenium, Playwright ni ninguna técnica de scraping. La comunicación es exclusivamente vía el Web Service oficial del SAT.

---

## 🙏 Créditos

Este proyecto no sería posible sin el trabajo de [**@josuealvarado**](https://github.com/SAT-CFDI) y los colaboradores de la librería open-source [`python-satcfdi`](https://github.com/SAT-CFDI/python-satcfdi).

`satcfdi` abstrae toda la complejidad del protocolo SOAP + WS-Security que requiere el SAT, incluyendo la construcción y firma de mensajes XML, la gestión automática del token de autenticación y los modelos de datos del ciclo de descarga masiva. Sin esta librería, implementar este cliente desde cero requeriría cientos de líneas de código de bajo nivel de criptografía y XML.

Si este proyecto te fue útil, considera también darle una ⭐ al repositorio original de `satcfdi`.

---

## 📄 Licencia

MIT License — consulta el archivo `LICENSE` para más detalles.

---

*Desarrollado por [Ismael](https://github.com/tu-usuario) · Economía + Ciencia de Datos · UNAM FES Aragón*
