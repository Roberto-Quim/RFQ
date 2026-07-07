from django.conf import settings
from django.db import models


class RFQProcesado(models.Model):
    """Historial/auditoria de cada RFQ procesado desde la web.

    NOTA: puede contener datos reales -> db.sqlite3 esta ignorado por Git.
    """
    ESTADO_OK = "ok"
    ESTADO_ERROR = "error"
    ESTADOS = [(ESTADO_OK, "OK"), (ESTADO_ERROR, "Error")]

    rfq = models.CharField("RFQ", max_length=50)
    descripcion = models.TextField("Descripcion", blank=True)
    fecha_arranque = models.DateField("Fecha de arranque", null=True, blank=True)
    solicitante = models.CharField("Solicitante", max_length=200, blank=True)
    planta = models.CharField("Planta", max_length=200, blank=True)

    archivo_nombre = models.CharField("Archivo origen", max_length=255, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ESTADO_OK)
    accion = models.CharField("Accion", max_length=20, blank=True)  # agregado/actualizado
    campos_faltantes = models.CharField(max_length=255, blank=True)
    # Auditoria (Fase 3):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="rfqs_procesados",
        verbose_name="Confirmado por",
    )
    campos_editados = models.CharField(
        "Campos editados manualmente", max_length=255, blank=True
    )
    mensaje = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "RFQ procesado"
        verbose_name_plural = "RFQ procesados"
        permissions = [
            ("puede_confirmar", "Puede confirmar escritura al Excel"),
        ]

    def __str__(self):
        return f"RFQ {self.rfq} ({self.accion or self.estado})"
