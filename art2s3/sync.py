import os
import re
import logging
import click
import boto3
import botocore
from pytz import timezone
from artifactory import ArtifactoryPath
from smart_open import open


# set logger
log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('art2s3.sync')
logger.setLevel(logging.INFO)


# regular expressions
S3_URL_RE = re.compile(r's3s?://(.+?)/(.+)$')


def _walk(path, api_key):
    """Function to recursively walk an artifactory path."""

    path = ArtifactoryPath(path, apikey=api_key)
    for p in path:
        if p.is_dir():
            yield from _walk(str(p), api_key)
        else:
            yield p


@click.command()
@click.argument('path')
@click.option('--api_key', help="Artifactory API key")
def walk(path, api_key):
    for p in _walk(path, api_key):
        logger.info(str(p))


def _sync(art_path, s3_path, api_key):
    """Function to recursively walk an artifactory path and
       copy over artifacts to an S3 location."""

    client = boto3.client('s3')
    for p in list(_walk(art_path, api_key)):
        path = str(p)
        stat = p.stat()
        rel_path = path.replace(art_path, '')
        s3_abs_path = os.path.join(s3_path, rel_path)
        match = S3_URL_RE.search(s3_abs_path)
        if not match:
            raise RuntimeError("Failed to parse S3 url.")
        bucket, key = match.groups()
        logger.info(f"bucket: {bucket} key: {key}")
        #logger.info(f"art stat: {stat}")
        mtime_art = stat.mtime.astimezone(timezone('UTC'))
        logger.info(f"art mtime: {mtime_art}")
        # skip transfer if object already exists
        try:
            s3_met = client.head_object(Bucket=bucket, Key=key)
            #logger.info(f"s3_met: {s3_met}")
            mtime_s3 = s3_met['LastModified'].astimezone(timezone('UTC'))
            logger.info(f"s3 mtime: {mtime_s3}")
        except botocore.exceptions.ClientError:
            mtime_s3 = None
        if mtime_s3 is None or mtime_art > mtime_s3:
            local_file = os.path.basename(s3_abs_path)
            try:
                logger.info(f"Downloading {path}...")
                with p.open() as f_in:
                    with open(local_file, 'wb') as f_out:
                        for line in f_in:
                            f_out.write(line)
                logger.info("done.")
                logger.info(f"Uploading {local_file} -> {s3_abs_path}...")
                with open(local_file, 'rb') as f_in:
                    client.upload_fileobj(f_in, bucket, key)
                logger.info("done.")
            finally:
                if os.path.exists(local_file):
                    os.unlink(local_file)
        else:
            logger.info(f"{s3_abs_path} is already current. Skipping.")


@click.command()
@click.argument('art_path')
@click.argument('s3_path')
@click.option('--api_key', help="Artifactory API key")
def sync(art_path, s3_path, api_key):
    return _sync(art_path, s3_path, api_key)
