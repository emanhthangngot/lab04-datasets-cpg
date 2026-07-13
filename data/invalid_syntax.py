# This file intentionally contains a Python syntax error.
# Purpose: trigger a controlled parser failure so that the parser_service
# emits a real error event (status="failed") to the cpg.errors Kafka topic.
# Required by openspec/specs/kafka-spark/spec.md task 1.6: sample all 4 topics.

def broken_function(
    print("this line has a syntax error because the def is never closed")
