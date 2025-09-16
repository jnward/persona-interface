#!/usr/bin/env python3
"""
Simple test script for the persona steering API.
Tests basic generation without steering (Phase 1).
"""

import requests
import json
import time


API_URL = "http://localhost:8000"


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_info_endpoint():
    """Test the info endpoint."""
    print("\nTesting info endpoint...")
    response = requests.get(f"{API_URL}/api/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_basic_generation():
    """Test basic text generation without steering."""
    print("\nTesting basic generation...")

    request_data = {
        "messages": [
            {"role": "user", "content": "What are you?"}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 50
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(
        f"{API_URL}/api/generate",
        json=request_data
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Generated: {result['content']}")
        print(f"Terminating: {result['terminating']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_conversation():
    """Test multi-turn conversation."""
    print("\nTesting multi-turn conversation...")

    request_data = {
        "messages": [
            {"role": "user", "content": "Hi! My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! It's nice to meet you. How can I help you today?"},
            {"role": "user", "content": "What's my name?"}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 30
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(
        f"{API_URL}/api/generate",
        json=request_data
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Generated: {result['content']}")
        print(f"Terminating: {result['terminating']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_steering_basic():
    """Test that steering affects output."""
    print("\nTesting basic steering functionality...")

    # Test without steering
    print("\n1. Without steering:")
    request_data = {
        "messages": [
            {"role": "user", "content": "What are you?"}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 30
    }

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False

    baseline = response.json()
    print(f"Response: {baseline['content'][:100]}...")

    # Test with positive steering
    print("\n2. With PC1=+3000:")
    request_data["steering_config"] = {"pc_values": {"0": 3000}}

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False

    steered = response.json()
    print(f"Response: {steered['content'][:100]}...")

    # Check that outputs are different
    if baseline['content'] != steered['content']:
        print("✓ SUCCESS: Steering changes output!")
        return True
    else:
        print("✗ FAILURE: Steering had no effect")
        return False


def test_multiple_pc_steering():
    """Test combining multiple PC vectors."""
    print("\nTesting multiple PC steering...")

    request_data = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "steering_config": {
            "pc_values": {"0": 2000, "1": -1000, "3": 500}
        },
        "num_tokens": 30
    }

    print(f"Testing with PC1=+2000, PC2=-1000, PC4=+500")

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return False

    result = response.json()
    print(f"Response: {result['content']}")
    print("✓ Multiple PC steering executed successfully")
    return True


def test_step_mode_comparison():
    """Compare regular generation with step-by-step to ensure they match."""
    print("\nTesting step mode vs regular generation (deterministic)...")

    prompt = "Count to five:"
    num_tokens = 10

    # First, generate normally
    print(f"\n1. Generating {num_tokens} tokens normally...")
    request_data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": num_tokens,
        "is_partial": False
    }

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error in normal generation: {response.text}")
        return False

    normal_result = response.json()
    normal_text = normal_result['content']
    print(f"Normal generation: '{normal_text}'")

    # Now generate step-by-step
    print(f"\n2. Generating {num_tokens} tokens step-by-step...")
    request_data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 1,
        "is_partial": False
    }

    step_accumulated = ""
    for i in range(num_tokens):
        response = requests.post(f"{API_URL}/api/generate", json=request_data)
        if response.status_code != 200:
            print(f"Error in step {i+1}: {response.text}")
            return False

        result = response.json()
        token = result['content']
        step_accumulated += token
        print(f"  Step {i+1}: got '{token}'")

        # Update messages for next request
        if len(request_data["messages"]) == 1:
            request_data["messages"].append({"role": "assistant", "content": token})
        else:
            request_data["messages"][-1]["content"] += token

        request_data["is_partial"] = True

        # Stop early if model signals termination
        if result['terminating']:
            print(f"  (terminated after {i+1} tokens)")
            break

    print(f"\nStep-by-step result: '{step_accumulated}'")

    # Compare results
    print("\n3. Comparison:")
    if normal_text == step_accumulated:
        print("✓ SUCCESS: Both methods produced identical output!")
        return True
    else:
        print("✗ FAILURE: Outputs differ!")
        print(f"  Normal:      '{normal_text}'")
        print(f"  Step-by-step: '{step_accumulated}'")

        # Find where they diverge
        for i, (c1, c2) in enumerate(zip(normal_text, step_accumulated)):
            if c1 != c2:
                print(f"  First difference at position {i}: '{c1}' vs '{c2}'")
                break

        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Persona Steering API")
    print("=" * 60)

    # Wait a moment for server to be ready
    print("\nWaiting for server to be ready...")
    time.sleep(2)

    tests = [
        ("Health Check", test_health_check),
        ("Info Endpoint", test_info_endpoint),
        ("Basic Generation", test_basic_generation),
        ("Conversation", test_conversation),
        ("Steering Basic", test_steering_basic),
        ("Multiple PC Steering", test_multiple_pc_steering),
        ("Step Mode Comparison", test_step_mode_comparison)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name}: {status}")


if __name__ == "__main__":
    main()