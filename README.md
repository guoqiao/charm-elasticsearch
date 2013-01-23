# Running ElasticSearch

To deploy elasticsearch locally you just need to:

    juju bootstrap
    juju deploy elasticsearch

You can add more units ...  LXC can deal with multicast
  
    juju add-unit elasticsearch

To deploy on ec2 you need to specify a config file with your AWS access key and secret key which are used by
elasticsearch for discovery.  See the elastisearch on ec2 tutorial for more information:

see 

- http://www.elasticsearch.org/tutorials/2011/08/22/elasticsearch-on-ec2.html

For instance in an elasticsearch.yaml config file you would have:

    elasticsearch:
      access-key: Your_AWS_Access_Key
      secret-key: Your_AWS_Secret_Key

You can also set a region config parameter in this file if the us-east region is not the one you want to use for
discovery.  See the elasticache aws plugin documentation for more information:

- https://github.com/elasticsearch/elasticsearch-cloud-aws

# Configuration Options

There is an experimental config item 'zenmasters' which should enable unicast clustering.

Once the unit has started you can test if everything's working by using curl as below to do a health check
which should give you a similar json response.

    curl -XGET 'http://<ec2 dns or ip of a node>:9200/_cluster/health?pretty=true'

    {
      "cluster_name" : "es-demo",
      "status" : "green",
      "timed_out" : false,
      "number_of_nodes" : 2,
      "number_of_data_nodes" : 2,
      "active_primary_shards" : 5,
      "active_shards" : 10,
      "relocating_shards" : 0,
      "initializing_shards" : 0,
      "unassigned_shards" : 0
    }

The download files for the current version are included in the package,  but they can be downloaded by removing the files, or changing the config to point to a different version.

there seems to be something a bit buggy with the service wrapper on the first unit ...  if it's not start/stopping properly,  get in there and hard kill any java processes then start it again using the service wrapper.   seems to work fine after doing that.

will relation join with logstash and kibana charms via the cluster and rest relations.

use http://ip.addr:9200/_plugin/head to see a good status view of the cluster.


see logstash-indexer charm's README.md file for usage examples.
