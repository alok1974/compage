import uuid
import random
import unittest


from compage.services import ServiceManager, exception


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


# Generates a new unique token on each call
def getNewUniqueToken():
    return uuid.uuid4().hex


class TestDependencyManager(unittest.TestCase):
    def setUp(self):
        self.mgr = ServiceManager
        self.token01 = getNewUniqueToken()
        self.token02 = getNewUniqueToken()
        self.tokens = [getNewUniqueToken() for x in range(100)]

    def tearDown(self):
        self.mgr.removeAll()

    def testAddAndGet(self):
        codeObject = InjectionDonor(self.token01)
        self.mgr.add(self.token01, codeObject)
        service = self.mgr.get(self.token01)
        self.assertEqual(service.foo, self.token01)

    def testAddAndGetFunc(self):
        for token in self.tokens:
            self.mgr.add(token, lambda token: token, execute=False)
        randint = random.randint(0, len(self.tokens) - 1)
        randomToken = self.tokens[randint]
        self.assertEqual(self.mgr.get(randomToken)(randomToken), randomToken)

    def testRemoveAll(self):
        self.mgr.removeAll()
        self.assertEqual(self.mgr.count, 0)

    def testRemoveService(self):
        self.mgr.add(self.token01, lambda: True)
        self.mgr.remove(self.token01)
        self.assertFalse(self.mgr.exists(self.token01))

    def testExists(self):
        self.mgr.add(self.token01, self.token01)
        self.assertTrue(self.mgr.exists(self.token01))

    def testTokens(self):
        for token in self.tokens:
            self.mgr.add(token, token)
        self.assertEqual(self.mgr.tokens, self.tokens)

    def testCount(self):
        randInt = random.randint(1, 20)
        for i in range(randInt):
            self.mgr.add(getNewUniqueToken(), lambda: True)
        self.assertEqual(self.mgr.count, randInt)

    def testSingletonBehaviour(self):
        from compage.services import ServiceManager as mgr02

        self.assertEqual(mgr02.id, self.mgr.id)

    def testNoServiceException(self):
        with self.assertRaises(exception.NoServiceError):
            self.mgr.get(self.token01)

    def testServiceNotFoundException(self):
        self.mgr.add(self.token01, lambda: True)
        with self.assertRaises(exception.ServiceNotFoundError):
            self.mgr.get(self.token02)

    def testInvalidTokenError(self):
        with self.assertRaises(exception.InvalidTokenError):
            self.mgr.add(0, lambda: True)

    def testNoDuplicateService(self):
        self.mgr.add(self.token01, lambda: True)

        with self.assertRaises(exception.ServiceAlreadyExistsError):
            self.mgr.add(self.token01, lambda: True)

    def testForceUpdateService(self):
        self.mgr.add(self.token01, self.token01)
        self.mgr.add(self.token01, self.token02, force=True)
        self.assertEquals(self.mgr.get(self.token01), self.token02)


if __name__ == '__main__':
    unittest.main()
