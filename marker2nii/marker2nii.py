"""Read a marker from txt/csv/tsv file and map into nii using an atlas."""

# Author: Leonard Sasse <l.sasse@fz-juelich.de>

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
from nilearn import image


def read_markers(markers_path):
    """Read a marker file.

    Load either txt, csv or tsv files. delimiter is inferred from extension
    If this is a txt file, it is assumed this consists of one marker
    represented in a column vector. In this case the file name is the name of
    the marker. If it is a tsv or csv it is assumed that
    first column is the index, first row is the header. All other columns
    represent one marker each, with the column name representing the marker
    name

    Parameters
    ----------
    markers_path : str or os.Path-like
        path to txt, csv or tsv file.

    Returns
    -------
    markers : pd.DataFrame

    """
    _, tail = os.path.split(markers_path)
    _, ext = os.path.splitext(markers_path)

    assert ext in [
        ".csv",
        ".tsv",
        ".csv",
    ], "Marker file should be a txt, csv, or tsv file!"
    if ext in [".txt"]:
        marker = pd.DataFrame()
        marker[tail] = np.loadtxt(markers_path, dtype=np.float)
        return marker
    else:
        extensions = {".csv": ",", ".tsv": "\t"}
        return pd.read_csv(markers_path, index_col=0, sep=extensions[ext])


def load_atlas(path):
    """Load atlas file."""
    return image.load_img(path)


def map_to_atlas(marker, atlas):
    """Map values of a marker to the correct volumetric location in atlas.

    Parameters
    ----------
    marker : np.array, array-like
        length should correspond to number of regions in the given atlas
        index of each value corresponds to the label in the marker - 1,
        i.e. value at index 0 corresponds to ROI 1 etc.
    atlas : str, os.Path-like
        path to a nifti file for a volumetric parcellation

    Returns
    -------
    marker_img : niimg
        a nifti image of the marker values mapped back to the corresponding
        ROI's in the brain

    """
    marker = np.array(marker)
    atlas_array = np.array(atlas.dataobj)
    rois = np.unique(atlas_array)
    assert len(rois) - 1 == len(
        marker
    ), "Length of marker array and n ROI's are inconsistent!"
    marker_img_array = np.zeros(atlas_array.shape)
    marker_no_na = marker[~np.isnan(marker)]
    marker_min = np.min(marker_no_na)
    marker_max = np.max(marker_no_na)

    for roi in rois:
        roi = int(roi)
        if roi == 0:
            continue

        value = marker[roi - 1]
        marker_img_array[atlas_array == roi] = value

    marker_img_array[np.isnan(marker_img_array)] = marker_min - 20000
    marker_img_array[atlas_array == 0] = marker_min - 20000
    marker_img = image.new_img_like(atlas, marker_img_array)
    marker_img.header["cal_max"] = marker_max
    marker_img.header["cal_min"] = marker_min
    return marker_img


def prepare_output(out_folder, marker_file):
    """Prepare output directory."""
    if not os.path.isdir(out_folder):
        raise FileNotFoundError(f"{out_folder} is not an existing directory!")

    _, tail = os.path.split(marker_file)
    file_name, _ = os.path.splitext(tail)
    output_folder = Path(out_folder) / file_name
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    return output_folder


def parse_args():
    """Parse arguments for the CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Map Markers saved in a text file back on the brain." "\n"
        )
    )
    parser.add_argument(
        "marker_file",
        type=str,
        help=(
            "Path to the input marker. If this is a txt file, it is assumed"
            " that this consists of one marker in a column vector. If it is a "
            "tsv or csv file it is assumed that the first column represents "
            "the index and the first row the header. All other columns "
            "represent one marker each, with the column name representing the "
            "marker name."
        ),
    )
    parser.add_argument(
        "parcellation_file",
        type=str,
        help=("Path to the parcellation file used to parcellate the marker."),
    )
    parser.add_argument(
        "out_folder",
        type=str,
        help=(
            "Path to the directory where output nifti files should be saved."
        ),
    )
    return parser.parse_args()


def main():
    """Run marker2nii."""
    args = parse_args()
    output_folder = prepare_output(args.out_folder, args.marker_file)

    parcellation = load_atlas(args.parcellation_file)
    markers = read_markers(args.marker_file)
    n_total = len(markers.columns)
    for i, marker in enumerate(markers):
        print(f"Marker {i}/{n_total}", end="\r")
        marker_img = map_to_atlas(markers[marker], parcellation)
        output_file = output_folder / f"{marker}.nii.gz"
        marker_img.to_filename(output_file)
