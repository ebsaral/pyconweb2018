from django import forms

from s3demo.models import Document


class DocumentUploadForm(forms.Form):

    file = forms.FileField()
