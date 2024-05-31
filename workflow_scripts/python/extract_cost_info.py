import re
import os
import sys

with open('/tmp/aws-cost.txt', 'r') as file:
    output = file.read()

print("File content:")
print(output)

pattern = re.compile(r'┃\s*main\s*┃\s*\$(\d+)\s*┃\s*\$(\d+)\s*┃\s*\$(\d+)\s*┃')
match = pattern.search(output)

print(f"Match: {match}")

if match:
    baseline_cost = match.group(1)
    usage_cost = match.group(2)
    total_cost = match.group(3)

    print(f"Baseline cost: ${baseline_cost}")
    print(f"Usage cost: ${usage_cost}")
    print(f"Total cost: ${total_cost}")

    github_output = os.getenv('GITHUB_OUTPUT', 'output.txt')
    with open(github_output, 'a') as output_file:
        output_file.write(f'baseline_cost={baseline_cost}\n')
        output_file.write(f'usage_cost={usage_cost}\n')
        output_file.write(f'total_cost={total_cost}\n')
else:
    print("Can't extract cost info")
    sys.exit(1)
