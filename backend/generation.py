"""
Text generation logic with optional steering.
"""

import torch
from typing import List, Dict, Tuple, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import config


def format_messages_for_chat(tokenizer: AutoTokenizer, messages: List[Dict[str, str]]) -> str:
    """
    Apply the chat template to a list of messages.

    Args:
        tokenizer: The tokenizer with chat template
        messages: List of message dicts with 'role' and 'content'

    Returns:
        Formatted string ready for tokenization
    """
    # Convert to the format expected by apply_chat_template
    formatted_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    # Apply chat template
    formatted = tokenizer.apply_chat_template(
        formatted_messages,
        tokenize=False,
        add_generation_prompt=True
    )

    return formatted


def check_for_termination(generated_text: str, tokenizer: AutoTokenizer) -> bool:
    """
    Check if the generated text contains end-of-turn tokens.

    Args:
        generated_text: The generated text
        tokenizer: The tokenizer to check special tokens

    Returns:
        True if generation terminated naturally, False otherwise
    """
    # Check for common end tokens
    end_tokens = ["<end_of_turn>", "<|endoftext|>", "</s>", "<eos>"]

    # Also check for the specific EOS token of this tokenizer
    if tokenizer.eos_token:
        end_tokens.append(tokenizer.eos_token)

    # Check if any end token is in the generated text
    for token in end_tokens:
        if token in generated_text:
            return True

    return False


def generate_text(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    messages: List[Dict[str, str]],
    num_tokens: int,
    steering_config: Optional[Dict[str, Dict[int, float]]] = None,
    temperature: float = None,
    top_p: float = None
) -> Tuple[str, bool]:
    """
    Generate text from a conversation with optional steering.

    Args:
        model: The language model
        tokenizer: The tokenizer
        messages: List of conversation messages
        num_tokens: Number of tokens to generate
        steering_config: Optional steering configuration (will be used in Phase 2)
        temperature: Sampling temperature (uses default if None)
        top_p: Top-p sampling parameter (uses default if None)

    Returns:
        Tuple of (generated_text, terminating_flag)
    """
    # Use defaults if not specified
    if temperature is None:
        temperature = config.DEFAULT_TEMPERATURE
    if top_p is None:
        top_p = config.DEFAULT_TOP_P

    # Format messages with chat template
    formatted_prompt = format_messages_for_chat(tokenizer, messages)

    # Tokenize
    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # Store the original input length
    input_length = inputs["input_ids"].shape[1]

    # Generate
    with torch.no_grad():
        # Note: In Phase 2, we'll wrap this with steering context manager
        outputs = model.generate(
            **inputs,
            max_new_tokens=num_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=config.DEFAULT_REPETITION_PENALTY
        )

    # Decode only the new tokens (not the prompt)
    generated_ids = outputs[0][input_length:]
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=False)

    # Check if generation terminated naturally
    terminating = check_for_termination(generated_text, tokenizer)

    # Clean up the text (remove end tokens for display)
    # But keep the text as-is to preserve the actual generation
    clean_text = generated_text

    # Remove common end tokens from the end of the text for cleaner display
    end_tokens = ["<end_of_turn>", "<|endoftext|>", "</s>", "<eos>"]
    if tokenizer.eos_token:
        end_tokens.append(tokenizer.eos_token)

    for token in end_tokens:
        if clean_text.endswith(token):
            clean_text = clean_text[:-len(token)]
            break

    return clean_text.strip(), terminating


def generate_text_with_steering(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    messages: List[Dict[str, str]],
    num_tokens: int,
    pc_values: Dict[int, float],
    pc_vectors,
    layer: int = 22,
    temperature: float = None,
    top_p: float = None
) -> Tuple[str, bool]:
    """
    Generate text with PC-based steering applied.
    This will be implemented in Phase 2.

    Args:
        model: The language model
        tokenizer: The tokenizer
        messages: List of conversation messages
        num_tokens: Number of tokens to generate
        pc_values: Dict mapping PC index to magnitude (e.g., {0: 1000, 3: -2000})
        pca_vectors: The PCA component vectors
        layer: Which layer to apply steering at
        temperature: Sampling temperature
        top_p: Top-p sampling parameter

    Returns:
        Tuple of (generated_text, terminating_flag)
    """
    # For Phase 1, just call regular generation
    # In Phase 2, we'll add the steering logic here
    return generate_text(
        model, tokenizer, messages, num_tokens,
        steering_config={"pc_values": pc_values},
        temperature=temperature,
        top_p=top_p
    )