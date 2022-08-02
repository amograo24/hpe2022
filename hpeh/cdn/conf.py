import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = "uhi"  # Your space's name
AWS_S3_ENDPOINT_URL = "sgp1.digitaloceanspaces.com"

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400"
}

AWS_LOCATION = "https://uhi.sgp1.digitaloceanspaces.com/"

STATIC_FILES_STORAGE = "hpeh.cdn.backends.StaticRootS3Boto3Storage"