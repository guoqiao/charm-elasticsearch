"""Unit tests for the elasticsearch charm.

These are near-worthless unit-tests, simply testing the behaviour
of the hooks.py module, as it is extremely difficult to unit-test anything
that calls into charmhelpers in a stateful way (as charmhelpers is always
writing to system directories), without setting up environments.

For this reason, rely on the functional tests of the charm instead (tests
directory)
"""
import unittest

try:
    import mock
except ImportError:
    raise ImportError(
        "Please ensure both python-mock and python-nose are installed.")


from hooks import hooks
from charmhelpers.core.hookenv import Config


class HooksTestCase(unittest.TestCase):

    def setUp(self):
        super(HooksTestCase, self).setUp()

        # charmhelpers is getting difficult to test against, as it writes
        # to system directories even for things that should be idempotent,
        # like accessing config options.
        patcher = mock.patch('charmhelpers.core.hookenv.charm_dir')
        self.mock_charm_dir = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_charm_dir.return_value = '/tmp/foo'

        patcher = mock.patch('charmhelpers.core.hookenv.config')
        self.mock_config = patcher.start()
        self.addCleanup(patcher.stop)
        config = Config({
            'install_deps_from_ppa': False,
        })
        config.implicit_save = False
        self.mock_config.return_value = config

        patcher = mock.patch('charmhelpers.payload.execd.execd_preinstall')
        self.mock_preinstall = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch('charmhelpers.contrib.ansible')
        self.mock_ansible = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch('charmhelpers.core.host.rsync')
        self.mock_rsync = patcher.start()
        self.addCleanup(patcher.stop)

    def test_installs_ansible_support(self):
        hooks.execute(['install'])

        ansible = self.mock_ansible
        ansible.install_ansible_support.assert_called_once_with(
            from_ppa=False)

    def test_applies_install_playbook(self):
        hooks.execute(['install'])

        self.assertEqual([
            mock.call('playbook.yaml', tags=['install']),
        ], self.mock_ansible.apply_playbook.call_args_list)

    def test_executes_preinstall(self):
        hooks.execute(['install'])

        self.mock_preinstall.assert_called_once_with()

    def test_copys_backported_ansible_modules(self):
        hooks.execute(['install'])

        self.mock_rsync.assert_called_once_with(
            'ansible_module_backports',
            '/usr/share/ansible')

    def test_default_hooks(self):
        """Most of the hooks let ansible do all the work."""
        default_hooks = [
            'config-changed',
            'cluster-relation-joined',
            'peer-relation-joined',
            'peer-relation-departed',
            'nrpe-external-master-relation-changed',
            'rest-relation-joined',
            'start',
            'stop',
            'upgrade-charm',
            'client-relation-joined',
            'client-relation-departed',
        ]
        mock_apply_playbook = self.mock_ansible.apply_playbook

        for hook in default_hooks:
            mock_apply_playbook.reset_mock()

            hooks.execute([hook])

            self.assertEqual([
                mock.call('playbook.yaml',
                          tags=[hook]),
            ], mock_apply_playbook.call_args_list)


if __name__ == '__main__':
    unittest.main()
