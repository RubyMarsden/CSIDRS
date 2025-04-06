# CSIDRS - A stable isotope data reduction software for data from the CAMECA 1280 secondary ion mass spectrometer

This program accompanies the paper *CSIDRS – stable isotope data reduction software for the CAMECA LG SIMS* (Marsden et al, 2024).

## Getting started
### Standalone executables
Standalone executables are available for Ubuntu and Windows
[here](https://github.com/RubyMarsden/CSIDRS/releases). These should be downloadable
and runnable without any further action.

* The executable may take up to 30 seconds to show the window the first time you run the program. Subsequent runs
should be faster.
### Running the python code directly
CSIDRS uses Python 3.8.

You can clone the existing GitHub repository into a local directory on your computer following the instructions [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

Alternatively the source code for each release is available
[here](https://github.com/RubyMarsden/Crayfish/releases). Download the source code, unzip
it into a folder. Open a terminal and navigate inside the unzipped folder. Run
```
pip install requirements.txt
```
in order to ensure you have the correct set of Python modules installed. Then to start the program run:
```
python src/main.py
```
### Naming conventions
Unfortunately, there are some specific naming conventions which need to be followed in order for the program to work with minimum fuss. The reference material names must be the same as those listed in the reference material dialog.
Additionally, if a sample name is separated by "_" or "-" (e.g., TEMORA-2) the program will separate the "TEMORA" and the "2" and will struggle to name the sample correctly.
A good file name would be "MountName_Operator_Date_SampleName@1.asc".

## Program flexibility
This program was written to have a level of flexibility in order to add new stable isotope methods as they are designed.
### Adding a method
Using [the HACKING.md file](HACKING.md) a user with basic python knowledge can add a stable isotope method. Additionally, users with no python knowledge can create an issue on the GitHub repository.
#### Creating a GitHub issue for the repository
Issues can be added by users with a GitHub account [here](https://github.com/RubyMarsden/CSIDRS/issues). Issues which are additional method suggestions should be labelled as an enhancement.
When reporting a bug as an issue please detail exactly the circumstances in which is happened and label the issue as a bug.
