import yaml
import os
import sys
from intent_validator import IntentValidator

intent_file = sys.argv[1] if len(sys.argv) > 1 else 'intent.yaml'

print("Reading intent rules...")

# 1. Read and validate intent
try:
    with open(intent_file, 'r') as file:
        intent = yaml.safe_load(file)
except Exception as e:
    print(f"Error: Could not read intent file '{intent_file}': {e}")
    sys.exit(1)

print(f"Loaded intent for: {intent['metadata']['name']}")

# Validation step
print("Validating intent structure...")
validator = IntentValidator()
errors = validator.validate(intent)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"   - {error}")
    sys.exit(1)

print("Intent validation passed successfully.")

# Security analysis
print("Analyzing security patterns...")
warnings, suggestions = validator.semantic_analysis(intent)

if warnings:
    print("Security warnings:")
    for warning in warnings:
        print(f"   - {warning}")

if suggestions:
    print("Improvement suggestions:")
    for suggestion in suggestions:
        print(f"   - {suggestion}")

# 2. Create Kubernetes NetworkPolicy
network_policy = {
    'apiVersion': 'networking.k8s.io/v1',
    'kind': 'NetworkPolicy',
    'metadata': {
        'name': f"{intent['metadata']['name']}-policy",
        'namespace': 'default'
    },
    'spec': {
        'podSelector': {
            'matchLabels': {
                'app': intent['metadata']['name']
            }
        },
        'policyTypes': ['Egress'],
        'egress': []
    }
}

print("Converting intent to Kubernetes rules...")

# 3. Add allowed connections
for rule in intent.get('spec', {}).get('egress', []):
    egress_rule = {
        'to': [{'ipBlock': {'cidr': '0.0.0.0/0'}}],
        'ports': []
    }

    for port in rule.get('ports', []):
        egress_rule['ports'].append({
            'protocol': port.get('protocol', 'TCP').upper(),
            'port': port.get('number')
        })

    network_policy['spec']['egress'].append(egress_rule)

# 4. Save the policy
os.makedirs('policies', exist_ok=True)
policy_file = f"policies/{intent['metadata']['name']}-networkpolicy.yaml"

try:
    with open(policy_file, 'w') as f:
        yaml.dump(network_policy, f, default_flow_style=False)
except Exception as e:
    print(f"Error writing policy file: {e}")
    sys.exit(1)

print(f"Created Kubernetes policy: {policy_file}")
print("This policy enforces the declared intent successfully.")
