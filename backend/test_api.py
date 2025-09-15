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


def test_step_mode():
    """Test step-by-step generation (num_tokens=1)."""
    print("\nTesting step-by-step mode...")

    # First token
    request_data = {
        "messages": [
            {"role": "user", "content": "Count to five:"}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 1
    }

    print("Generating one token at a time...")
    accumulated = ""

    for i in range(10):
        response = requests.post(
            f"{API_URL}/api/generate",
            json=request_data
        )

        if response.status_code == 200:
            result = response.json()
            token = result['content']
            accumulated += token
            print(f"Token {i+1}: '{token}' (terminating: {result['terminating']})")

            # Add the generated token to the assistant message for next request
            if len(request_data["messages"]) == 1:
                request_data["messages"].append({"role": "assistant", "content": token})
            else:
                request_data["messages"][-1]["content"] += token

            if result['terminating']:
                print(f"Generation terminated naturally after {i+1} tokens")
                break
        else:
            print(f"Error: {response.text}")
            return False

    print(f"Accumulated response: {accumulated}")
    return True


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
        ("Step Mode", test_step_mode)
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