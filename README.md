# Getting started with ElasticSearch

To deploy ElasticSearch locally:

    juju bootstrap
    juju deploy --repository=../.. local:elasticsearch

You can add more units and they will discover each other and
join the cluster.


## Relating to the Elasticsearch cluster

This charm currently provides the website http interface to the
consuming service, ie. the private address of an elasticsearch unit. The
consuming service can use this on the website-relation-joined
relation to query the cluster for the list of nodes (many client
elasticsearch apis will do this for you [1]).

If it's needed, we can add an elasticsearch cluster interface that
returns the lists of hosts in the cluster.

[1] http://elasticsearch-py.readthedocs.org/en/latest/api.html#elasticsearch


## Discovery

This charm uses unicast discovery which utilises the orchestration
of juju so that the discovery method is the same whether you deploy
on EC2, lxc or any other cloud provider.

When a new unit first joins the cluster, it will update its config
with the other units in the cluster (via the peer-relation-joined
hook), after which ElasticSearch handles the rest.


## Testing the ElasticSearch charm

Run the unit-tests with `make test`.

Run the functional tests with `juju test`.


## Downloading ElasticSearch

This charm installs elasticsearch from a configured apt repository.
By default, this is the 1.0 repository from elasticsearch.org, but
you can configure your own internal repo if you don't want your
deployment to be dependent on external resources.

Alternatively, you can include a files/elasticsearch.deb in the
charm payload and it will be installed instead.
