from django.contrib import admin

from .models import RFQProcesado


@admin.register(RFQProcesado)
class RFQProcesadoAdmin(admin.ModelAdmin):
    list_display = ("rfq", "accion", "estado", "solicitante", "planta",
                    "campos_faltantes", "creado_en")
    list_filter = ("estado", "accion", "creado_en")
    search_fields = ("rfq", "solicitante", "planta", "descripcion")
    readonly_fields = ("creado_en",)
