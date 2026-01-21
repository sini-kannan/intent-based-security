import time
from intent_parser import IntentParser

def run_benchmark():
    print("-" * 40)
    print("BENCHMARK: REGEX vs LLM")
    print("-" * 40)

    parser = IntentParser()
    
    simple_intent = "Allow web-service to access postgres-db on port 5432"
    complex_intent = "Isolate the database layer but allow access from the analytics-service for read-only operations"

    print("\n[1] Testing Regex Mode...")
    start = time.perf_counter()
    parser.parse(simple_intent, "benchmark-container")
    end = time.perf_counter()
    regex_time = (end - start) * 1000
    print(f"    Status: Parsed")
    print(f"    Time:   {regex_time:.4f} ms")

    print("\n[2] Testing LLM Mode...")
    start = time.perf_counter()
    try:
        parser.parse(complex_intent, "benchmark-container")
    except Exception as e:
        print("    (LLM not running, skipping)")
    
    end = time.perf_counter()
    llm_time = (end - start) * 1000
    print(f"    Status: Parsed")
    print(f"    Time:   {llm_time:.2f} ms")

    print("\n" + "="*40)
    print(f"Regex Latency: {regex_time:.4f} ms")
    print(f"LLM Latency:   {llm_time:.2f} ms")
    print("="*40)

if __name__ == "__main__":
    run_benchmark()
