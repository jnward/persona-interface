interface GenerationRequest {
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
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
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
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

export async function getServerInfo() {
  const response = await fetch(`${API_BASE}/api/info`);
  if (!response.ok) {
    throw new Error('Failed to get server info');
  }
  return response.json();
}