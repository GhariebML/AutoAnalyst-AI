import gzip
import json

import pandas as pd
import pytest

from autoanalyst.data_loading.loader import DatasetLoader
from autoanalyst.exceptions import DataLoadError, FileAccessError, UnsupportedFileTypeError


def test_load_csv(sample_csv_path):
    loader = DatasetLoader()
    df, meta = loader.load(sample_csv_path)
    assert df.shape[0] > 0
    assert meta.file_format == "csv"


def test_missing_file_raises():
    loader = DatasetLoader()
    with pytest.raises(FileAccessError):
        loader.load("/tmp/does_not_exist_xyz.csv")


def test_unsupported_extension_raises(tmp_path):
    path = tmp_path / "file.exe"
    path.write_bytes(b"binary")
    loader = DatasetLoader()
    with pytest.raises(UnsupportedFileTypeError):
        loader.load(str(path))


def test_empty_file_raises(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    loader = DatasetLoader()
    with pytest.raises(FileAccessError):
        loader.load(str(path))


def test_load_tsv(tmp_path, sample_df):
    path = tmp_path / "sample.tsv"
    sample_df.to_csv(path, sep="\t", index=False)
    loader = DatasetLoader()
    df, meta = loader.load(str(path))
    assert df.shape[1] == sample_df.shape[1]


def test_load_gzip_csv(tmp_path, sample_df):
    path = tmp_path / "sample.csv.gz"
    with gzip.open(path, "wt") as f:
        sample_df.to_csv(f, index=False)
    loader = DatasetLoader()
    df, meta = loader.load(str(path))
    assert df.shape[0] == sample_df.shape[0]
    assert meta.file_format == "gzip_csv"


def test_load_json_records(tmp_path):
    path = tmp_path / "sample.json"
    records = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    path.write_text(json.dumps(records))
    loader = DatasetLoader()
    df, meta = loader.load(str(path))
    assert list(df.columns) == ["a", "b"]
    assert df.shape[0] == 2


def test_load_excel(tmp_path, sample_df):
    path = tmp_path / "sample.xlsx"
    sample_df.to_excel(path, index=False)
    loader = DatasetLoader()
    df, meta = loader.load(str(path))
    assert df.shape[0] == sample_df.shape[0]
    assert meta.file_format == "excel"


def test_load_parquet(tmp_path, sample_df):
    path = tmp_path / "sample.parquet"
    sample_df.to_parquet(path)
    loader = DatasetLoader()
    df, meta = loader.load(str(path))
    assert df.shape[0] == sample_df.shape[0]
    assert meta.file_format == "parquet"
