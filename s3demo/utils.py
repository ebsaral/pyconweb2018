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

    def get_signed_url(self, path, expires):
        """
        Return signed url
        :param path: Full path to the object
        :param expires: Integer, expire in seconds
        :return: signed url
        """
        params = {
            'Bucket': self.bucket,
            'Key': path
        }

        acl = self.s3.meta.client.get_object_acl(
            Bucket=self.bucket,
            Key=path)

        print("ACL INFO:")
        print(acl)

        url = self.s3.meta.client.generate_presigned_url('get_object',
                                                         Params=params,
                                                         ExpiresIn=expires)
        return url

    def get_url(self, path):
        url = self.get_signed_url(path, expires=1)
        # You can build your own url in this structure:
        # https://{bucket_name}.{s3_url}/{path_to_file}
        return url[:url.index('?')]

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


class SNSManager(object):

    def __init__(self, arn):
        self.arn = arn

        access_key = settings.AWS_ACCESS_KEY_ID
        secret_key = settings.AWS_SECRET_KEY
        region = settings.AWS_REGION

        session = boto3.session.Session()

        self.sns = session.resource(
            'sns',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=True
        )

    def verify_subscription(self, token):
        topic = self.sns.Topic(self.arn)
        topic.confirm_subscription(Token=token)