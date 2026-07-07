"""
Pruebas de integracion del flujo web (Fase 2) con datos FICTICIOS.

Usan la BD de prueba de Django (no tocan db.sqlite3) y un PROYECTO.xlsx
TEMPORAL (no tocan el Excel real). Ejecuta:  python manage.py test seguimiento
"""
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.test import Client, TestCase
from openpyxl import Workbook, load_workbook

import config
from seguimiento.models import RFQProcesado


class FlujoWebTests(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self._orig_master = config.ARCHIVO_MAESTRO
        self._orig_backups = config.CARPETA_BACKUPS
        config.ARCHIVO_MAESTRO = self.tmp / "PROYECTO.xlsx"
        config.CARPETA_BACKUPS = self.tmp / "backups"
        self._crear_maestro_temporal()

        self.user = User.objects.create_user("tester", password="secreta-de-prueba")
        self.client = Client()
        self.client.force_login(self.user)

    def tearDown(self):
        config.ARCHIVO_MAESTRO = self._orig_master
        config.CARPETA_BACKUPS = self._orig_backups
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _crear_maestro_temporal(self):
        """Excel ficticio con la estructura real: hoja con espacio, encabezados
        fila 2, datos fila 3, formulas en O y P."""
        wb = Workbook()
        ws = wb.active
        ws.title = config.HOJA_SEGUIMIENTO  # "SEGUIMIENTO " con espacio
        headers = {1: "RFQ", 2: "DESCRIPCION", 3: "FECHA DE ARRANQUE",
                   4: "SOLICITANTE", 6: "PLANTA", 15: "O", 16: "P"}
        for c, t in headers.items():
            ws.cell(row=2, column=c, value=t)
        ws.cell(row=3, column=1, value="100").number_format = "@"
        ws.cell(row=3, column=15, value='=IF(N3<=M3,"SI","NO")')
        ws.cell(row=3, column=16, value="=N3-C3")
        wb.save(config.ARCHIVO_MAESTRO)

    def test_login_requerido(self):
        resp = Client().get("/")
        self.assertEqual(resp.status_code, 302)  # redirige a login

    def test_confirmar_escribe_y_registra(self):
        resp = self.client.post("/confirmar/", {
            "rfq": "228", "descripcion": "Rectificadora plana",
            "solicitante": "Jose Manuel Martinez", "planta": "Ramos",
            "fecha_arranque": "", "archivo_nombre": "pedido_228.txt",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "agregado")

        wb = load_workbook(config.ARCHIVO_MAESTRO)
        ws = wb[config.HOJA_SEGUIMIENTO]
        self.assertEqual(ws["A4"].value, "228")            # agregado en fila 4
        self.assertEqual(ws["A4"].number_format, "@")       # RFQ como texto
        self.assertEqual(ws["O4"].value, '=IF(N4<=M4,"SI","NO")')  # formula ajustada
        self.assertEqual(ws["P4"].value, "=N4-C4")

        reg = RFQProcesado.objects.get(rfq="228")
        self.assertEqual(reg.estado, "ok")
        self.assertEqual(reg.accion, "agregado")
        self.assertIn("fecha_arranque", reg.campos_faltantes)

    def test_confirmar_sin_maestro_da_error_claro(self):
        config.ARCHIVO_MAESTRO.unlink()  # simula maestro ausente
        resp = self.client.post("/confirmar/", {
            "rfq": "999", "descripcion": "", "solicitante": "",
            "planta": "", "fecha_arranque": "", "archivo_nombre": "x.txt",
        })
        self.assertContains(resp, "No existe")
        reg = RFQProcesado.objects.get(rfq="999")
        self.assertEqual(reg.estado, "error")
