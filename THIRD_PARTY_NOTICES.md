# Third-party notices

This repository is distributed under the [MIT License](LICENSE). No third-party source code or generated platform distribution is vendored in the canonical skill catalog.

The development and validation environment uses the following separately distributed components:

| Component | Purpose | License | Distribution in this repository |
| --- | --- | --- | --- |
| [PyYAML 6.0.4](https://pypi.org/project/PyYAML/6.0.4/) | Parse YAML frontmatter during structural validation | MIT | Version pinned in `requirements.txt`; package is not vendored |
| [actions/checkout](https://github.com/actions/checkout) | Check out source in CI | MIT | Referenced by immutable commit in the workflow; not vendored |
| [actions/setup-python](https://github.com/actions/setup-python) | Provision Python in CI | MIT | Referenced by immutable commit in the workflow; not vendored |

The project links to the Agent Skills specification and vendor documentation for interoperability facts. Links and short factual references do not incorporate those documents into this repository. Their trademarks and documentation remain subject to their owners' terms.

Contributors must identify any copied or adapted material and confirm that its license is compatible before inclusion. This notice records dependencies and references known from the repository; it is not a provenance guarantee for future contributions.
