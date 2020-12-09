import pytest

from interpret.util.all import gen_perf_dicts
from interpret.util.all import gen_feat_val_list, gen_name_from_class
from interpret.util.all import reverse_map, unify_data, unify_vector
import numpy as np
import pandas as pd


@pytest.fixture
def fixture_feat_val_list():
    return [("race", 3), ("age", -2), ("gender", 1)]


def test_unify_vector_on_ndim_array():
    y = np.array([[0], [1], [2], [3]])
    expected = np.array([0, 1, 2, 3])
    new_y = unify_vector(y)
    assert np.all(new_y == expected)


def test_unify_fails_on_missing():
    orig_data = np.array([[1, 2], [3, np.nan]])
    orig_labels = np.array([0, 1])

    with pytest.raises(ValueError):
        unify_data(orig_data, orig_labels)


def test_unify_dataframe_smoke():
    df = pd.DataFrame()
    df["f1"] = [1.5, "a"]
    df["f2"] = [3, "b"]
    df["label"] = [0, 1]

    train_cols = df.columns[0:-1]
    label = df.columns[-1]
    X = df[train_cols]
    y = df[label]

    unify_data(X, y)


def test_unify_list_data():
    orig_data = [[1, 2], [3, 4]]
    orig_labels = [0, 0]

    data, labels, feature_names, feature_types = unify_data(orig_data, orig_labels)
    assert feature_names is not None
    assert feature_types is not None
    assert isinstance(data, np.ndarray)
    assert data.ndim == 2
    assert isinstance(labels, np.ndarray)
    assert labels.ndim == 1


def test_that_names_generated():
    class SomeClass:
        pass

    some_class = SomeClass()

    name = gen_name_from_class(some_class)
    assert name == "SomeClass_0"


def test_that_feat_val_generated(fixture_feat_val_list):
    features = ["age", "race", "gender"]
    values = [-2, 3, 1]

    feat_val_list = gen_feat_val_list(features, values)
    assert feat_val_list == fixture_feat_val_list


def test_reverse_map():
    map = {"a": 1, "b": 2, "c": 3}
    actual_rev_map = reverse_map(map)
    expected_rev_map = {1: "a", 2: "b", 3: "c"}

    assert actual_rev_map == expected_rev_map


def test_gen_perf_dicts_regression():
    y = np.array([0, 0.5])
    scores = np.array([0.9, 0.1])
    expected_predicted = np.array([0.9, 0.1])
    expected_actual_score = np.array([0, 0.5])
    expected_predicted_score = np.array([0.9, 0.1])

    records = gen_perf_dicts(scores, y, False)
    for i, di in enumerate(records):
        assert di["actual"] == y[i]
        assert di["predicted"] == expected_predicted[i]
        assert di["actual_score"] == expected_actual_score[i]
        assert di["predicted_score"] == expected_predicted_score[i]


def test_gen_perf_dicts_classification():
    y = np.array([0, 2])
    scores = np.array([[0.9, 0.06, 0.04], [0.1, 0.5, 0.4],])
    expected_predicted = np.array([0, 1])
    expected_actual_score = np.array([0.9, 0.4])
    expected_predicted_score = np.array([0.9, 0.5])

    records = gen_perf_dicts(scores, y, True)
    for i, di in enumerate(records):
        assert di["actual"] == y[i]
        assert di["predicted"] == expected_predicted[i]
        assert di["actual_score"] == expected_actual_score[i]
        assert di["predicted_score"] == expected_predicted_score[i]