from unittest.mock import patch, PropertyMock

import pytest


def test_foreshadow_defaults():
    from ..foreshadow import Foreshadow
    from ..preprocessor import Preprocessor
    from ..estimators.auto_estimator import AutoEstimator

    foreshadow = Foreshadow()
    # defaults
    assert (
        isinstance(foreshadow.X_preprocessor, Preprocessor)
        and isinstance(foreshadow.y_preprocessor, Preprocessor)
        and isinstance(foreshadow.estimator, AutoEstimator)
        and foreshadow.optimizer is None
        and foreshadow.target is None
        and foreshadow.pipeline is None
        and foreshadow.data_columns is None
    )


def test_foreshadow_X_preprocessor_false():
    from ..foreshadow import Foreshadow

    foreshadow = Foreshadow(X_preprocessor=False)
    assert foreshadow.X_preprocessor is None


def test_foreshadow_X_preprocessor_custom():
    from ..foreshadow import Foreshadow
    from ..preprocessor import Preprocessor

    preprocessor = Preprocessor()
    foreshadow = Foreshadow(X_preprocessor=preprocessor)
    assert isinstance(foreshadow.X_preprocessor, Preprocessor)


def test_foreshadow_X_preprocessor_error():
    from ..foreshadow import Foreshadow

    preprocessor = "Invalid"
    with pytest.raises(ValueError) as e:
        foreshadow = Foreshadow(X_preprocessor=preprocessor)

    assert str(e.value) == "Invalid value passed as X_preprocessor"


def test_foreshadow_y_preprocessor_false():
    from ..foreshadow import Foreshadow

    foreshadow = Foreshadow(y_preprocessor=False)
    assert foreshadow.y_preprocessor is None


def test_foreshadow_y_preprocessor_custom():
    from ..foreshadow import Foreshadow
    from ..preprocessor import Preprocessor

    preprocessor = Preprocessor()
    foreshadow = Foreshadow(y_preprocessor=preprocessor)
    assert isinstance(foreshadow.y_preprocessor, Preprocessor)


def test_foreshadow_y_preprocessor_error():
    from ..foreshadow import Foreshadow

    preprocessor = "Invalid"
    with pytest.raises(ValueError) as e:
        foreshadow = Foreshadow(y_preprocessor=preprocessor)

    assert str(e.value) == "Invalid value passed as y_preprocessor"


def test_foreshadow_estimator_custom():
    from ..foreshadow import Foreshadow
    from sklearn.base import BaseEstimator

    estimator = BaseEstimator()
    foreshadow = Foreshadow(estimator=estimator)
    assert isinstance(foreshadow.estimator, BaseEstimator)


def test_foreshadow_estimator_error():
    from ..foreshadow import Foreshadow

    estimator = "Invalid"
    with pytest.raises(ValueError) as e:
        foreshadow = Foreshadow(estimator=estimator)

    assert str(e.value) == "Invalid value passed as estimator"


def test_foreshadow_optimizer_custom():
    from ..foreshadow import Foreshadow
    from sklearn.model_selection._search import BaseSearchCV
    from sklearn.base import BaseEstimator

    class DummySearch(BaseSearchCV):
        def __init__(self):
            pass

    # Need custom estimator to avoid warning
    estimator = BaseEstimator()
    optimizer = DummySearch()
    foreshadow = Foreshadow(estimator=estimator, optimizer=optimizer)
    assert isinstance(foreshadow.optimizer, BaseSearchCV)


def test_foreshadow_optimizer_error():
    from ..foreshadow import Foreshadow

    optimizer = "Invalid"
    with pytest.raises(ValueError) as e:
        foreshadow = Foreshadow(optimizer=optimizer)

    assert str(e.value) == "Invalid value passed as optimizer"


def test_foreshadow_warns_on_set_estimator_optimizer():
    from ..foreshadow import Foreshadow
    from sklearn.model_selection._search import BaseSearchCV

    class DummySearch(BaseSearchCV):
        def __init__(self):
            pass

    optimizer = DummySearch()
    with pytest.warns(Warning) as w:
        foreshadow = Foreshadow(optimizer=optimizer)

    assert str(w[0].message) == (
        "An automatic estimator cannot be used with an"
        " optimizer. Proceeding without use of optimizer"
    )


