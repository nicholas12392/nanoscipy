# nanoscipy

nanoscipy has been made, to ease the more heavy data-handling, -processing, and - analysis. 
This package is being readily updated at the moment, so be sure to keep up, as new and useful additions and fixes are 
very likely to be included.

## Installation and updating
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install nanoscipy like below. 
Rerun this command to check for and install  updates .
```bash
pip install nanoscipy
```
For package updates, use:
```bash
pip install --upgrade nanoscipy
```
Note that if you're using anaconda, you might have to install the module from the anaconda terminal instead (or use 
conda rather than pip)
## Usage
### Import
Currently, the package consists of four distinct modules:
```bash
nanoscipy.functions
```
Contains most of the practical functions of nanoscipy. 

```bash
nanoscipy.modules
```
Contains all classes of nanoscipy.

```bash
nanoscipy.util
```
Contains all utility functions and lists used within nanoscipy. Different modules use functions from this module. 
Note that some of these functions may be of practical use, but many are simply throw-away functions to increase 
readability.

```bash
nanoscipy.mathpar
```
The module with the mathematical parser of nanoscipy. Specifically, this contains the practical function parser(), which
is the collective parser itself.

