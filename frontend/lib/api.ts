type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

interface GenerationRequest {
  messages: ChatMessage[];
  steering_config: {
    pc_values: Record<string, number>;
  };
  num_tokens: number;
  is_partial?: boolean;
}

interface GenerationResponse {
  content: string;
  terminating: boolean;
}

const API_BASE = 'http://localhost:8000';

export async function generateText(
  messages: ChatMessage[],
  pcValues: Record<string, number>,
  numTokens: number,
  isPartial: boolean = false
): Promise<GenerationResponse> {
  const request: GenerationRequest = {
    messages,
    steering_config: {
      pc_values: pcValues
    },
    num_tokens: numTokens,
    is_partial: isPartial
  };

  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Generation failed');
  }

  return response.json();
}

function swapRoles(messages: ChatMessage[]): ChatMessage[] {
  return messages.map((message) => ({
    role: message.role === 'user' ? 'assistant' : 'user',
    content: message.content
  }));
}

function ensureValidSequence(messages: ChatMessage[]): ChatMessage[] {
  if (messages.length === 0) {
    return [{ role: 'user', content: '' }];
  }

  if (messages[0].role !== 'user') {
    return [{ role: 'user', content: '' }, ...messages];
  }

  return messages;
}

export async function generateUserMessage(
  messages: ChatMessage[],
  numTokens: number,
  isPartial: boolean = false
): Promise<GenerationResponse> {
  const swapped = ensureValidSequence(swapRoles(messages));

  const request: GenerationRequest = {
    messages: swapped,
    steering_config: {
      pc_values: {}
    },
    num_tokens: numTokens,
    is_partial: isPartial
  };

  const response = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Generation failed');
  }

  return response.json();
}

export async function getServerInfo() {
  const response = await fetch(`${API_BASE}/api/info`);
  if (!response.ok) {
    throw new Error('Failed to get server info');
  }
  return response.json();
}
