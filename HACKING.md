# Local development

To deploy ElasticSearch locally, pull the bzr branch into your
local charm repository and deploy from there:

    mkdir -p ~/charms/trusty && cd ~/charms/trusty
    charm-get trusty/elasticsearch
    juju bootstrap
    juju deploy --repository=../.. local:elasticsearch


# Testing the ElasticSearch charm

Run the unit-tests with `make test`.

Run the functional tests with `juju test`.

