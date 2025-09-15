# Persona Steering Interface - Design Document (v0)

## 1. Project Overview

The Persona Steering Interface is an interactive web application that allows users to explore and control the behavior of the Gemma-3-12b language model through principal component (PC) steering. Users can adjust multiple PC sliders to influence the model's responses during text generation.

### Background
The PCs come from the model's persona subspace, generated based on Christina Lu's work from [persona-subspace](https://github.com/lu-christina/persona-subspace). These vectors represent different behavioral dimensions discovered through PCA analysis of persona activations.

### Core Concept
- **Persona Steering**: Manipulate model behavior by adjusting activation vectors derived from PCA of persona representations
- **Interactive Control**: Modify steering parameters to shape model responses
- **Chat Interface**: Multi-turn conversation support with steering applied consistently

## 2. Core Requirements

### System Requirements
- **Model**: Google Gemma-3-12b-it (12B parameter model)
- **GPU**: CUDA-capable GPU with sufficient VRAM for model + inference
- **Python**: 3.10+ with PyTorch, Transformers
- **Node.js**: 18+ for Next.js frontend
- **Steering Vectors**: Pre-computed PCA components loaded from disk

### Key Challenges
- **Chat Functionality**: Current implementation (8_steering.py) only handles single prompts - need to implement proper chat context management
- **Multiple Concurrent Vectors**: May need experimentation with scaling factors or normalization when combining multiple PC adjustments

## 3. Key Features (v0)

### 3.1 Chat Interface
- **Message History**: Scrollable chat with user/assistant messages
- **Input Field**: Text area with submit button and keyboard shortcuts
- **Token Count**: User specifies number of tokens to generate
- **Regenerate**: Re-generate last assistant response with same/different steering
- **Context Display**: Show current context usage

### 3.2 Steering Controls
- **PC Sliders**:
  - Support for multiple PCs (PC1-PC10)
  - Range: -5000 to +5000 magnitude
  - Real-time preview of current values
  - Reset individual or all sliders
- **Fixed Configuration**:
  - Layer 22 steering (hardcoded)
  - Apply to all token positions

### 3.3 Generation Controls (v0)
- **Token Count Input**: Specify number of tokens to generate
- **Generate Button**: Start generation (runs to completion)
- **Step Mode**: Generate one token at a time with manual stepping
- **Current Token Display**: Show token being generated

## 4. Architecture Design

### 4.1 High-Level Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Chat UI     │  │ Slider Panel │  │ Generation       │  │
│  │ Component   │  │ Component    │  │ Controls         │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│                           │                               │
│  ┌────────────────────────┴────────────────────────────┐  │
│  │              State Management (Zustand)             │  │
│  │  - Chat history                                     │  │
│  │  - Steering configuration                           │  │
│  │  - Partial generations                              │  │
│  └────────────────────────┬────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────┘
                           │
                     REST API (POST)
                           │
┌──────────────────────────┴────────────────────────────────┐
│              Backend (FastAPI) - STATELESS                │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             Single Endpoint: /api/generate          │  │
│  │                                                     │  │
│  │  Request:  (messages, steering_config, num_tokens)  │  │
│  │     ↓                                              │  │
│  │  1. Apply chat template to messages                │  │
│  │  2. Load steering vectors based on pc_values       │  │
│  │  3. Apply steering with ActivationSteering         │  │
│  │  4. Generate num_tokens tokens                     │  │
│  │     ↓                                              │  │
│  │  Response: { content: "generated text" }           │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  [Model & PCA vectors loaded once at startup]            │
└───────────────────────────────────────────────────────────┘
```

### 4.2 Frontend Architecture

```typescript
// Simplified Component Structure for v0
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── Message.tsx
│   │   └── InputArea.tsx
│   ├── controls/
│   │   ├── SteeringPanel.tsx
│   │   ├── PCSlider.tsx
│   │   └── TokenControls.tsx
│   └── common/
│       └── Layout.tsx
├── hooks/
│   ├── useGeneration.ts
│   └── useSteering.ts
├── store/
│   ├── chatStore.ts
│   └── steeringStore.ts
└── types/
    └── index.ts
```

### 4.3 Backend Architecture (Simplified)

```python
# Minimal Module Structure for v0
backend/
├── main.py              # FastAPI app with single endpoint
├── generation.py        # Generation logic with steering
├── model_manager.py     # Load model and PCA vectors
├── schemas.py          # Pydantic models
├── config.py           # Configuration (paths, model name)
└── tests/
    ├── test_generation.py
    └── test_steering.py
```

The backend is intentionally minimal:
- **main.py**: FastAPI app with just `/api/generate` endpoint
- **generation.py**: Applies steering and generates tokens
- **model_manager.py**: Loads and caches model + PCA vectors on startup
- **schemas.py**: Request/response models
- **config.py**: Hardcoded paths and settings

## 5. API Specification

### 5.1 Single Endpoint Design (v0)

The backend is completely stateless with just one endpoint:

```yaml
POST   /api/generate
  body: {
    messages: Message[],       # Full conversation history
    steering_config: {          # PC values to apply
      pc_values: { 0: 1000, 3: -2000 }  # e.g., PC1=1000, PC4=-2000
    },
    num_tokens: number          # How many tokens to generate (1 for step mode)
  }
  response: {
    content: string,            # The generated text
    terminating: boolean        # True if model output end-of-turn token
  }
```

### 5.2 How It Handles All Use Cases

#### Normal Generation
```javascript
// Frontend sends full conversation + steering config
POST /api/generate
{
  messages: [
    { role: "user", content: "What are you?" }
  ],
  steering_config: { pc_values: { 2: 3000 } },
  num_tokens: 50
}
// Returns: { content: "I am an AI assistant...", terminating: true }
```

#### Step-by-Step Mode
```javascript
// Same endpoint, just num_tokens: 1
POST /api/generate
{
  messages: [
    { role: "user", content: "Hello" },
    { role: "assistant", content: "Hi" }  // Partial generation so far
  ],
  steering_config: { pc_values: {} },
  num_tokens: 1
}
// Returns: { content: " there", terminating: false }  // Single token, not done

// Next call:
{
  messages: [
    { role: "user", content: "Hello" },
    { role: "assistant", content: "Hi there" }
  ],
  steering_config: { pc_values: {} },
  num_tokens: 1
}
// Returns: { content: "!", terminating: true }  // End of response
```

#### Mid-Generation Steering Change
```javascript
// User generated "I am", then changed sliders
POST /api/generate
{
  messages: [
    { role: "user", content: "What are you?" },
    { role: "assistant", content: "I am" }  // What was generated before
  ],
  steering_config: { pc_values: { 0: 5000 } },  // New steering!
  num_tokens: 10
}
// Returns: { content: " a helpful AI", terminating: false }  // Continuation
```

#### Regeneration
```javascript
// Frontend removes last assistant message, sends again
POST /api/generate
{
  messages: [
    { role: "user", content: "Tell me a joke" }
    // Previous assistant message removed by frontend
  ],
  steering_config: { pc_values: { 1: -3000 } },  // Maybe different steering
  num_tokens: 100
}
// Returns: { content: "Why did the chicken...", terminating: true }
```

### 5.3 Backend Simplicity

The backend is now a pure function:
- No session state
- No conversation tracking
- No partial generation storage
- Just: (history, steering, num_tokens) → generated_text

All state management happens in the frontend.

## 6. Data Models

### 6.1 TypeScript Interfaces

```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface GenerationRequest {
  messages: Message[];
  steering_config: {
    pc_values: Record<number, number>;  // e.g., { 0: 1000, 3: -2000 }
  };
  num_tokens: number;
}

interface GenerationResponse {
  content: string;     // The generated text
  terminating: boolean; // True if model output an end-of-turn token
}
```

### 6.2 Python Pydantic Models

```python
from pydantic import BaseModel
from typing import Dict, List, Literal

class Message(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class GenerationRequest(BaseModel):
    messages: List[Message]
    steering_config: Dict[str, Dict[int, float]]  # {"pc_values": {0: 1000.0}}
    num_tokens: int = 100

class GenerationResponse(BaseModel):
    content: str
    terminating: bool  # True if model output an end-of-turn token
```

## 7. Frontend Components (v0)

### 7.1 Core Components

#### ChatInterface
- Displays message history with auto-scroll
- Shows current conversation
- Typing indicator during generation
- Regenerate button for last message

#### SteeringPanel
- Array of PCSlider components (PC1-PC10)
- Reset all button
- Shows current configuration

#### PCSlider
- Range slider: -5000 to +5000
- Number input for precise values
- Individual reset button
- PC label with variance explained

#### TokenControls
- Number input for token count
- Generate button
- Step button (for token-by-token mode)

### 7.2 State Management

```typescript
interface ChatStore {
  messages: Message[];
  isGenerating: boolean;
  addMessage: (message: Message) => void;
  regenerateLast: () => void;
}

interface SteeringStore {
  pcValues: Record<number, number>;
  updatePC: (index: number, value: number) => void;
  resetPC: (index: number) => void;
  resetAll: () => void;
}
```

## 8. Testing Strategy

### 8.1 Backend Testing (TDD)

Critical areas requiring careful testing:

```python
class TestChatContext:
    """Test chat functionality (not in original implementation)"""
    def test_conversation_formatting(self):
        """Test proper chat template application"""

    def test_context_window_limits(self):
        """Test handling when approaching context limits"""

    def test_steering_persistence_across_turns(self):
        """Test that steering applies consistently"""

class TestSteeringApplication:
    def test_single_pc_steering(self):
        """Test applying single PC vector"""

    def test_multiple_pc_combination(self):
        """Test combining multiple PCs (scaling/normalization)"""

    def test_load_vectors_from_disk(self):
        """Test loading pre-computed PCA components"""

class TestGeneration:
    def test_token_count_accuracy(self):
        """Test generating exact number of tokens requested"""

    def test_regeneration_consistency(self):
        """Test regeneration maintains chat context"""
```

## 9. Development Phases

### Phase 1: Minimal Backend
- [ ] Set up FastAPI with single `/api/generate` endpoint
- [ ] Load Gemma-3-12b model
- [ ] Load PCA components from `/workspace/persona-subspace/roles/pca/layer22_pos23.pt`
- [ ] Test basic generation without steering

### Phase 2: Steering Implementation
- [ ] Integrate ActivationSteering from existing code
- [ ] Apply single PC steering vector
- [ ] Combine multiple PC vectors (test scaling)
- [ ] Verify steering affects output

### Phase 3: Chat Template
- [ ] Apply proper Gemma-3-12b chat template
- [ ] Test multi-turn conversations
- [ ] Handle edge cases (empty messages, long context)

### Phase 4: Frontend Foundation
- [ ] Create Next.js project
- [ ] Set up Zustand stores
- [ ] Build chat UI components
- [ ] Implement PC sliders (PC1-PC10)

### Phase 5: Integration
- [ ] Connect frontend to backend
- [ ] Implement step-by-step mode (num_tokens: 1)
- [ ] Add regeneration functionality
- [ ] Test steering changes mid-generation

### Phase 6: Polish
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] Basic styling
- [ ] README documentation

## 10. Technical Considerations

### 10.1 Critical Implementation Notes

#### Chat Context Management
- Current implementation (8_steering.py) doesn't handle chat - needs careful implementation
- Must apply proper chat template for Gemma-3-12b
- Track conversation history within session only

#### Multiple PC Combination
- May need scaling/normalization when combining multiple PCs
- Experiment with different combination strategies
- Monitor for unexpected interactions

#### Performance
- Keep model loaded in memory between requests
- Cache PCA components after loading
- Optimize for single-user local deployment initially

### 10.2 Architecture for Future Features

Design backend to support future additions:
- **Streaming**: Structure generation service for token streaming
- **Cancellation**: Use async/await patterns for interruptible generation
- **Pause/Resume**: Consider generation state management

## 11. Future Enhancements (Post-v0)

Features moved to future versions:
- **Streaming Generation**: Real-time token streaming
- **Pause/Resume/Cancel**: Fine-grained generation control
- **Speed Control**: Adjustable generation speed
- **Steering Profiles**: Save/load configurations
- **A/B Testing**: Compare different steering settings
- **Export/Import**: Configuration and chat history export
- **Edit Messages**: Modify previous messages
- **Layer Selection**: UI for choosing steering layer
- **Position Control**: Choose where to apply steering

## 12. Vector Loading

The PCA components are pre-generated and stored at:
```
/workspace/persona-subspace/roles/pca/layer22_pos23.pt
```

The backend must load these vectors on startup and cache them for steering application.

---

*Document Version: 0.1 (v0 Focus)*
*Last Updated: September 2025*
