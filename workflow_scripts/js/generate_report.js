const fs = require('fs');
const path = require('path');

const issue_number = 2;  // Specify the issue number
const directoryPath = process.env.JSON_FILE_PATH;
const extractedDataPath = process.env.EXTRACTED_DATA_PATH;

// read cost report
const costReportPath = fs.readFileSync('/tmp/aws-cost.txt', 'utf8');

// Read the directory and find the first JSON file
const files = fs.readdirSync(directoryPath).filter(file => file.endsWith('.json'));
if (files.length === 0) {
    console.log("No JSON file found.");
    return;
}
const firstJsonFile = files[0];
const filePath = path.join(directoryPath, firstJsonFile);

// Read the content of the JSON file
const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

// Extract latency metrics
const latencyAvg = jsonData.aggregatedEndToEndLatencyAvg;
const latency95pct = jsonData.aggregatedEndToEndLatency95pct;
const latency99pct = jsonData.aggregatedEndToEndLatency99pct;
const latency999pct = jsonData.aggregatedEndToEndLatency999pct;

// Process extracted data
let extractedData = JSON.parse(fs.readFileSync(extractedDataPath, 'utf8'));

// Extract specific fields from benchmark log json and extracted data
const {
    workload_config,
    producer_config,
    consumer_config,
    topic_config,
    replication_factor,
    average_throughput
} = extractedData;

const extractWorkloadConfig = (config) => {
    const keys = [
        'name', 'topics', 'partitionsPerTopic', 'partitionsPerTopicList', 'randomTopicNames',
        'keyDistributor', 'messageSize', 'useRandomizedPayloads', 'randomBytesRatio',
        'randomizedPayloadPoolSize', 'payloadFile', 'subscriptionsPerTopic', 'producersPerTopic',
        'producersPerTopicList', 'consumerPerSubscription', 'producerRate', 'producerRateList',
        'consumerBacklogSizeGB', 'backlogDrainRatio', 'testDurationMinutes', 'warmupDurationMinutes',
        'logIntervalMillis'
    ];

    const pairs = keys.map(key => `${key}: ${config[key]}`);
    return pairs.join('\n');
};

const workloadConfigPairs = extractWorkloadConfig(workload_config);
const configToKeyValuePairs = (config) => {
    return config.split(', ').map(pair => pair.replace('=', ': ')).join('\n');
};

const producerConfigPairs = configToKeyValuePairs(producer_config);
const consumerConfigPairs = configToKeyValuePairs(consumer_config);
const topicConfigPairs = configToKeyValuePairs(topic_config);
const replicationFactorPairs = configToKeyValuePairs(replication_factor);

// Costs are directly used from the steps
const baselineCost = process.env.BASELINE_COST;
const usageCost = process.env.USAGE_COST;
const totalCost = process.env.TOTAL_COST;

// Get current date and time
const now = new Date();
const currentDate = now.toISOString().split('T')[0];
const currentTime = now.toTimeString().split(' ')[0];

// Generate a Markdown formatted report
const markdownReport = `
  ## AutoMQ Benchmark VS. Result 🚀
  ### Benchmark Info
  **Report Generated:** ${currentDate} ${currentTime}
  ### Workload Configuration
  ${workloadConfigPairs}
  ### Producer Configuration
  ${producerConfigPairs}
  ### Consumer Configuration
  ${consumerConfigPairs}
  ### Topic Configuration
  ${topicConfigPairs}
  replicationFactor: ${replicationFactorPairs}
  ### Replication Configuration
  Average Throughput: ${average_throughput} MB/s

  > Cost Estimate Rule: AutoMQ 800MB of storage corresponds to about 25 PUTs and 10 GETs.We have estimated that each GB corresponds to 31.25 PUTs and 12.5 GETs.Assuming a peak throughput of 0.5 GB/s and an average throughput of 0.01 GB/s, with data retention for 7 days, the data volume for 30 days(calculated with 7 days) is:7*24*3600*0.01GB/s = 6048GB = 5.9T ≈ 6T


  | Streaming System | E2E LatencyAvg(ms) | E2E P95 Latency(ms) | E2E P99 Latency(ms) | Baseline Cost | Usage Cost | Total Cost |
  | ---------------- | ------------------ | ------------------- | ------------------- | ------------- | ---------- | ---------- |
  | AutoMQ           | ${latencyAvg}      | ${latency95pct}     | ${latency99pct}     | ${baselineCost} | ${usageCost} | ${totalCost} |
`;

// Post the report as a comment to the specified issue
await github.rest.issues.createComment({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issue_number,
    body: markdownReport
});
