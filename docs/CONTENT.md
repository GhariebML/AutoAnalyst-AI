# Content Agent Implementation

## Overview

The Content Agent is a core component of AdPilot responsible for generating creative marketing assets including:
- Ad copy for multiple platforms
- Email sequences
- Social media posts
- Blog outlines
- CTA variants

## Architecture

### LLM Integration

The Content Agent uses the enhanced `LLMClient` with:

**Features:**
- **Retry Logic:** Exponential back-off with jitter (max 3 attempts)
- **Streaming Support:** Optional response streaming
- **Temperature Control:** Configurable creativity level
- **Timeout Handling:** Configurable timeout with fallback
- **Rate Limit Handling:** Respects OpenAI rate limit headers

**Configuration:**
```python
from adpilot.services.llm_client import LLMClient

client = LLMClient(
    api_key="<your-openai-key>",
    model="gpt-4o",
    temperature=0.7,      # Creativity level (0-1)
    max_retries=3,        # Retry attempts
    timeout=30,           # Request timeout in seconds
)

response = await client.chat(
    messages=messages,
    temperature=0.7,      # Override default
    stream=False,         # Disable streaming for now
)
```

### Environment Variables

Required environment variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=<your-openai-key>
MODEL_NAME=gpt-4o

# Content Generation
CONTENT_TEMPERATURE=0.7      # Creativity level (default: 0.7)
ENVIRONMENT=development      # development or production
```

### Agent Workflow

The Content Agent follows this pipeline:

1. **Input Validation** – Validate `ContentAgentInput` schema
2. **Message Building** – Construct LLM prompts with strategy and research context
3. **LLM Call** – Send to OpenAI with configured parameters
4. **Response Parsing** – Extract JSON from response
5. **Output Validation** – Validate against `ContentAgentOutput` schema
6. **Error Handling** – Fallback and retry on failure

## Input Schema

**ContentAgentInput**

```typescript
interface ContentAgentInput {
  strategy: StrategyAgentOutput;    // Strategy from Strategy Agent
  research: ResearchAgentOutput;    // Research insights
}
```

## Output Schema

**ContentAgentOutput**

```typescript
interface ContentAgentOutput {
  ads: AdContent[];                 // Generated advertisements
  emailSequences: EmailSequence[];   // Email campaign sequences
  socialPosts: SocialPost[];         // Social media content
  blogOutlines: BlogOutline[];       // Blog post outlines
  ctaVariants: CTAVariant[];         // Call-to-action variations
  contentCalendarNote: string;       // Scheduling notes
}

interface AdContent {
  platform: string;                 // e.g., "Facebook", "Google Ads"
  headline: string;                 // Main ad headline
  body: string;                      // Ad body copy
  cta: string;                       // Call to action text
  performance?: string;              // Expected performance metrics
}

interface EmailSequence {
  subject: string;                  // Email subject line
  preview: string;                  // Email preview text
  body: string;                      // Email body content
  sequence: number;                 // Position in sequence
}

interface SocialPost {
  platform: string;                 // e.g., "LinkedIn", "Twitter"
  content: string;                  // Post content
  hashtags: string[];               // Relevant hashtags
  imagePrompt?: string;              // Image generation prompt
}
```

## Implementation

### Basic Usage

```python
from adpilot.agents.content_agent import ContentAgent
from adpilot.schemas.agent_schemas import ContentAgentInput

# Create agent
agent = ContentAgent()

# Prepare input with strategy and research
input_data = ContentAgentInput(
    strategy=strategy_output,
    research=research_output,
)

# Generate content
output = await agent.run(input_data)

# Access results
for ad in output.ads:
    print(f"[{ad.platform}] {ad.headline}")
    print(f"  {ad.body}")
    print(f"  CTA: {ad.cta}")
```

### Error Handling

```python
from adpilot.core.exceptions import AgentExecutionError

try:
    output = await agent.run(input_data)
except AgentExecutionError as e:
    print(f"Content generation failed: {e}")
    # Implement retry logic or fallback
```

### Temperature Control

Adjust creativity level via environment or parameter:

```python
# Via environment variable
os.environ['CONTENT_TEMPERATURE'] = '0.9'  # More creative

# Or override in runtime
client = LLMClient(
    api_key=config.openai_api_key,
    model=config.model_name,
    temperature=0.9,  # High creativity
)
```

**Temperature Guide:**
- **0.0-0.3:** Deterministic, factual content (best for technical/compliance)
- **0.4-0.6:** Balanced, professional content (recommended)
- **0.7-0.9:** Creative, varied content (good for marketing copy)
- **1.0+:** Highly creative, sometimes unpredictable

## Prompt Engineering

### System Prompt

Located in [prompts/content_system_prompt.md](../src/adpilot/prompts/content_system_prompt.md)

The system prompt defines:
- Agent personality and tone
- Content guidelines
- Brand voice considerations
- Output format requirements

### Message Structure

Messages sent to LLM:

```python
[
    {
        "role": "system",
        "content": "You are a creative marketing copywriter..."
    },
    {
        "role": "user",
        "content": "Generate content using:\n\nStrategy: {...}\n\nResearch: {...}\n\nSchema: {...}"
    }
]
```

## Testing

### Unit Tests

```python
# tests/test_content_agent.py
import pytest
from adpilot.agents.content_agent import ContentAgent
from adpilot.schemas.agent_schemas import ContentAgentOutput

