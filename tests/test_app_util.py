import httplib

import mock
from rhsm import certificate, certificate2
import unittest2 as unittest

from crane import app_util
from crane import exceptions
from crane.data import V1Repo, V2Repo, V3Repo
import demo_data

from views import base


@app_util.authorize_repo_id
def mock_repo_func(repo_id):
    return 'foo'


@app_util.authorize_image_id
def mock_image_func(image_id, repo_info):
    return 'foo'


@app_util.authorize_name
def mock_name_func(repo_id):
    return 'foo'


class FlaskContextBase(base.BaseCraneAPITest):

    def setUp(self):
        super(FlaskContextBase, self).setUp()
        self.ctx = self.app.test_request_context('/')
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
        super(FlaskContextBase, self).tearDown()


class TestAuthorizeRepoId(FlaskContextBase):

    def test_raises_not_found_if_repo_id_none(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_repo_func(None)
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    def test_raises_not_found_if_repo_id_invalid(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_repo_func('bad_id')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_raises_not_found_if_id_invalid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_repo_func('qux')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_passes_if_auth_valid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        result = mock_repo_func('baz')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_bypass_if_not_protected(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        result = mock_repo_func('redhat/foo')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_auth_fails_if_no_path_matches_credentials(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_repo_func('qux')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)


class TestAuthorizeName(FlaskContextBase):

    def test_raises_not_found_if_repo_id_none(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func(None)
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    def test_raises_not_found_if_repo_id_invalid(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func('bad_id')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_raises_not_found_if_id_invalid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func('qux')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_passes_if_auth_valid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert

        result = mock_name_func('v2/bar')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_if_protected(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        cert.check_path = mock.Mock(return_value=True)
        mock_get_cert.return_value = cert
        result = mock_name_func('protected')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_if_protected_but_invalid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func('protected')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    def test_if_protected_but_no_cert(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func('protected')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_bypass_if_not_protected(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        result = mock_name_func('v2/bar')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_auth_fails_if_no_path_matches_credentials(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_name_func('bar1')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)


class TestAuthorizeImageId(FlaskContextBase):

    def test_raises_not_found_if_image_id_none(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_image_func(None)
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    def test_raises_not_found_if_image_id_invalid(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_image_func('invalid')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_raises_auth_error_if_id_invalid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_image_func('qux')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    @mock.patch('crane.app_util._get_certificate')
    def test_passes_if_auth_valid(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        result = mock_image_func('baz123')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_bypass_if_not_protected(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert
        result = mock_image_func('xyz789')
        self.assertEquals(result, 'foo')

    @mock.patch('crane.app_util._get_certificate')
    def test_not_authorized(self, mock_get_cert):
        cert = certificate.create_from_file(demo_data.demo_entitlement_cert_path)
        mock_get_cert.return_value = cert

        with self.assertRaises(exceptions.HTTPError) as assertion:
            mock_image_func('qux123')
        self.assertEquals(assertion.exception.status_code, httplib.NOT_FOUND)


class TestHandler(unittest.TestCase):

    def test_default_message(self):
        string_value, http_code = app_util.http_error_handler(
            exceptions.HTTPError(httplib.NOT_FOUND))
        self.assertEquals(string_value, httplib.responses[httplib.NOT_FOUND])
        self.assertEquals(http_code, httplib.NOT_FOUND)

    def test_custom_message(self):
        string_value, http_code = app_util.http_error_handler(
            exceptions.HTTPError(httplib.BAD_GATEWAY, 'Foo Error'))
        self.assertEquals(string_value, 'Foo Error')
        self.assertEquals(http_code, httplib.BAD_GATEWAY)


class TestGetCertificate(FlaskContextBase):

    def test_empty_cert(self):
        cert = app_util._get_certificate()
        self.assertEquals(cert, None)

    def test_non_entitlement_cert(self):
        with open(demo_data.demo_no_entitlement_cert_path) as test_cert:
            data = test_cert.read()
        self.ctx.request.environ['SSL_CLIENT_CERT'] = data
        cert = app_util._get_certificate()
        self.assertEquals(cert, None)

    def test_valid_cert(self):
        with open(demo_data.demo_entitlement_cert_path) as test_cert:
            data = test_cert.read()
        self.ctx.request.environ['SSL_CLIENT_CERT'] = data
        cert = app_util._get_certificate()
        self.assertTrue(isinstance(cert, certificate2.EntitlementCertificate))


class TestValidateAndTransformRepoID(unittest.TestCase):
    def test_more_than_one_slash(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            app_util.validate_and_transform_repoid('a/b/c')
        self.assertEqual(assertion.exception.status_code, httplib.NOT_FOUND)

    def test_library_namespace(self):
        ret = app_util.validate_and_transform_repoid('library/centos')

        self.assertEqual(ret, 'centos')

    def test_normal(self):
        ret = app_util.validate_and_transform_repoid('foo/bar')

        self.assertEqual(ret, 'foo/bar')


class TestValidateAndTransformRepoName(unittest.TestCase):

    def test_normal(self):
        name, path, component = app_util.validate_and_transform_repo_name('redhat/rhel7.0/tags/latest') # noqa
        self.assertEqual(name, 'redhat/rhel7.0')
        self.assertEqual(path, 'tags/latest')
        self.assertEqual(component, 'tags')

    def test_funny_image_names(self):
        for image_name in ['tags', 'manifests', 'blobs']:
            for component_type in ['tags', 'manifests', 'blobs']:
                full_path = 'redhat/%s/%s/latest' % (image_name, component_type)
                name, path, component = app_util.validate_and_transform_repo_name(full_path)
                msg = 'Full path: ' + full_path
                self.assertEqual(name, 'redhat/' + image_name, msg=msg)
                self.assertEqual(path, component_type + '/latest', msg=msg)
                self.assertEqual(component, component_type, msg=msg)

    def test_boundary_conditions(self):
        """Ensure that no exception happens in boundary cases"""
        components = app_util.validate_and_transform_repo_name('tags')
        self.assertEqual(components, ('', 'tags', 'tags'))
        components = app_util.validate_and_transform_repo_name('tags/')
        self.assertEqual(components, ('', 'tags/', 'tags'))
        components = app_util.validate_and_transform_repo_name('/tags')
        self.assertEqual(components, ('', 'tags', 'tags'))

    def test_path_without_tags_or_manifest_or_blobs(self):
        with self.assertRaises(exceptions.HTTPError) as assertion:
            app_util.validate_and_transform_repo_name('redhat/rhel7.0/unknown/latest')
        self.assertEquals(assertion.exception.status_code, httplib.NOT_FOUND)


class TestValidateGetRepositories(unittest.TestCase):

    @mock.patch('crane.app_util.get_data')
    def test_get_repositories(self, mock_get_data):
        repo = V1Repo(url="",
                      repository="test-repo",
                      images_json="[{\"id\": \"test-image1\"}, {\"id\": \"test-image2\"}]",
                      tags_json="{\"tag1\": \"test-image1\"}",
                      url_path="",
                      protected=False)
        mock_get_data.return_value = {'repos': {"test-repo": repo}}
        ret = app_util.get_repositories()
        self.assertEqual(ret['test-repo']['image_ids'], ['test-image1', 'test-image2'])
        self.assertEqual(ret['test-repo']['tags'], {'tag1': 'test-image1'})
        self.assertEqual(ret['test-repo']['protected'], False)

    @mock.patch('crane.app_util.get_data')
    def test_get_repositories_empty(self, mock_get_data):
        mock_get_data.return_value = {'repos': {}}
        ret = app_util.get_repositories()
        self.assertEqual(ret, {})


class TestValidateGetV2Repositories(unittest.TestCase):

    @mock.patch('crane.app_util.get_v2_data')
    def test_get_v2_repositories(self, mock_get_v2_data):
        repo = V2Repo(url="", repository="", url_path="", protected=True)
        repo2 = V3Repo(url="", repository="", url_path="", schema2_data=[], protected=False)
        mock_get_v2_data.return_value = {'repos': {'test-repo': repo, 'test-repo2': repo2}}
        ret = app_util.get_v2_repositories()
        self.assertEqual(ret['test-repo']['protected'], True)
        self.assertEqual(ret['test-repo2']['protected'], False)

    @mock.patch('crane.app_util.get_v2_data')
    def test_get_v2_repositories_empty(self, mock_get_v2_data):
        mock_get_v2_data.return_value = {'repos': {}}
        ret = app_util.get_v2_repositories()
        self.assertEqual(ret, {})


class TestGenerateCDNToken(unittest.TestCase):

    def test_generate_cdn_url_token(self):
        path = '/content/repo/manifests/123'
        secret = 'abc123'
        exp = 1933027200
        algo = 'sha256'
        expected_hmac = 'd039ac10e019fd13824a3f861b4f55df40e2a402d102b5266194fff6f3a24ed0'
        token = app_util.generate_cdn_url_token(path, secret, exp, algo)
        self.assertIn('exp=%s' % exp, token)
        self.assertIn('hmac=%s' % expected_hmac, token)
