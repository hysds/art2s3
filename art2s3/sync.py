import os
import click
from artifactory import ArtifactoryPath
from smart_open import open


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
        print(i)


def _sync(art_path, s3_path, api_key):
    """Function to recursively walk an artifactory path and
       copy over artifacts to an S3 location."""

    for path in _walk(art_path, api_key):
        rel_path = path.replace(art_path, '')
        s3_abs_path = os.path.join(s3_path, rel_path)
        # skip transfer if object already exists
        try:
            with open(s3_abs_path):
                print(f"{s3_abs_path} already exists. Skipping.")
        except OSError:
            pass
        print(f"Copying {path} -> {s3_abs_path}...", end='') 
        with open(s3_abs_path, 'wb') as fout:
            for line in open(path, 'rb'):
                fout.write(line)
        print("done.")


@click.command()
@click.argument('art_path')
@click.argument('s3_path')
@click.option('--api_key', help="Artifactory API key")
def sync(art_path, s3_path, api_key):
    return _sync(art_path, s3_path, api_key)
