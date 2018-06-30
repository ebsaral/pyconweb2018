import json, csv, datetime

from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, \
    HttpResponseBadRequest
from django.urls import reverse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic import View
from django.contrib import messages

from s3demo import consts
from s3demo.forms import DocumentUploadForm
from s3demo.models import Document, Data
from s3demo.utils import SNSManager, S3Manager


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


def download_document(request, doc_id):
    try:
        document = Document.objects.get(pk=doc_id)
    except Document.DoesNotExist:
        raise Http404('Yo! Document does not exist on Earth.')

    url = document.s3_url
    return HttpResponseRedirect(url)


def delete_document(request, doc_id):
    try:
        document = Document.objects.get(pk=doc_id)
    except Document.DoesNotExist:
        raise Http404('Yo! Document does not exist on Earth.')
    document.delete()
    return HttpResponseRedirect(reverse('list_documents'))


def handle_event(request):
    settings.logger.debug('entered handler')
    settings.logger.debug('method: {m}'.format(m=request.method))

    if request.method == 'POST':
        settings.logger.debug('DATA: {data}'.format(data=request.POST))
        data = json.loads(request.POST)
        # TODO: Validate SNS message, maybe with a decorator
        sns_manager = SNSManager(settings.SNS_TOPIC_ARN)
        s3_manager = S3Manager(consts.BUCKET_NAME)

        if 'Token' in data:
            sns_manager.verify_subscription(data['Token'])
        elif 'Message' in data:
            records = data['Message']['Records']
            for record in records:
                path = record['s3']['object']['key']
                object = s3_manager.s3.meta.client.get_object(Key=path)
                stream = object['Body']
                for row in csv.reader(iter(stream)):
                    client, time, value = row.strip('\n').strip('\r').split(',')
                    time = datetime.datetime.strptime(time, '%d/%m/%Y')
                    value = float(value)
                    Data.objects.create(
                        client=client,
                        time=time,
                        value=value
                    )

    return HttpResponse('ok')