import boto3
from django.conf import settings


class S3Manager(object):

    def __init__(self, bucket):
        '''
        Manage S3 connection and file upload
        :param bucket: The name of the bucket
        '''

        self.bucket = bucket
        access_key = settings.AWS_ACCESS_KEY_ID
        secret_key = settings.AWS_SECRET_KEY
        region = settings.AWS_REGION

        session = boto3.session.Session()
        self.s3 = session.resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=True
        )

    def upload_file(self, file_obj, path):
        '''
        Upload the file
        :param file_obj: File data
        :param path: File full upload path
        :return:
        '''
        self.s3.Bucket(self.bucket).put_object(Key=path, Body=file_obj)

        # Alternative
        # https://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.upload_file
        # s3.meta.client.upload_file('/tmp/hello.txt', 'mybucket', 'hello.txt')