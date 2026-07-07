from django import forms

MAX_BYTES = 2 * 1024 * 1024  # 2 MB


class SubirRFQForm(forms.Form):
    """Paso 1: subir el archivo RFQ/correo en .txt."""
    archivo = forms.FileField(
        label="Archivo RFQ / correo (.txt)",
        help_text="Solo .txt (correo Form Approvals pegado como texto). Max 2 MB.",
    )

    def clean_archivo(self):
        f = self.cleaned_data["archivo"]
        if not f.name.lower().endswith(".txt"):
            raise forms.ValidationError("Solo se aceptan archivos .txt")
        if f.size > MAX_BYTES:
            raise forms.ValidationError("El archivo excede el limite de 2 MB.")
        return f


class VistaPreviaForm(forms.Form):
    """Paso 3: preview EDITABLE antes de escribir al Excel.

    Todos los campos salvo RFQ son opcionales; lo que quede vacio se registrara
    como faltante. La fecha de arranque suele venir vacia (el correo no la trae)
    y aqui el usuario puede capturarla manualmente si la conoce.
    """
    rfq = forms.CharField(label="RFQ (numero de pedido)", max_length=50)
    descripcion = forms.CharField(
        label="Descripcion", required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    fecha_arranque = forms.DateField(
        label="Fecha de arranque", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    solicitante = forms.CharField(label="Solicitante", required=False, max_length=200)
    planta = forms.CharField(label="Planta", required=False, max_length=200)
    archivo_nombre = forms.CharField(required=False, widget=forms.HiddenInput)
