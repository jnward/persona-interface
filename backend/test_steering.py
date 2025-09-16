#!/usr/bin/env python3
"""
Test script for verifying PC-based steering functionality.
Tests single and multiple PC steering with different magnitudes.
"""

import requests
import json
import time


API_URL = "http://localhost:8000"


def test_no_steering():
    """Baseline test without steering."""
    print("\n" + "="*60)
    print("Testing WITHOUT steering (baseline)")
    print("="*60)

    request_data = {
        "messages": [
            {"role": "user", "content": "What are you?"}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 50,
        "is_partial": False
    }

    response = requests.post(f"{API_URL}/api/generate", json=request_data)

    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['content']}")
        return result['content']
    else:
        print(f"Error: {response.text}")
        return None


def test_single_pc_steering():
    """Test steering with a single PC at different magnitudes."""
    print("\n" + "="*60)
    print("Testing SINGLE PC steering (PC1 at different magnitudes)")
    print("="*60)

    magnitudes = [-3000, 0, 3000]
    responses = {}

    for magnitude in magnitudes:
        print(f"\n--- PC1 = {magnitude:+.0f} ---")

        request_data = {
            "messages": [
                {"role": "user", "content": "What are you?"}
            ],
            "steering_config": {
                "pc_values": {"0": magnitude} if magnitude != 0 else {}
            },
            "num_tokens": 50,
            "is_partial": False
        }

        response = requests.post(f"{API_URL}/api/generate", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['content']}")
            responses[magnitude] = result['content']
        else:
            print(f"Error: {response.text}")
            responses[magnitude] = None

    return responses


def test_multiple_pc_steering():
    """Test steering with multiple PCs combined."""
    print("\n" + "="*60)
    print("Testing MULTIPLE PC steering (combining PC1 and PC2)")
    print("="*60)

    test_cases = [
        {"pc_values": {"0": 2000, "1": 2000}, "label": "PC1=+2000, PC2=+2000"},
        {"pc_values": {"0": 2000, "1": -2000}, "label": "PC1=+2000, PC2=-2000"},
        {"pc_values": {"0": -2000, "1": 2000}, "label": "PC1=-2000, PC2=+2000"},
        {"pc_values": {"0": 3000, "3": 1000}, "label": "PC1=+3000, PC4=+1000"},
    ]

    responses = {}

    for test_case in test_cases:
        print(f"\n--- {test_case['label']} ---")

        request_data = {
            "messages": [
                {"role": "user", "content": "What are you?"}
            ],
            "steering_config": {
                "pc_values": test_case["pc_values"]
            },
            "num_tokens": 50,
            "is_partial": False
        }

        response = requests.post(f"{API_URL}/api/generate", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['content']}")
            responses[test_case['label']] = result['content']
        else:
            print(f"Error: {response.text}")
            responses[test_case['label']] = None

    return responses


def test_conversation_with_steering():
    """Test steering in a multi-turn conversation."""
    print("\n" + "="*60)
    print("Testing steering in CONVERSATION")
    print("="*60)

    # First turn without steering
    print("\n--- First turn (no steering) ---")
    request_data = {
        "messages": [
            {"role": "user", "content": "Hello! Tell me about yourself."}
        ],
        "steering_config": {"pc_values": {}},
        "num_tokens": 50,
        "is_partial": False
    }

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    result = response.json()
    first_response = result['content']
    print(f"Assistant: {first_response}")

    # Second turn with strong positive steering
    print("\n--- Second turn (PC1=+4000) ---")
    request_data = {
        "messages": [
            {"role": "user", "content": "Hello! Tell me about yourself."},
            {"role": "assistant", "content": first_response},
            {"role": "user", "content": "What makes you unique?"}
        ],
        "steering_config": {"pc_values": {"0": 4000}},
        "num_tokens": 50,
        "is_partial": False
    }

    response = requests.post(f"{API_URL}/api/generate", json=request_data)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    result = response.json()
    print(f"Assistant: {result['content']}")


def test_step_mode_with_steering():
    """Test that step mode works with steering."""
    print("\n" + "="*60)
    print("Testing STEP MODE with steering (PC1=+2000)")
    print("="*60)

    request_data = {
        "messages": [
            {"role": "user", "content": "Count to five:"}
        ],
        "steering_config": {"pc_values": {"0": 2000}},
        "num_tokens": 1,
        "is_partial": False
    }

    accumulated = ""
    print("Generating token by token...")

    for i in range(15):
        response = requests.post(f"{API_URL}/api/generate", json=request_data)

        if response.status_code != 200:
            print(f"Error: {response.text}")
            break

        result = response.json()
        token = result['content']
        accumulated += token
        print(f"  Token {i+1}: '{token}'")

        # Update messages for next request
        if len(request_data["messages"]) == 1:
            request_data["messages"].append({"role": "assistant", "content": token})
        else:
            request_data["messages"][-1]["content"] += token

        request_data["is_partial"] = True

        if result['terminating']:
            print(f"  (terminated after {i+1} tokens)")
            break

    print(f"\nFull response: {accumulated}")


def main():
    """Run all steering tests."""
    print("="*60)
    print("PC-BASED STEERING TEST SUITE")
    print("="*60)

    print("\nWaiting for server to be ready...")
    time.sleep(2)

    # Check server health
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print("Server not responding!")
            return

        status = response.json()
        if not status.get("model_loaded") or not status.get("pca_loaded"):
            print("Model or PCA vectors not loaded!")
            return

        print("Server ready!")
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        return

    # Run tests
    print("\nRunning tests...")

    # Test 1: No steering baseline
    baseline = test_no_steering()

    # Test 2: Single PC steering
    single_pc_results = test_single_pc_steering()

    # Test 3: Multiple PC steering
    multi_pc_results = test_multiple_pc_steering()

    # Test 4: Conversation with steering
    test_conversation_with_steering()

    # Test 5: Step mode with steering
    test_step_mode_with_steering()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    print("\n✓ All tests completed!")
    print("\nKey observations:")
    print("1. Baseline response provides a reference point")
    print("2. Single PC steering should show variation with magnitude")
    print("3. Multiple PC combination demonstrates naive addition")
    print("4. Steering persists across conversation turns")
    print("5. Step mode maintains steering throughout generation")


if __name__ == "__main__":
    main()