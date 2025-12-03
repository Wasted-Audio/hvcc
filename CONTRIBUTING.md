# Contribution Guide

You are very welcome to contribute to this project.
In order to simplify the process please try to follow the following suggestions.

Please use English for all communications to include as many people as possible.

## Did you find a bug?

* **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/Wasted-Audio/hvcc/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/Wasted-Audio/hvcc/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a minimal **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

## Want to enhance the code?

### How to start

* Create an issue to discuss your idea before you spend a lot of time into designing or coding.
* Leave an `I like to work on this` comment on an existing issue to let the maintainer know about it.
* Fork the repository into your personal GitHub account to get started.
* Create a separate branch for each feature or bug-fix.

### While contributing

* Make sure that existing static code analysis and tests keep working.
  * run `TOXENV=flake8 tox` for style checking
  * run `TOXENV=mypy tox` for type checking
  * run `tox` for the full suite of tests or `poetry run pytest tests/` for just the test suite.
* Write unit, integration or end-to-end tests as appropriate to your feature or bug-fix.
* Review and update the [Changelog](CHANGELOG.md) and [Documentation](/docs/). Your changes may affect sections of these documents.

### Git best practices

* This project uses [git-flow](https://danielkummer.github.io/git-flow-cheatsheet/) and [Semantic Versioning](https://semver.org/)
* Pull requests will automatically be opened against the `develop` branch.
* Be sure to include a textual description in both your commit(s) and in the pull request if you are implementing a new feature or changing the behavior of an existing one.

## Want to create examples?

Not only the core project can use contributions, but there are also several repositories dedicated to user examples.

This stars with the [hvcc-examples](https://github.com/Wasted-Audio/hvcc-examples) project which contains some general abstractions and requirements. There are links to several dedicated generator projects that are based on this repository.

If you want to create a new generator example project open an [Issue](https://github.com/Wasted-Audio/hvcc-examples/issues) so it can be set up for you.
