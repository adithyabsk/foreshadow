import pytest


def test_metaestimator_predict():
    import numpy as np

    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    from foreshadow.estimators import MetaEstimator

    np.random.seed(0)

    me = MetaEstimator(LinearRegression(), StandardScaler())
    X = np.arange(200).reshape((-1, 1))
    y = np.random.normal(100, 10, 200).reshape((-1, 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    me.fit(X_train, y_train)

    # comapre
    scaler = StandardScaler().fit(y_train)
    est = LinearRegression().fit(X_train, scaler.transform(y_train))
    assert np.allclose(
        me.predict(X_test), scaler.inverse_transform(est.predict(X_test))
    )


def test_metaestimator_predict_proba():
    import numpy as np

    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    from foreshadow.estimators import MetaEstimator

    np.random.seed(0)

    me = MetaEstimator(LogisticRegression(), LabelEncoder())
    X = np.arange(100).reshape((-1, 1))
    y = np.array(["A"] * 50 + ["B"] * 50)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    me.fit(X_train, y_train)

    # comapre
    scaler = LabelEncoder().fit(y_train)
    est = LogisticRegression().fit(X_train, scaler.transform(y_train))
    assert np.allclose(me.predict_proba(X_test), est.predict_proba(X_test))


def test_metaestimator_score():
    import numpy as np

    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    from foreshadow.estimators import MetaEstimator

    np.random.seed(0)

    me = MetaEstimator(LogisticRegression(), LabelEncoder())
    X = np.arange(100).reshape((-1, 1))
    y = np.array(["A"] * 50 + ["B"] * 50)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    me.fit(X_train, y_train)

    # comapre
    scaler = LabelEncoder().fit(y_train)
    est = LogisticRegression().fit(X_train, scaler.transform(y_train))
    assert np.allclose(
        me.score(X_test, y_test), est.score(X_test, scaler.transform(y_test))
    )
