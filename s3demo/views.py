import codecs
import json, csv, datetime

from django.conf import settings
from django.http import Http404, HttpResponseRedirect, HttpResponse, \
    HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
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

    @property
    def data(self):
        return Data.objects.order_by('-create_date')

    def get(self, request, *args, **kwargs):
        form = DocumentUploadForm()
        context = {
            'documents': self.documents,
            'data': self.data,
            'form': form,
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = DocumentUploadForm(data=request.POST, files=request.FILES)

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
            'documents': self.documents,
            'data': self.data,
            'form': form,
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


def delete_data(request, data_id):
    try:
        data = Data.objects.get(pk=data_id)
    except Data.DoesNotExist:
        raise Http404('Yo! Data do not exist on Earth.')
    data.delete()
    return HttpResponseRedirect(reverse('list_documents'))


@csrf_exempt
def handle_event(request):
    import logging
    logger = logging.getLogger('pycon')

    if request.method == 'POST':
        data = json.loads(request.body)

        logger.debug("BODY data: {data}".format(data=data))

        # TODO: Validate SNS message, maybe with a decorator
        sns_manager = SNSManager(settings.SNS_TOPIC_ARN)
        s3_manager = S3Manager(consts.BUCKET_NAME)

        if 'Token' in data:
            sns_manager.verify_subscription(data['Token'])
        elif 'Message' in data:
            records = json.loads(data['Message'])['Records']
            for record in records:
                path = record['s3']['object']['key']
                object = s3_manager.s3.meta.client.get_object(
                    Bucket=s3_manager.bucket, Key=path)

                for row in csv.DictReader(
                        codecs.getreader('utf-8')(object['Body'])):
                    c, t, v = row['client'], row['time'], row['value']
                    t = datetime.datetime.strptime(t, '%d/%m/%Y')
                    v = float(v)
                    Data.objects.create(
                        client=c,
                        time=t,
                        value=v
                    )

    return HttpResponse('ok')