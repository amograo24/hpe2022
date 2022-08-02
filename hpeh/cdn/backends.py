from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"

# class MediaRootS3Boto3Storage(S3Boto3Storage): # we arent really using media but i guess let it be here
#     location = "media"
