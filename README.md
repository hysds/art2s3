# art2s3
Tools for syncing artifacts from Artifactory to S3.

## Installation
1. Clone and create virtualenv:
   ```
   git clone https://github.com/hysds/art2s3.git
   cd art2s3
   virtualenv env
   source env/bin/activate
   ```

2. Install using pip:
   ```
   pip install .
   ```

   or using poetry:
   ```
   pip install poetry
   poetry install
   ```

## Usage
```
$ art2s3 --help
Usage: art2s3 [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  sync
  walk
```

### walk
Recursively print out all artifacts under an artifactory URL:

```
$ art2s3 walk --help
Usage: art2s3 walk [OPTIONS] PATH

Options:
  --api_key TEXT  Artifactory API key
  --help          Show this message and exit.
```

### sync
Recursively sync all artifacts under an artifactory URL to an S3 location:

```
$ art2s3 sync --help
Usage: art2s3 sync [OPTIONS] ART_PATH S3_PATH

Options:
  --api_key TEXT  Artifactory API key
  --help          Show this message and exit.
```
