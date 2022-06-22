from hub.api.dataset import Dataset
from hub.api.tests.test_api import convert_string_to_pathlib_if_needed
from hub.tests.common import get_dummy_data_path
from hub.util.exceptions import (
    InvalidPathException,
    SamePathException,
    TensorAlreadyExistsError,
)
import numpy as np
import pytest
import hub
import pandas as pd  # type: ignore


@pytest.mark.parametrize("convert_to_pathlib", [True, False])
def test_ingestion_simple(memory_ds: Dataset, convert_to_pathlib: bool):
    path = get_dummy_data_path("tests_auto/image_classification")
    src = "tests_auto/invalid_path"

    if convert_to_pathlib:
        path = convert_string_to_pathlib_if_needed(path, convert_to_pathlib)
        src = convert_string_to_pathlib_if_needed(src, convert_to_pathlib)
        memory_ds.path = convert_string_to_pathlib_if_needed(
            memory_ds.path, convert_to_pathlib
        )

    with pytest.raises(InvalidPathException):
        hub.ingest(
            src=src,
            dest=memory_ds.path,
            images_compression="auto",
            progressbar=False,
            summary=False,
            overwrite=False,
        )

    with pytest.raises(SamePathException):
        hub.ingest(
            src=path,
            dest=path,
            images_compression="jpeg",
            progressbar=False,
            summary=False,
            overwrite=False,
        )

    ds = hub.ingest(
        src=path,
        dest=memory_ds.path,
        images_compression="auto",
        progressbar=False,
        summary=False,
        overwrite=False,
    )

    assert ds["images"].meta.sample_compression == "jpeg"
    assert list(ds.tensors.keys()) == ["images", "labels"]
    assert ds["images"][0:5].numpy().shape == (5, 200, 200, 3)
    assert ds["images"].numpy().shape == (12, 200, 200, 3)
    assert ds["labels"].numpy().shape == (12, 1)
    assert ds["labels"].info.class_names == (
        "class0",
        "class1",
        "class10",
        "class11",
        "class2",
        "class3",
        "class4",
        "class5",
        "class6",
        "class7",
        "class8",
        "class9",
    )


def test_image_classification_sets(memory_ds: Dataset):
    path = get_dummy_data_path("tests_auto/image_classification_with_sets")
    ds = hub.ingest(
        src=path,
        dest=memory_ds.path,
        images_compression="auto",
        progressbar=False,
        summary=False,
        overwrite=False,
    )

    assert list(ds.tensors) == [
        "test/images",
        "test/labels",
        "train/images",
        "train/labels",
    ]

    assert ds["train/images"].meta.sample_compression == "jpeg"
    assert ds["test/images"].numpy().shape == (3, 200, 200, 3)
    assert ds["test/labels"].numpy().shape == (3, 1)
    assert ds["test/labels"].info.class_names == (
        "class0",
        "class1",
        "class2",
    )

    assert ds["train/images"].numpy().shape == (3, 200, 200, 3)
    assert ds["train/labels"].numpy().shape == (3, 1)
    assert ds["train/labels"].info.class_names == (
        "class0",
        "class1",
        "class2",
    )


def test_ingestion_exception(memory_ds: Dataset):
    path = get_dummy_data_path("tests_auto/image_classification_with_sets")
    with pytest.raises(InvalidPathException):
        hub.ingest(
            src="tests_auto/invalid_path",
            dest=memory_ds.path,
            images_compression="auto",
            progressbar=False,
            summary=False,
            overwrite=False,
        )

    with pytest.raises(SamePathException):
        hub.ingest(
            src=path,
            dest=path,
            images_compression="auto",
            progressbar=False,
            summary=False,
            overwrite=False,
        )


def test_overwrite(local_ds: Dataset):
    path = get_dummy_data_path("tests_auto/image_classification")

    hub.ingest(
        src=path,
        dest=local_ds.path,
        images_compression="auto",
        progressbar=False,
        summary=False,
        overwrite=False,
    )

    with pytest.raises(TensorAlreadyExistsError):
        hub.ingest(
            src=path,
            dest=local_ds.path,
            images_compression="auto",
            progressbar=False,
            summary=False,
            overwrite=False,
        )


def test_csv(memory_ds: Dataset):
    path = get_dummy_data_path("tests_auto/csv/deniro.csv")
    with pytest.raises(InvalidPathException):
        hub.ingest(
            src="tests_auto/csv/cities.csv",
            dest=memory_ds.path,
            progressbar=False,
            summary=False,
            overwrite=False,
        )

    ds = hub.ingest(
        src=path,
        dest=memory_ds.path,
        progressbar=False,
        summary=False,
        overwrite=False,
    )
    df = pd.read_csv(path, quotechar='"', skipinitialspace=True)

    assert list(ds.tensors) == ["Year", "Score", "Title"]

    assert ds["Year"].dtype == np.dtype("int")
    np.testing.assert_array_equal(ds["Year"].numpy().reshape(-1), df["Year"].values)

    assert ds["Score"].dtype == np.dtype("int")
    np.testing.assert_array_equal(ds["Score"].numpy().reshape(-1), df["Score"].values)

    assert ds["Title"].htype == "text"
    assert ds["Title"].dtype == str
    np.testing.assert_array_equal(ds["Title"].numpy().reshape(-1), df["Title"].values)


@pytest.mark.parametrize("convert_to_pathlib", [True, False])
def test_dataframe(memory_ds: Dataset, convert_to_pathlib: bool):
    path = get_dummy_data_path("tests_auto/csv/deniro.csv")
    df = pd.read_csv(path, quotechar='"', skipinitialspace=True)
    ds = hub.ingest_dataframe(df, memory_ds.path, progressbar=False)

    with pytest.raises(Exception):
        memory_ds.path = convert_string_to_pathlib_if_needed(
            memory_ds, convert_to_pathlib
        )
        hub.ingest_dataframe(123, memory_ds.path)

    assert list(ds.tensors) == ["Year", "Score", "Title"]

    assert ds["Year"].dtype == np.dtype("int")
    np.testing.assert_array_equal(ds["Year"].numpy().reshape(-1), df["Year"].values)

    assert ds["Score"].dtype == np.dtype("int")
    np.testing.assert_array_equal(ds["Score"].numpy().reshape(-1), df["Score"].values)

    assert ds["Title"].htype == "text"
    assert ds["Title"].dtype == str
    np.testing.assert_array_equal(ds["Title"].numpy().reshape(-1), df["Title"].values)
