import re
import json

log_file_path = "debug.output"
output_file_path = "/tmp/extracted_data"

# Define regex patterns
kafka_benchmark_driver_pattern = r'\[.*?\] INFO Benchmark - Initialized Kafka benchmark driver with common config: \{(.*?)\}, producer config: \{(.*?)\}, consumer config: \{(.*?)\}, topic config: \{(.*?)\}, replicationFactor: (\d+)'
workloads_pattern = r'Workloads: \{(.*?)\}'

# Read log file
with open(log_file_path, 'r') as file:
    log_content = file.read()

workloads_match = re.search(workloads_pattern, log_content, re.DOTALL)
if workloads_match:
    workloads_str = workloads_match.group(1).strip()
else:
    workloads_str = "Not found"


def extract_workload_config(config):
    def get_value(key):
        start_index = config.find(f'"{key}"') + len(key) + 4
        end_index = config.find(',', start_index)
        if end_index == -1:
            end_index = config.find('\n', start_index)
        value = config[start_index:end_index].strip()
        if value.endswith(','):
            value = value[:-1]
        return value.replace('"', '')

    keys = [
        "name", "topics", "partitionsPerTopic", "partitionsPerTopicList", "randomTopicNames",
        "keyDistributor", "messageSize", "useRandomizedPayloads", "randomBytesRatio",
        "randomizedPayloadPoolSize", "payloadFile", "subscriptionsPerTopic", "producersPerTopic",
        "producersPerTopicList", "consumerPerSubscription", "producerRate", "producerRateList",
        "consumerBacklogSizeGB", "backlogDrainRatio", "testDurationMinutes", "warmupDurationMinutes",
        "logIntervalMillis"
    ]

    workload_dict = {}
    for key in keys:
        value = get_value(key)
        if value == 'null':
            value = None
        elif value == 'true':
            value = True
        elif value == 'false':
            value = False
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        workload_dict[key] = value

    return workload_dict


if workloads_str != "Not found":
    workloads = extract_workload_config(workloads_str)
else:
    workloads = "Not found"

# Extract KafkaBenchmarkDriver information
kafka_benchmark_driver_match = re.search(kafka_benchmark_driver_pattern, log_content, re.DOTALL)
if kafka_benchmark_driver_match:
    common_config = kafka_benchmark_driver_match.group(1).strip()
    producer_config = kafka_benchmark_driver_match.group(2).strip()
    consumer_config = kafka_benchmark_driver_match.group(3).strip()
    topic_config = kafka_benchmark_driver_match.group(4).strip()
    replicationFactor = kafka_benchmark_driver_match.group(5).strip()
else:
    common_config = "Not found"
    producer_config = "Not found"
    consumer_config = "Not found"
    topic_config = "Not found"
    replicationFactor = "Not found"

# Calculate average throughput
throughput_pattern = r'WorkloadGenerator - Pub rate \d+\.\d+ msg/s \/ (\d+\.\d+) MB/s'
throughput_matches = re.findall(throughput_pattern, log_content)
average_throughput = sum(float(tp) for tp in throughput_matches) / len(throughput_matches) if throughput_matches else 0

# Prepare data for output
extracted_data = {
    "workload_config": workloads,
    "producer_config": producer_config,
    "consumer_config": consumer_config,
    "topic_config": topic_config,
    "replication_factor": replicationFactor,
    "average_throughput": average_throughput
}

# Write to output file
with open(output_file_path, 'w') as outfile:
    json.dump(extracted_data, outfile, indent=4)

# Print the extracted data for verification
print(json.dumps(extracted_data, indent=4))
