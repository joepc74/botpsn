# botpsn

Este proyecto permite consultar y comparar precios de juegos de PlayStation en diferentes tiendas a través de web scraping.

## Requisitos
- Python 3.12 o superior
- Paquetes: `requests`, `beautifulsoup4`

Instalación de dependencias:
```bash
pip install requests beautifulsoup4
```

## Uso
Ejecuta el script principal para obtener información de precios de juegos usando su SKU:

```bash
python botpsn.py
```

El script buscará los precios en las tiendas configuradas en `stores.py` y mostrará el precio más barato encontrado para cada SKU consultado.

## Archivos principales
- `botpsn.py`: Script principal para consultar precios.
- `stores.py`: Configuración de las tiendas y expresiones regulares para extraer precios.

## Notas
- El script utiliza la API de currency-api para obtener tasas de cambio y convertir precios a euros si es necesario.
- Asegúrate de que las expresiones regulares y configuraciones en `stores.py` estén actualizadas para cada tienda soportada.

## Configuración (`config.py`)

Crea un archivo `config.py` en el directorio principal con la siguiente estructura:

```python
# Clave de la API para currency-api
TELEGRAM_TOKEN = "tu_clave_api_aqui"
```

Asegúrate de mantener tu clave de API segura y no compartirla públicamente.

## Registro de actividad (logs)

El script genera un archivo de log llamado `botpsn.log` en el directorio principal con información sobre la ejecución. Si deseas ver los mensajes de log directamente en pantalla, ejecuta el script con el parámetro de línea de comando `-debug`:

```bash
python botpsn.py -debug
```