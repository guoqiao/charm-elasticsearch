#!/bin/bash

set -eux # -x for verbose logging to juju debug-log

VERSION=$(config-get version)
CLUSTER_NAME=$(config-get cluster-name)
BOOTSTRAP_CLASS=$(config-get bootstrap-class)
ACCESS_KEY=$(config-get access-key)
SECRET_KEY=$(config-get secret-key)
REGION=$(config-get region)
CHECKSUM=$(config-get checksum)
DOWNLOADURL=$(config-get downloadurl)
CHECKSUMWRAPPER=$(config-get checksum-wrapper)
ZENMASTERS=$(config-get zenmasters)