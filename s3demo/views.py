from django.http import Http404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import View
from django.contrib import messages

from s3demo.forms import DocumentUploadForm
from s3demo.models import Document
from s3demo.utils import S3Manager


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
            extension = file.name[file.name.rindex('.') + 1:]
            path = "{extension}/{filename}".format(
                extension=extension, filename=file.name
            )
            manager = S3Manager(bucket='pyconweb2018')
            manager.upload_file(file_obj=file, path=path)
            msg = "Document is uploaded to path: {path}".format(path=path)
            Document.objects.create(name=file.name, url=path)
            messages.add_message(request, messages.SUCCESS, msg)


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


