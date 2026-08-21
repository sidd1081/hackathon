export const NOT_DOCUMENTED = "Not explicitly documented.";

// Verified example incidents — each retrieves its target ticket at (or near)
// rank 1 and produces a grounded, cited RCA on the current dataset. They span
// multiple Apache projects so "Use example" demonstrates cross-project coverage.
// See TEST_CASES.md for the full list with expected tickets/confidence.
export const EXAMPLE_INCIDENTS = [
  // Kafka — KAFKA-13122 (High)
  "A Kafka Streams app leaks resources because KeyValueIterator objects returned from state store queries are never closed after use.",
  // Solr — SOLR-15273 (High)
  "A distributed grouped query in Solr throws a NullPointerException when the unique key field has been renamed.",
  // Spark — SPARK-36067 (High)
  "Running the Spark YarnClusterSuite integration tests throws NoClassDefFoundError unless the hadoop-3.2 build profile is explicitly activated.",
  // ZooKeeper — ZOOKEEPER-4325 (High)
  "Calling ZkUtil listSubTreeBFS on the root path throws an IllegalArgumentException because an invalid path with an empty node name is generated.",
  // HBase — HBASE-26088 (Medium)
  "Repeatedly calling Connection.getBufferedMutator for a table leaks thread pool executors and never releases them.",
];

// First example is the default (also used as the textarea placeholder hint).
export const EXAMPLE_INCIDENT = EXAMPLE_INCIDENTS[0];
