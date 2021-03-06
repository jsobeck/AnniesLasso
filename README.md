# *The Cannon* 2: Compressed sensing edition
If we take *The Cannon* to large numbers of labels (say chemical abundances),
the model complexity grows very fast. At the same time, we know that most 
chemicals affect very few wavelengths in the spectrum; that is, we know that
the problem is sparse. Here we use standard methods to discover and enforce
sparsity.

## Authors
- **Andrew R. Casey** (Cambridge)
- **David W. Hogg** (NYU) (MPIA) (SCDA)
- **Melissa Ness** (MPIA)

## License
**Copyright 2015, 2016 the authors**.
The code in this repository is released under the open-source **MIT License**.
See the file `LICENSE` for more details.

## Installation
[![Build Status](https://img.shields.io/travis/andycasey/AnniesLasso/master.svg)](https://travis-ci.org/andycasey/AnniesLasso)
[![Coverage Status](https://img.shields.io/coveralls/andycasey/AnniesLasso/master.svg)](https://coveralls.io/github/andycasey/AnniesLasso?branch=master)
[![Scrutinizer](https://img.shields.io/scrutinizer/g/andycasey/AnniesLasso.svg?b=master)](https://scrutinizer-ci.com/g/andycasey/AnniesLasso/?branch=master)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/andycasey/AnniesLasso/blob/master/LICENSE)

``
pip install https://github.com/andycasey/AnniesLasso/archive/master.zip
``

Note that the code is actively being developed in the `develop` branch,
which represents the most up-to-date version.  When the `develop` branch
is stable and has complete test coverage, it will be merged into
`master` and tagged as the first version release.
