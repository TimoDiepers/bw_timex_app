# bw_timex_app

<!-- [![Read the Docs](https://img.shields.io/readthedocs/timex?label=documentation)]([https://docs.brightway.dev/projects/bw-timex/en/latest/](https://bw-timex-app.readthedocs.io/en/latest/)) -->
[![PyPI - Version](https://img.shields.io/pypi/v/bw-timex-app?color=%2300549f)](https://pypi.org/project/bw-timex-app/)
[![Conda Version](https://img.shields.io/conda/v/diepers/bw_timex_app?label=conda)](https://anaconda.org/diepers/bw_timex_app)
![Conda - License](https://img.shields.io/conda/l/diepers/bw_timex_app)

## Installation


To install the `bw_timex_app`, just install the package in a new Conda environment (in this example named `timex_app`).
Depending on your operating system, you need to install a slightly different version:

### Linux, Windows, or MacOS (x64)

```console
conda create -n timex_app -c conda-forge -c cmutel -c diepers brightway25 bw_timex_app
```

### macOS (Apple Silicon/ARM)

```console
conda create -n timex_app -c conda-forge -c cmutel -c diepers brightway25_nosolver scikit-umfpack numpy==1.24 matplotlib==3.5.2 bw_timex_app
```

## Running the App

To run the `bw_timex_app`, just do the following:

1. Activate the environment:

```console
conda activate timex_app
```

2. Run the app:

```console
bw-timex
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][License],
_bw_timex_app_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://bw_timex_app.readthedocs.io/en/latest/usage.html
[License]: https://github.com/TimoDiepers/bw_timex_app/blob/main/LICENSE
[Contributor Guide]: https://github.com/TimoDiepers/bw_timex_app/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/TimoDiepers/bw_timex_app/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_bw_timex_app
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
