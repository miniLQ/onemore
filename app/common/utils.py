import uuid
import os

def generate_uuid():
    return (str(uuid.uuid4()).replace('-', ''))[:7]

def linuxPath2winPath(path):
    return os.path.normpath(path).replace(os.sep, os.path.normcase(os.sep))
