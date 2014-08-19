"""Unit tests for the elasticsearch charm."""
import unittest

try:
    import mock
except ImportError:
    raise ImportError(
        "Please ensure both python-mock and python-nose are installed.")


from hooks import hooks


class InstallHookTestCase(unittest.TestCase):

    def setUp(self):
        super(InstallHookTestCase, self).setUp()

        patcher = mock.patch('hooks.charmhelpers')
        self.mock_charmhelpers = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch('charmhelpers.contrib.ansible.apply_playbook')
        self.mock_apply_playbook = patcher.start()
        self.addCleanup(patcher.stop)

    def test_installs_ansible_support(self):
        hooks.execute(['install'])

        ansible = self.mock_charmhelpers.contrib.ansible
        ansible.install_ansible_support.assert_called_once_with(
            from_ppa=False)

    def test_applies_install_playbook(self):
        hooks.execute(['install'])

        self.assertEqual([
            mock.call('playbook.yaml', tags=['install']),
        ], self.mock_apply_playbook.call_args_list)

    def test_executes_preinstall(self):
        hooks.execute(['install'])

        execd = self.mock_charmhelpers.payload.execd
        execd.execd_preinstall.assert_called_once_with()

    def test_copys_backported_ansible_modules(self):
        hooks.execute(['install'])

        rsync = self.mock_charmhelpers.core.host.rsync
        rsync.assert_called_once_with(
            'ansible_module_backports',
            '/usr/share/ansible')


class DefaultHooksTestCase(unittest.TestCase):

    def setUp(self):
        super(DefaultHooksTestCase, self).setUp()
        patcher = mock.patch('charmhelpers.contrib.ansible.apply_playbook')
        self.mock_apply_playbook = patcher.start()
        self.addCleanup(patcher.stop)

    def test_default_hooks(self):
        """Most of the hooks let ansible do all the work."""
        default_hooks = [
            'config-changed',
            'peer-relation-joined',
            'start',
            'stop',
        ]
        for hook in default_hooks:
            self.mock_apply_playbook.reset_mock()

            hooks.execute([hook])

            self.assertEqual([
                mock.call('playbook.yaml',
                          tags=[hook]),
            ], self.mock_apply_playbook.call_args_list)
