from storages.backends.s3boto3 import S3Boto3Storage


class SpiS3Boto3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def download_link_with_name(self, name, *, filename):
        parameters = {}
        parameters['ResponseContentDisposition'] = f'attachment; filename={filename}'

        download_url = super().url(name, parameters=parameters)

        return download_url