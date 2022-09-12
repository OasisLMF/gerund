from unittest import main, TestCase
from gerund.components.local_variable_storage import LocalVariableStorage, Singleton


class TestLocalVariableStorage(TestCase):

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        Singleton._instances = {}

    def test___init__(self):
        test = LocalVariableStorage()
        test_two = LocalVariableStorage()

        self.assertEqual(id(test), id(test_two))


if __name__ == "__main__":
    main()
