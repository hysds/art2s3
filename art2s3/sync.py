import os
import logging
import click
from artifactory import ArtifactoryPath
from smart_open import open


# set logger
log_format = "[%(asctime)s: %(levelname)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger('art2s3.sync')
logger.setLevel(logging.INFO)


def _walk(path, api_key):
    """Function to recursively walk an artifactory path."""

    path = ArtifactoryPath(path, apikey=api_key)
    for p in path:
        if p.is_dir():
            yield from _walk(str(p), api_key)
        else:
            yield str(p)


@click.command()
@click.argument('path')
@click.option('--api_key', help="Artifactory API key")
def walk(path, api_key):
    for i in _walk(path, api_key):
        logger.info(i)


def _sync(art_path, s3_path, api_key):
    """Function to recursively walk an artifactory path and
       copy over artifacts to an S3 location."""

    for path in list(_walk(art_path, api_key)):
        rel_path = path.replace(art_path, '')
        s3_abs_path = os.path.join(s3_path, rel_path)
        # skip transfer if object already exists
        try:
            with open(s3_abs_path):
                logger.info(f"{s3_abs_path} already exists. Skipping.")
                continue
        except OSError:
            pass
        logger.info(f"Copying {path} -> {s3_abs_path}...")
        with open(s3_abs_path, 'wb') as fout:
            for line in open(path, 'rb'):
                fout.write(line)
        logger.info("done.")


@click.command()
@click.argument('art_path')
@click.argument('s3_path')
@click.option('--api_key', help="Artifactory API key")
def sync(art_path, s3_path, api_key):
    return _sync(art_path, s3_path, api_key)
