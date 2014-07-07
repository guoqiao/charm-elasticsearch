#!/usr/bin/env python
"""Setup hooks for the elasticsearch charm."""

import sys
import charmhelpers.contrib.ansible
import charmhelpers.payload.execd


hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path='playbook.yaml',
    default_hooks=[
        'config-changed',
        'cluster-relation-joined',
        'peer-relation-joined',
        'nrpe-external-master-relation-changed',
        'rest-relation-joined',
        'start',
        'stop',
        'upgrade-charm',
        'client-relation-changed',
        'client-relation-joined',
    ])


@hooks.hook('install', 'upgrade-charm')
def install():
    """Install ansible before running the tasks tagged with 'install'."""
    # Allow charm users to run preinstall setup.
    charmhelpers.payload.execd.execd_preinstall()
    charmhelpers.contrib.ansible.install_ansible_support(
        from_ppa=False)


if __name__ == "__main__":
    hooks.execute(sys.argv)
