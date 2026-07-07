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
- `correo_formapprovals.py` — funcional. Correos "Form Approvals" (`.txt` / `.eml`).
- `pendientes.py` — PDF / Word (por implementar con archivos reales).

Para un formato nuevo: crea una subclase de `Extractor` y agregala a
`REGISTRO` en `src/extractores/__init__.py`.

## Regla de negocio: RFQ = numero de pedido
Confirmado con el area (Edith): en los correos Form Approvals, el **numero de
RFQ se toma del numero de pedido**.

- `PEDIDO #228`  -> se registra `RFQ = 228`.
- `Request #228` -> tambien se registra `RFQ = 228`.

Este es el comportamiento por defecto (`config.FUENTE_RFQ_CORREO = "pedido"`).
El RFQ se guarda siempre como **texto** en la columna A del maestro.

## Pendientes por confirmar con negocio
- **Fecha de arranque**: el correo Form Approvals NO la incluye. Falta definir
  de donde sale (se captura manual, viene en otro documento, o se usa la fecha
  del pedido). Hoy queda como faltante y se reporta en la bitacora.
- **Planta vs Unidad de Negocio**: falta confirmar si `Selecciona Unidad de
  Negocio` (ej. "Questum Maquinados Ramos") equivale directo a `Planta`, o si
  requiere un mapeo (ej. -> "Ramos Arizpe"). El mapeo opcional esta en
  `config.MAPA_UNIDAD_A_PLANTA` (vacio = se usa el valor tal cual).

## Config
Todo lo ajustable esta en `config.py` (rutas, hoja, columnas, formato de
fecha, marcado de faltantes, fuente del RFQ y mapeo de planta).
