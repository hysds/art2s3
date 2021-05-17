import click
from artifactory import ArtifactoryPath


@click.command()
@click.option('--path', help="Artifactory path")
@click.option('--api_key', help="Artifactory API key")
def walk(path, api_key):
    path = ArtifactoryPath(path, apikey=api_key)
    for p in path:
        print(p)
