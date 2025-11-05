#!/usr/bin/env python3
import os
import sys
import yaml
from intent_validator import IntentValidator

# Directory scan for intent_*.yaml files
intent_files = [f for f in os.listdir('.') if f.startswith('intent_') and f.endswith('.yaml')]
if not intent_files:
    print("No intent_*.yaml files found in the current directory.")
    sys.exit(1)

print(f"Found {len(intent_files)} intent files: {', '.join(intent_files)}")

validator = IntentValidator()
os.makedirs('policies', exist_ok=True)

for file in intent_files:
    print(f"\nProcessing {file}...")
    try:
        with open(file, 'r') as f:
            intent = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {file}: {e}")
        continue

    errors = validator.validate(intent)
    if errors:
        print(f"Validation failed for {file}:")
        for e in errors:
            print("   -", e)
        continue

    print("Validation passed.")

    warnings, suggestions = validator.semantic_analysis(intent)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print("  -", w)
    if suggestions:
        print("Suggestions:")
        for s in suggestions:
            print("  -", s)

    # Build the Kubernetes NetworkPolicy object
    policy = {
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

    # Add egress rules based on the intent specification
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

        policy['spec']['egress'].append(egress_rule)

    # Write the resulting NetworkPolicy to a YAML file
    policy_file = f"policies/{intent['metadata']['name']}-networkpolicy.yaml"
    try:
        with open(policy_file, 'w') as f:
            yaml.dump(policy, f, sort_keys=False)
        print(f"Created Kubernetes policy: {policy_file}")
    except Exception as e:
        print(f"Error writing policy for {file}: {e}")
        continue

print("\nAll intent files have been processed successfully.")
