from django.db import models
from django.utils.functional import cached_property
from django.utils.encoding import force_text, smart_text

from s3demo.utils import S3Manager
from s3demo import consts


class Document(models.Model):
    name = models.TextField('Name')
    url = models.TextField('URL')
    create_date = models.DateTimeField(auto_now_add=True)

    EXPIRES = 60
    ENABLE_EXPIRING = False

    @property
    def s3_url(self):
        """
        Generate pre-signed url with expiration time if expiring enabled
        :return: url string
        """
        manager = S3Manager(bucket=consts.BUCKET_NAME)
        if self.ENABLE_EXPIRING:
            url = manager.get_signed_url(self.url, expires=self.EXPIRES)
        else:
            url = manager.get_url(self.url)
        return url

    @classmethod
    def upload_file(cls, file):
        """
        Upload file and create a document object if successful
        :param file: file object
        :return: string (full path where file is uploaded)
        """
        extension = file.name[file.name.rindex('.') + 1:]
        path = "{extension}/{filename}".format(
            extension=extension, filename=file.name
        )

        manager = S3Manager(bucket=consts.BUCKET_NAME)
        try:
            manager.upload_file(file_obj=file, path=path)
            cls.objects.create(name=file.name, url=path)
            return path
        except Exception as e:
            return None


class Data(models.Model):
    client = models.CharField(max_length=255)
    time = models.DateTimeField()
    value = models.FloatField()
    create_date = models.DateTimeField(auto_now_add=True)
