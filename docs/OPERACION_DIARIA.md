# Operacion diaria (Fase 5)

Guia rapida para operar el sistema RFQ ya desplegado internamente. Complementa
la instalacion ([OPERACION.md](OPERACION.md)) y los scripts/servicio de Windows
([../scripts/README_OPERACION_WINDOWS.md](../scripts/README_OPERACION_WINDOWS.md)).

## Iniciar
- Manual: doble clic o ejecutar `scripts\iniciar_servidor.bat`.
- Automatico: via Task Scheduler o NSSM (ver guia de Windows).

Primero corre `check_operativo --simple`; si falla, NO arranca (protege el Excel).

## Detener
- Si corre en una ventana: `Ctrl + C` en esa ventana.
- Si es servicio NSSM: `nssm stop RFQServidor`.
- Si es Task Scheduler: **Finalizar** la tarea, o cerrar la ventana del `.bat`.

## Reiniciar
- Detener y volver a iniciar con el mismo metodo.
- NSSM: `nssm restart RFQServidor`.

## Saber si esta funcionando
- Abre `http://127.0.0.1:8000/` (o el host/puerto configurado).
- O revisa el chequeo: `scripts\check_operativo.bat` (o `--simple`).
- Pagina de estado (requiere login): `http://.../estado/` -> muestra si existen
  `PROYECTO.xlsx`, la hoja `"SEGUIMIENTO "`, carpetas, BD y si `DEBUG=True`.
  Nunca muestra `SECRET_KEY`.

## Revisar logs
- Archivo principal: `logs\rfq.log`.
- Rotan automaticamente: hasta 5 MB por archivo y 5 backups
  (`rfq.log`, `rfq.log.1`, ... `rfq.log.5`).
- Registran errores de lectura de RFQ, backup, escritura al Excel, permisos y
  confirmaciones exitosas. No guardan `SECRET_KEY`.

## Revisar backups
- Cada escritura crea `PROYECTO_YYYYMMDD_HHMMSS.xlsx` en la carpeta de backups
  (`RFQ_CARPETA_BACKUPS` o `backups/`).
- Ordena por fecha para ver el mas reciente.

## Si Excel esta abierto y bloquea la escritura
- Sintoma: al confirmar, la app dice que el archivo esta abierto en Excel.
- El maestro **no** queda a medias (escritura atomica). Ademas la escritura esta
  serializada por un lock (una a la vez).
- Solucion: cierra `PROYECTO.xlsx` en Excel y reintenta la confirmacion.

## Si `check_operativo` falla
Lee el/los `[X]` que reporta y corrige:
- **DEBUG=True** -> pon `DJANGO_DEBUG=0` en `.env`.
- **SECRET_KEY insegura** -> define `DJANGO_SECRET_KEY` propia.
- **No existe PROYECTO.xlsx / falta la hoja** -> corrige `RFQ_ARCHIVO_MAESTRO` o
  la ubicacion del archivo; verifica el nombre exacto de la hoja (con espacio).
- **Migraciones pendientes / falta permiso** -> `scripts\migrar_y_collectstatic.bat`.
- **Carpeta no escribible** -> revisa permisos de la carpeta/usuario.

## Restaurar un backup
1. Detiene el servidor y cierra Excel.
2. Copia el backup elegido encima del maestro:
   ```bat
   copy C:\ruta\controlada\backups\PROYECTO_20260707_140420.xlsx C:\ruta\controlada\PROYECTO.xlsx
   ```
3. Reinicia el servidor.

---

## Checklist diario
- [ ] El servidor responde (`/` o `/estado/`).
- [ ] `check_operativo --simple` = OK.
- [ ] No hay errores nuevos raros en `logs\rfq.log`.

## Checklist semanal
- [ ] Revisar tamano/rotacion de `logs/`.
- [ ] Revisar que la carpeta de backups tenga copias recientes.
- [ ] Confirmar `DEBUG=0` y `ALLOWED_HOSTS` correctos.
- [ ] Prueba rapida del flujo con un `.txt` ficticio (sin datos reales).
