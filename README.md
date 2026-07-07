# MVP - Actualizador de PROYECTO.xlsx desde RFQ

Automatizacion local que lee archivos RFQ de `entrada/`, extrae los campos
clave y actualiza la hoja **SEGUIMIENTO** de `PROYECTO.xlsx` sin perder
formato, formulas, bordes ni filtros.

## Instalacion
```
pip install -r requirements.txt
```

## Uso
1. Coloca tu maestro real en `PROYECTO.xlsx` (raiz del proyecto).
2. **Primero** analiza su estructura:
   ```
   python inspeccionar.py
   ```
   Ajusta `config.py` (hoja, fila de encabezados, columnas) segun lo que reporte.
3. Deja archivos RFQ en `entrada/` (por ahora `.csv`; ver formatos abajo).
4. Ejecuta:
   ```
   python main.py
   ```
5. Revisa el reporte en `reportes/`.

## Como funciona
- Antes de escribir hace **backup** en `backups/`.
- Busca el RFQ en la columna A: si existe **actualiza** esa fila; si no, **agrega** al final.
- Solo toca columnas A, B, C, D, F. Las demas quedan intactas.
- RFQ siempre como texto; fechas como fechas reales de Excel.
- Guarda de forma atomica (temp + replace) para no corromper el archivo.
- Los archivos ya leidos se mueven a `procesados/`.

## Formato CSV de entrada (funcional hoy)
Encabezados exactos:
```
rfq,descripcion,fecha_arranque,solicitante,planta
```
Fechas en `dd/mm/aaaa`. RFQ puede ser `185`, `185.5`, `131/4`.

## Extractores
`src/extractores/` — un plugin por tipo de archivo:
- `csv_manual.py` — funcional (carga manual/masiva).
- `excel_rfq.py` — plantilla adaptable para RFQ en Excel.
- `pendientes.py` — PDF / Word / correo (por implementar con archivos reales).

Para un formato nuevo: crea una subclase de `Extractor` y agregala a
`REGISTRO` en `src/extractores/__init__.py`.

## Config
Todo lo ajustable esta en `config.py` (rutas, hoja, columnas, formato de
fecha, marcado de faltantes).
