import yaml
import os
import sys
from intent_validator import IntentValidator

intent_file = sys.argv[1] if len(sys.argv) > 1 else 'intent.yaml'

print("Reading our intent rules...")

# 1. Read and validate intent
with open(intent_file, 'r') as file:
    intent = yaml.safe_load(file)

print(f"Loaded intent for: {intent['metadata']['name']}")

# Validation step
print("Validating intent structure...")
validator = IntentValidator()
errors = validator.validate(intent)

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"   - {error}")
    exit(1)

print("Intent validation passed!")

# Security analysis
print("Analyzing security patterns...")
warnings, suggestions = validator.semantic_analysis(intent)

if warnings:
    print("Security recommendations:")
    for warning in warnings:
        print(f"   - {warning}")

if suggestions:
    print("Suggested improvements:")
    for suggestion in suggestions:
        print(f"   - {suggestion}")

print("Intent validation passed!")

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

# 3. Add the allowed connections
for rule in intent['spec']['egress']:
    egress_rule = {
        'to': [{'ipBlock': {'cidr': '0.0.0.0/0'}}],  # Allow any IP (we'll improve this)
        'ports': []
    }
    
    for port in rule['ports']:
        egress_rule['ports'].append({
            'protocol': port['protocol'].upper(),
            'port': port['number']
        })
    
    network_policy['spec']['egress'].append(egress_rule)

# 4. Save the policy
os.makedirs('policies', exist_ok=True)
policy_file = f"policies/{intent['metadata']['name']}-networkpolicy.yaml"

with open(policy_file, 'w') as f:
    yaml.dump(network_policy, f, default_flow_style=False)

print(f"Created Kubernetes policy: {policy_file}")
print("This policy will enforce our intent rules in Kubernetes!")
