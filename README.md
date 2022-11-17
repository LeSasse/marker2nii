# marker2nii
Command line tool to map markers back on the brain.

# Set up

You may or may not want to set up a virtual environment.

```sh
python3 -m venv .examplevenv
source .examplevenv/bin/activate
pip install -U pip
```
Then clone the repository to where you would like to install it.
```
git clone https://github.com/LeSasse/marker2nii.git
cd marker2nii
pip install -e .
```

# How to use

Run `marker2nii --help`:

```
usage: marker2nii [-h]
                  marker_file parcellation_file
                  out_folder

Map Markers saved in a text file back on the brain.

positional arguments:
  marker_file        Path to the input marker. If
                     this is a txt file, it is
                     assumed that this consists of
                     one marker in a column vector.
                     If it is a tsv or csv file it is
                     assumed that the first column
                     represents the index and the
                     first row the header. All other
                     columns represent one marker
                     each, with the column name
                     representing the marker name.
  parcellation_file  Path to the parcellation file
                     used to parcellate the marker.
  out_folder         Path to the directory where
                     output nifti files should be
                     saved.

optional arguments:
  -h, --help         show this help message and exit
```
