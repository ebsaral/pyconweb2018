from django.http import Http404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import View
from django.contrib import messages

from s3demo.forms import DocumentUploadForm
from s3demo.models import Document
from s3demo.utils import S3Manager
from s3demo import consts



class DocumentManagerView(TemplateResponseMixin, View):
    template_name = 'main.html'

    @property
    def documents(self):
        return Document.objects.order_by('-create_date')

    def get(self, request, *args, **kwargs):
        form = DocumentUploadForm()
        context = {
            'documents': self.documents,
            'form': form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = DocumentUploadForm(data=request.POST, files=request.FILES)
        documents = Document.objects.order_by('-create_date')

        if form.is_valid():
            file = form.cleaned_data.get('file')
            path = Document.upload_file(file)

            if path:
                msg = "Document is uploaded to path: {path}".format(path=path)
                msg_type = messages.SUCCESS

            else:
                msg = "There was an issue while uploading the file :/ Life is" \
                      "full of suprises."
                msg_type = messages.ERROR

            messages.add_message(request, msg_type, msg)

        context = {
            'documents': documents,
            'form': form
        }
        return self.render_to_response(context)


class DocumentView(TemplateResponseMixin, View):
    template_name = 'detail.html'

    def get(self, request, doc_id, *args, **kwargs):
        try:
            document = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            raise Http404('Yo! Document does not exist on Earth.')

        context = {
            'document': document
        }
        return self.render_to_response(context)


