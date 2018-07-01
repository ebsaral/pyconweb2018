import os

BUCKET_NAME = os.getenv('BUCKET_NAME')
EXPIRES = int(os.getenv('EXPIRES', 60)) # Default 60 seconds
ENABLE_EXPIRING = bool(int(os.getenv('ENABLE_EXPIRING', 0)))
