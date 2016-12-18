import uuid
import random
import unittest


from compage import service, exception


class InjectionDonor(object):
    def __init__(self, foo):
        super(InjectionDonor, self).__init__()
        self._foo = foo

    @property
    def foo(self):
        return self._foo


class InjectionReceiver(object):
    def __init__(self, injection):
        self._injection = injection

    @property
    def injection(self):
        return self._injection


def unique_token():
    return uuid.uuid4().hex


class TestDependencyManager(unittest.TestCase):
    def setUp(self):
        self.mgr = service.ServiceManager
        self.token_01 = unique_token()
        self.token_02 = unique_token()
        self.tokens = [unique_token() for x in range(100)]

    def tearDown(self):
        self.mgr.remove_all()

    def test_add_and_get(self):
        code_object = InjectionDonor(self.token_01)
        self.mgr.add(self.token_01, code_object)
        service = self.mgr.get(self.token_01)
        self.assertEqual(service.foo, self.token_01)

    def test_add_and_get_func(self):
        for token in self.tokens:
            self.mgr.add(token, lambda token: token, execute=False)
        randint = random.randint(0, len(self.tokens) - 1)
        random_token = self.tokens[randint]
        self.assertEqual(
            self.mgr.get(random_token)(random_token), random_token)

    def test_remove_all(self):
        self.mgr.remove_all()
        self.assertEqual(self.mgr.count, 0)

    def test_remove_service(self):
        self.mgr.add(self.token_01, lambda: True)
        self.mgr.remove(self.token_01)
        self.assertFalse(self.mgr.exists(self.token_01))

    def test_exists(self):
        self.mgr.add(self.token_01, self.token_01)
        self.assertTrue(self.mgr.exists(self.token_01))

    def test_tokens(self):
        for token in self.tokens:
            self.mgr.add(token, token)
        self.assertEqual(self.mgr.tokens, self.tokens)

    def test_count(self):
        randInt = random.randint(1, 20)
        for i in range(randInt):
            self.mgr.add(unique_token(), lambda: True)
        self.assertEqual(self.mgr.count, randInt)

    def test_singleton_behaviour(self):
        another_mgr = service.ServiceManager
        self.assertEqual(another_mgr.id, self.mgr.id)

    def test_no_service_exception(self):
        with self.assertRaises(exception.NoServiceError):
            self.mgr.get(self.token_01)

    def test_service_not_found_exception(self):
        self.mgr.add(self.token_01, lambda: True)
        with self.assertRaises(exception.ServiceNotFoundError):
            self.mgr.get(self.token_02)

    def test_invalid_token_error(self):
        with self.assertRaises(exception.InvalidTokenError):
            self.mgr.add(0, lambda: True)

    def test_no_duplicate_service(self):
        self.mgr.add(self.token_01, lambda: True)

        with self.assertRaises(exception.ServiceAlreadyExistsError):
            self.mgr.add(self.token_01, lambda: True)

    def test_force_update_service(self):
        self.mgr.add(self.token_01, self.token_01)
        self.mgr.add(self.token_01, self.token_02, force=True)
        self.assertEquals(self.mgr.get(self.token_01), self.token_02)


if __name__ == '__main__':
    unittest.main()