# patch to override type verification
@patch(
    "foreshadow.foreshadow.Foreshadow.X_preprocessor",
    create=True,
    new_callable=PropertyMock,
)
def test_foreshadow_custom_fit_estimate(X_preprocessor):
    import numpy as np
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.model_selection import train_test_split
    from ..foreshadow import Foreshadow

    np.random.seed(0)

    X_pipeline = Pipeline([("xohe", OneHotEncoder())])
    setattr(X_pipeline, "pipeline", X_pipeline)
    estimator = LogisticRegression()

    X = np.array([0] * 50 + [1] * 50).reshape((-1, 1))
    y = np.array([0] * 50 + [1] * 50)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    # Let foreshadow set to defaults, we will overwrite them
    foreshadow = Foreshadow(y_preprocessor=False, estimator=estimator)
    X_preprocessor.return_value = X_pipeline
    foreshadow.fit(X_train, y_train)
    foreshadow_predict = foreshadow.predict(X_test)
    foreshadow_predict_proba = foreshadow.predict_proba(X_test)
    foreshadow_score = foreshadow.score(X_test, y_test)
    expected_predict = np.array([0, 1, 0, 1, 1, 1, 0, 1, 1, 1])
    expected_predict_proba = np.array(
        [
            [0.9414791454949417, 0.05852085450505827],
            [0.06331066362121573, 0.9366893363787843],
            [0.9414791454949417, 0.05852085450505827],
            [0.06331066362121573, 0.9366893363787843],
            [0.06331066362121573, 0.9366893363787843],
            [0.06331066362121573, 0.9366893363787843],
            [0.9414791454949417, 0.05852085450505827],
            [0.06331066362121573, 0.9366893363787843],
            [0.06331066362121573, 0.9366893363787843],
            [0.06331066362121573, 0.9366893363787843],
        ]
    )
    expected_score = 1.0

    assert np.allclose(foreshadow_predict, expected_predict)
    assert np.allclose(foreshadow_predict_proba, expected_predict_proba)
    assert np.allclose(foreshadow_score, expected_score)


@patch(
    "foreshadow.foreshadow.Foreshadow.y_preprocessor",
    create=True,
    new_callable=PropertyMock,
)
def test_foreshadow_y_preprocessor(y_preprocessor):
    import numpy as np
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from ..foreshadow import Foreshadow

    np.random.seed(0)

    y_pipeline = Pipeline([("yohe", StandardScaler())])
    setattr(y_pipeline, "pipeline", y_pipeline)
    estimator = LinearRegression()

    X = np.array([0] * 50 + [1] * 50).reshape((-1, 1))
    y = np.random.normal(100, 10, 100).reshape((-1, 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    # Let foreshadow set to defaults, we will overwrite them
    foreshadow = Foreshadow(X_preprocessor=False, estimator=estimator)
    y_preprocessor.return_value = y_pipeline
    foreshadow.fit(X_train, y_train)
    foreshadow_predict = foreshadow.predict(X_test)
    foreshadow_score = foreshadow.score(X_test, y_test)
    expected_predict = np.array(
        [
            [102.19044770619593],
            [102.19044770619593],
            [102.19044770619593],
            [100.05275170774354],
            [102.19044770619593],
            [102.19044770619593],
            [102.19044770619593],
            [102.19044770619593],
            [100.05275170774354],
            [100.05275170774354],
        ]
    )
    expected_score = -0.3576910440975052

    assert np.allclose(foreshadow_predict, expected_predict)
    assert np.allclose(foreshadow_score, expected_score)


def test_foreshadow_without_x_processor():
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from ..foreshadow import Foreshadow

    np.random.seed(0)
    estimator = LinearRegression()
    X = np.arange(200).reshape((-1, 1))
    y = np.random.normal(0, 1, 200).reshape((-1, 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    foreshadow = Foreshadow(
        X_preprocessor=False, y_preprocessor=False, estimator=estimator
    )
    foreshadow.fit(X_train, y_train)
    foreshadow_predict = foreshadow.predict(X_test)
    expected_predict = np.array(
        [
            [0.21789584803659176],
            [-0.11658780412675052],
            [-0.008315639264628194],
            [-0.04698426957252905],
            [0.229496437128962],
            [0.09608966256670409],
            [-0.07791917381884972],
            [0.21402898500580167],
            [0.20629525894422152],
            [-0.023783091387788502],
            [0.06902162135117351],
            [0.10769025165907437],
            [0.0825556419589388],
            [0.16569319712092562],
            [-0.11852123564214556],
            [-0.11078750958056544],
            [0.028419559527877614],
            [-0.01604936532620832],
            [0.03035299104327266],
            [0.09222279953591403],
        ]
    )

    assert np.allclose(foreshadow_predict, expected_predict)


def test_foreshadow_predict_before_fit():
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from ..foreshadow import Foreshadow

    np.random.seed(0)
    estimator = LinearRegression()
    X = np.arange(200).reshape((-1, 2))
    y = np.random.normal(0, 1, 100).reshape((-1, 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    foreshadow = Foreshadow(
        X_preprocessor=False, y_preprocessor=False, estimator=estimator
    )

    with pytest.raises(ValueError) as e:
        foreshadow_predict = foreshadow.predict(X_test)

    assert str(e.value) == "Foreshadow has not been fit yet"


def test_foreshadow_predict_diff_cols():
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from ..foreshadow import Foreshadow

    np.random.seed(0)
    estimator = LinearRegression()
    X = np.arange(200).reshape((-1, 2))
    y = np.random.normal(0, 1, 100).reshape((-1, 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    foreshadow = Foreshadow(
        X_preprocessor=False, y_preprocessor=False, estimator=estimator
    )
    foreshadow.fit(X_train, y_train)

    with pytest.raises(ValueError) as e:
        foreshadow_predict = foreshadow.predict(X_test[:, :-1])

    assert str(e.value) == "Predict must have the same columns as train columns"