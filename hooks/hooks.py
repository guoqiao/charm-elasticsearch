#!/usr/bin/env python3
"""Setup hooks for the elasticsearch charm."""

import sys
import charmhelpers.contrib.ansible
import charmhelpers.payload.execd
import charmhelpers.core.host
from charmhelpers.core import hookenv
import os
import shutil

mountpoint = '/srv/elasticsearch'

hooks = charmhelpers.contrib.ansible.AnsibleHooks(
    playbook_path='playbook.yaml',
    default_hooks=[
        'config-changed',
        'cluster-relation-joined',
        'logs-relation-joined',
        'data-relation-joined',
        'data-relation-changed',
        'data-relation-departed',
        'data-relation-broken',
        'peer-relation-joined',
        'peer-relation-changed',
        'peer-relation-departed',
        'nrpe-external-master-relation-changed',
        'rest-relation-joined',
        'start',
        'stop',
        'upgrade-charm',
        'client-relation-joined',
        'client-relation-departed',
    ])


@hooks.hook('install', 'upgrade-charm')
def install():
    """Install ansible before running the tasks tagged with 'install'."""
    # Allow charm users to run preinstall setup.
    charmhelpers.payload.execd.execd_preinstall()
    charmhelpers.contrib.ansible.install_ansible_support(
        from_ppa=False)

    # We copy the backported ansible modules here because they need to be
    # in place by the time ansible runs any hook.
    charmhelpers.core.host.rsync(
        'ansible_module_backports',
        '/usr/share/ansible')


@hooks.hook('data-relation-joined', 'data-relation-changed')
def data_relation():
    if hookenv.relation_get('mountpoint') == mountpoint:
        # Other side of relation is ready
        migrate_to_mount(mountpoint)
    else:
        # Other side not ready yet, provide mountpoint
        hookenv.log('Requesting storage for {}'.format(mountpoint))
        hookenv.relation_set(mountpoint=mountpoint)


@hooks.hook('data-relation-departed', 'data-relation-broken')
def data_relation_gone():
    hookenv.log('Data relation no longer present, stopping elasticsearch.')
    charmhelpers.core.host.service_stop('elasticsearch')


def migrate_to_mount(new_path):
    """Invoked when new mountpoint appears. This function safely migrates
    elasticsearch data from local disk to persistent storage (only if needed)
    """
    old_path = '/var/lib/elasticsearch'
    if os.path.islink(old_path):
        hookenv.log('{} is already a symlink, skipping migration'.format(
            old_path))
        return True
    # Ensure our new mountpoint is empty. Otherwise error and allow
    # users to investigate and migrate manually
    files = os.listdir(new_path)
    try:
        files.remove('lost+found')
    except ValueError:
        pass
    if files:
        raise RuntimeError('Persistent storage contains old data. '
                           'Please investigate and migrate data manually '
                           'to: {}'.format(new_path))
    os.chmod(new_path, 0o700)
    charmhelpers.core.host.service_stop('elasticsearch')
    # Ensure we have trailing slashes
    charmhelpers.core.host.rsync(os.path.join(old_path, ''),
                                 os.path.join(new_path, ''),
                                 options=['--archive'])
    shutil.rmtree(old_path)
    os.symlink(new_path, old_path)
    charmhelpers.core.host.service_start('elasticsearch')


if __name__ == "__main__":
    hooks.execute(sys.argv)
