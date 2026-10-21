# Building the Python Package

This document describes how to build and publish the OpenPlate Python package.

For Python package distribution, the package metadata and build artifacts should make it straightforward for a consumer to identify the project license, locate the source repository, and rebuild the package from source.

OpenPlate is structured to support that by:

- Declaring the package license in `pyproject.toml`
- Publishing source repository and documentation links in package metadata
- Including the `LICENSE` and `NOTICE` files in distribution artifacts
- Building the package from the checked-in source tree with a manually supplied semantic version

## Build the Python package locally

From the repository root:

```sh
python -m build
```

If `python -m build` fails with `No module named build.__main__`, install the build package first:

```sh
python -m pip install build
python -m build
```

The generated source and wheel artifacts are written to `dist/`.

## Publish with GitHub Actions

The repository includes a manual workflow at `.github/workflows/python-publish.yml`.

It does not run on pull requests, merges, or tags. It runs only when started manually from GitHub Actions.

### Workflow inputs

Required inputs:

- `semantic_version`: The version to publish. This must match the Semantic Versioning 2.0.0 format, for example `1.2.3`, `1.2.3-rc.1`, or `1.2.3+build.5`.

### Required repository configuration

Required repository variables:

- `PYPI_REPOSITORY_URL`: The package upload endpoint, for example `https://upload.pypi.org/legacy/`, `https://test.pypi.org/legacy/`, or an internal Python package repository endpoint.

Optional repository variables:

- `PYPI_USERNAME`: Package repository username. If this is not set as a variable, the workflow will read it from the `PYPI_USERNAME` secret.
- `PYPI_PASSWORD`: Package repository password or token. If this is not set as a variable, the workflow will read it from the `PYPI_PASSWORD` secret.

Required repository secrets:

- `PYPI_USERNAME`: Package repository username when not stored in a repository variable.
- `PYPI_PASSWORD`: Package repository password or token when not stored in a repository variable.

### Published package name

The workflow publishes one package:

- `openplate`

### What the workflow does

When run manually, the workflow:

1. Validates that `semantic_version` matches the SemVer 2.0.0 regex.
2. Validates that the required package repository configuration is present.
3. Updates the package version in `src/openplate/__init__.py` for the build.
4. Builds the source distribution and wheel from the checked-in source.
5. Runs `twine check` against the generated artifacts.
6. Uploads the package artifacts to the configured package repository.