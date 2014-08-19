# Overview

Elasticsearch is a flexible and powerful open source, distributed, real-time
search and analytics engine. Architected from the ground up for use in
distributed environments where reliability and scalability are must haves,
Elasticsearch gives you the ability to move easily beyond simple full-text
search. Through its robust set of APIs and query DSLs, plus clients for the
most popular programming languages, Elasticsearch delivers on the near
limitless promises of search technology.

Excerpt from [elasticsearch.org](http://www.elasticsearch.org/overview/ "Elasticsearch Overview")

# Usage

You can simply deploy one node with:

    juju deploy elasticsearch

You can also deploy and relate the Kibana dashboard:

    juju deploy kibana
    juju add-relation kibana elasticsearch
    juju expose kibana

This will expose the Kibana web UI, which will then act as a front end to
all subsequent Elasticsearch units.

## Scale Out Usage

Deploy three or more units with:

    juju deploy -n3 elasticsearch

And when they have started you can inspect the cluster health:

    juju run --unit elasticsearch/0 "curl http://localhost:9200/_cat/health?v"
    epoch      timestamp cluster       status node.total node.data shards ...
    1404728290 10:18:10  elasticsearch green           2         2      0

See the separate HACKING.md for information about deploying this charm
from a local repository.

### Relating to the Elasticsearch cluster

This charm currently provides the elasticsearch client interface to the
consuming service (cluster-name, host and port). Normally the other service
will only need this data from one elasticsearch unit to start as most client
libraries then query for the list of backends [1].

[1] http://elasticsearch-py.readthedocs.org/en/latest/api.html#elasticsearch

### Discovery

This charm uses unicast discovery which utilises the orchestration
of juju so that whether you deploy on ec2, lxc or any other cloud
provider, the functionality for discovering other nodes remains the same.

When a new unit first joins the cluster, it will update its config
with the other units in the cluster (via the peer-relation-joined
hook), after which ElasticSearch handles the rest.

# Configuration

## Downloading ElasticSearch

This charm installs elasticsearch from a configured apt repository.
By default, this is the 1.0 repository from elasticsearch.org, but
you can configure your own internal repo if you don't want your
deployment to be dependent on external resources.

Alternatively, you can include a files/elasticsearch.deb in the
charm payload and it will be installed instead.

# Contact Information

## Elasticsearch

- [Elasticsearch website](http://www.elasticsearch.org/)
- [Source code](http://github.com/elasticsearch)
- [Mailing List](https://groups.google.com/forum/?fromgroups#!forum/elasticsearch)
- [Other community resources](http://www.elasticsearch.org/community/)
