#!/usr/bin/env python3
"""Setup hooks for the elasticsearch charm."""
import http
import os
import shutil
import sys
import json
import re
import requests

import charmhelpers.contrib.ansible
import charmhelpers.payload.execd
import charmhelpers.core.host
from charmhelpers.core import hookenv
from charmhelpers.fetch import add_source, apt_update
from charmhelpers.contrib.charmsupport import nrpe

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
        # 'nrpe-external-master-relation-changed',
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

    # No Java8 on trusty; add appropriate ppa before the install task runs.
    if charmhelpers.core.host.lsb_release()['DISTRIB_CODENAME'] == 'trusty':
        add_source("ppa:openjdk-r/ppa")
        apt_update()


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


def check_elasticsearch_health():
    """ Checks the health status of the current node on the cluster """

    status = None
    r = requests.get('http://127.0.0.1:9200/_cluster/health')
    if r.status_code != http.HTTPStatus.OK:
        hookenv.log("Elastic Search cluster '{}' is not reachable.".format(hookenv.unit_private_ip()), hookenv.ERROR)
        return False

    try:
        status = json.loads(r.text)['status']
    except Exception:
        pass

    if status != 'green':
        hookenv.log("Elastic Search cluster '{}' is not in healthy (green) state.".format(hookenv.unit_private_ip()),
                    hookenv.ERROR)
        return False

    hookenv.log("Elastic Search cluster '{}' is up.".format(hookenv.unit_private_ip()), hookenv.DEBUG)
    return True


@hooks.hook('update-status')
def update_status():
    hookenv.log('Updating status.')
    if charmhelpers.core.host.service_running('elasticsearch'):
        if not check_elasticsearch_health():
            state = 'blocked'
            message = ('elasticsearch is reporting problems with local host '
                       '- please check health')
        else:
            state = 'active'
            message = 'Unit is ready'
    else:
        state = 'blocked'
        message = 'elasticsearch service not running'

    hookenv.status_set(state, message)


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


@hooks.hook('nrpe-external-master-relation-changed', 'upgrade-charm', 'config-changed')
def update_nrpe_checks():
    nrpe_client = nrpe.NRPE()

    nrpe_client.add_check(
        shortname='cluster_health',
        description='Verify the cluster health is green.',
        # class nrpe.Check will convert cmd to full path.
        check_cmd='check_http -H localhost -u /_cluster/health -p 9200 -w 2 -c 3 -s green',
    )
    hookenv.log('check_cluser_health added')

    nrpe_client.add_check(
        shortname='systemd_service',
        description='Check elasticsearch systemd service is running',
        check_cmd='check_systemd.py elasticsearch',
    )
    hookenv.log('check_systemd_service added')

    nrpe_client.write()
    # ansible tasks in playbook.yaml tagged with these hooks
    # will still be triggered after this line.

if __name__ == "__main__":
    hooks.execute(sys.argv)
