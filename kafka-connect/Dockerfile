FROM confluentinc/cp-kafka-connect:7.6.0

# TODO: Pin connector version if the course image expects a different class.
# Verify with `bash scripts/check_connect_plugins.sh` before registering.
RUN confluent-hub install --no-prompt neo4j/kafka-connect-neo4j:5.1.0
