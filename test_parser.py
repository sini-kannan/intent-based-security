from intent_parser import parse_intent

def run_test_case(name, input_text, container_name):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Input: {input_text.strip()}")
    print("\nGenerated YAML:")
    try:
        yaml_output = parse_intent(input_text, container_name)
        print(yaml_output)
    except Exception as e:
        print(f"Error: {str(e)}")
    print("="*60)

# Test cases
test_cases = [
    ("Web Access", "My container should access web services.", "web-app"),
    ("Database Access", "The application needs to connect to the database.", "database-service"),
    ("Multiple Services", """
    Allow web access.
    Enable database connectivity.
    The app needs to send emails.
    """, "full-stack-app"),
    ("DNS Access", "The container requires DNS resolution.", "dns-client"),
    ("Complex Example", """
    My application needs to access web services.
    It should be able to connect to PostgreSQL.
    Also, it needs to send emails.
    Allow DNS lookups.
    """, "complex-app")
]

# Run all test cases
for name, input_text, container in test_cases:
    run_test_case(name, input_text, container)
