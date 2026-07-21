FROM confluentinc/cp-kafka-connect:7.6.0

# The connector is pinned for reproducible builds. Verify its reported class
# with `bash scripts/check_connect_plugins.sh` before registering.
RUN confluent-hub install --no-prompt neo4j/kafka-connect-neo4j:5.1.0
