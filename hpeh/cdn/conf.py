import os

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "DO00QA4DJ4RPXQETADWA")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "cYQHJCcmEPLhT9iEOSfgNhp12T2urUhJrO0a7PkSYUQ")
AWS_STORAGE_BUCKET_NAME = "uhi"  # Your space's name
AWS_S3_ENDPOINT_URL = "https://sgp1.digitaloceanspaces.com"

AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400"
}

AWS_LOCATION = "https://uhi.sgp1.digitaloceanspaces.com"

STATICFILES_STORAGE = "hpeh.cdn.backends.StaticRootS3Boto3Storage"

print(AWS_SECRET_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