@pytest.mark.asyncio
async def test_content_agent_success(mock_llm):
    """Test successful content generation."""
    agent = ContentAgent()
    
    # Mock LLM response
    mock_response = {
        "ads": [...],
        "email_sequences": [...],
        "social_posts": [...],
    }
    mock_llm.chat.return_value = mock_response
    
    output = await agent.run(input_data)
    
    assert isinstance(output, ContentAgentOutput)
    assert len(output.ads) > 0
```

### Integration Tests

```bash
# With real API key
export OPENAI_API_KEY="<your-openai-key>"
pytest tests/test_content_agent.py -v
```

## API Endpoints

### Submit Campaign

**POST /api/campaigns**

```bash
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "TechCorp",
    "productName": "CloudSync",
    "productDescription": "Enterprise cloud synchronization platform",
    "targetAudience": "IT managers at mid-size companies",
    "goals": ["Increase brand awareness", "Drive sign-ups"],
    "budget": 50000,
    "duration": "3-months",
    "tone": "professional"
  }'
```

**Response (202 Accepted):**
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "message": "Campaign generation queued"
}
```

### Get Task Status

**GET /api/tasks/{taskId}**

```bash
curl http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "taskId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "progress": 50,
  "message": "Campaign generation in progress"
}
```

### Get Campaign Content

**GET /api/campaigns/{campaignId}/content**

```bash
curl http://localhost:8000/api/campaigns/550e8400-e29b-41d4-a716-446655440000/content
```

**Response:**
```json
{
  "ads": [
    {
      "platform": "Facebook",
      "headline": "Discover CloudSync",
      "body": "Transform your cloud infrastructure...",
      "cta": "Learn More",
      "performance": "Expected CTR: 3.2%"
    }
  ],
  "emailSequences": [
    {
      "subject": "Introducing CloudSync - Enterprise Grade Sync",
      "preview": "Limited time offer inside...",
      "body": "Dear IT Manager...",
      "sequence": 1
    }
  ],
  "socialPosts": [
    {
      "platform": "LinkedIn",
      "content": "Excited to announce CloudSync!",
      "hashtags": ["#CloudTech", "#Enterprise", "#Sync"],
      "imagePrompt": "Modern cloud infrastructure diagram"
    }
  ],
  "summary": "Campaign generated successfully"
}
```

## Performance Considerations

### Caching

For identical inputs, cache LLM responses:

```python
import hashlib
import json

def cache_key(strategy, research):
    """Generate cache key from inputs."""
    content = json.dumps({
        'strategy': strategy.model_dump(),
        'research': research.model_dump(),
    })
    return hashlib.sha256(content.encode()).hexdigest()

# Check cache before calling LLM
key = cache_key(strategy, research)
if key in cache:
    return cache[key]
```

### Streaming

For better UX, implement streaming:

```python
response = await client.chat(
    messages=messages,
    stream=True,
)

async for chunk in response:
    if content := chunk.get('choices', [{}])[0].get('delta', {}).get('content'):
        # Stream content to frontend
        await websocket.send_json({"content": content})
```

### Timeout Optimization

Adjust timeout based on content complexity:

```python
# Simple content: 15 seconds
# Complex content: 30 seconds
timeout = 30 if len(strategy.details) > 500 else 15

client = LLMClient(timeout=timeout)
```

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("adpilot.agents.content_agent")
```

### Inspect LLM Response

```python
# Log raw response before parsing
import json

print(json.dumps(response, indent=2))
```

### Validate Output

```python
try:
    output = ContentAgentOutput.model_validate(output_data)
except ValidationError as e:
    print(f"Validation errors: {e.errors()}")
    print(f"Raw data: {output_data}")
```

## Future Enhancements

- [ ] WebSocket streaming for real-time content generation
- [ ] Multi-model support (Claude, Gemini)
- [ ] Content A/B variant generation
- [ ] Image generation integration (DALL-E)
- [ ] Content scheduling and publishing
- [ ] Analytics and performance tracking
- [ ] Content approval workflow

## Related Documentation

- [LLM Client](./API.md)
- [Task Manager](./API.md)
- [FastAPI Integration](./API.md)
- [Dashboard Integration](./DASHBOARD.md)
- [Testing Guide](./TESTING.md)

---

**Last Updated:** May 2026  
**Maintainer:** Sleem
