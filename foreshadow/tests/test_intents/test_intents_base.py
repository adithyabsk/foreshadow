import pytest


def test_instantiate_base():
    from foreshadow.intents.base import BaseIntent

    with pytest.raises(TypeError) as e:
        b = BaseIntent()
    assert str(e.value) == "BaseIntent may not be instantiated"


def test_mock_subclass_missing_dtype():
    from foreshadow.intents.base import BaseIntent

    with pytest.raises(NotImplementedError) as e:

        class TestIntent(BaseIntent):
            pass

    assert str(e.value) == (
        "Subclass must define cls.dtype attribute.\nThis attribute should define the "
        "dtype of the intent."
    )


def test_mock_subclass_missing_children():
    from foreshadow.intents.base import BaseIntent

    with pytest.raises(NotImplementedError) as e:

        class TestIntent(BaseIntent):
            dtype = "TEST"

    assert str(e.value) == (
        "Subclass must define cls.children attribute.\nThis attribute should define the"
        " children of the intent."
    )


def test_valid_mock_subclass():
    from foreshadow.intents.registry import _unregister_intent
    from foreshadow.intents.base import BaseIntent

    class TestIntent(BaseIntent):
        dtype = "TEST"
        children = []

        def __init__(self):
            pass

    t = TestIntent()
    _unregister_intent(TestIntent.__name__)


def test_to_string():
    from foreshadow.intents.registry import _unregister_intent
    from foreshadow.intents.base import BaseIntent

    class TestIntent(BaseIntent):
        dtype = "TEST"
        children = ["TestIntent1", "TestIntent2"]

    class TestIntent1(TestIntent):
        dtype = "TEST"
        children = ["TestIntent11", "TestIntent12"]

    class TestIntent2(TestIntent):
        dtype = "TEST"
        children = []

    class TestIntent11(TestIntent1):
        dtype = "TEST"
        children = []

    class TestIntent12(TestIntent1):
        dtype = "TEST"
        children = []

    class_list = [
        "TestIntent",
        "TestIntent1",
        "TestIntent2",
        "TestIntent11",
        "TestIntent12",
    ]
    assert TestIntent.to_string() == (
        "TestIntent\n\tTestIntent1\n\t\tTestIntent11\n\t\tTestIntent12\n\t"
        "TestIntent2\n"
    )
    _unregister_intent(class_list)


def test_priority_traverse():
    from foreshadow.intents.registry import _unregister_intent
    from foreshadow.intents.base import BaseIntent

    class TestIntent(BaseIntent):
        dtype = "TEST"
        children = ["TestIntent1", "TestIntent2"]

    class TestIntent1(TestIntent):
        dtype = "TEST"
        children = ["TestIntent11", "TestIntent12"]

    class TestIntent2(TestIntent):
        dtype = "TEST"
        children = []

    class TestIntent11(TestIntent1):
        dtype = "TEST"
        children = []

    class TestIntent12(TestIntent1):
        dtype = "TEST"
        children = []

    class_list = [TestIntent, TestIntent2, TestIntent1, TestIntent12, TestIntent11]
    assert class_list == list(TestIntent.priority_traverse())
    _unregister_intent(list(map(lambda x: x.__name__, class_list)))


def test_is_intent_implementation():
    import pandas as pd

    from foreshadow.intents.registry import _unregister_intent
    from foreshadow.intents.base import BaseIntent

    X_df = pd.DataFrame([[1]], columns=["A"])

    class TestIntent(BaseIntent):
        dtype = "TEST"
        children = ["TestIntent1", "TestIntent2"]

    with pytest.raises(NotImplementedError) as e:
        TestIntent.is_intent(X_df)

    assert str(e.value) == "is_fit is not immplemented"
    _unregister_intent(TestIntent.__name__)
