# Xe-Bot Animation API

## Public API for Animation Generation

Base URL: `https://your-deployment-url.com`

---

## Authentication

All requests require an API key in the header:

```
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Search Papers

```http
GET /api/search?query=transformers&max_results=5
```

**Response:**
```json
{
  "papers": [
    {
      "arxiv_id": "1706.03762",
      "title": "Attention Is All You Need",
      "authors": ["Vaswani et al."],
      "summary": "..."
    }
  ]
}
```

---

### 2. Generate Animation

```http
POST /api/generate
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "arxiv_id": "1706.03762",
  "quality": "low",
  "segments": true
}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "estimated_time": "5-10 minutes"
}
```

---

### 3. Check Job Status

```http
GET /api/jobs/{job_id}
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "videos": [
    {
      "segment": 1,
      "url": "https://your-url.com/videos/abc123/segment_1.mp4",
      "download_url": "https://your-url.com/download/abc123/segment_1.mp4"
    }
  ]
}
```

---

### 4. Generate Code Only (No Rendering)

```http
POST /api/generate-code
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "topic": "Neural Network Architecture",
  "key_concepts": ["layers", "activation", "backpropagation"]
}
```

**Response:**
```json
{
  "manim_code": "from manim import *\n\nclass NeuralNetwork(Scene):..."
}
```

---

### 5. List All Videos

```http
GET /api/videos
Authorization: Bearer YOUR_API_KEY
```

---

## Rate Limits

| Tier | Requests/day | Concurrent Jobs |
|------|--------------|-----------------|
| Free | 10 | 1 |
| Basic | 50 | 3 |
| Pro | Unlimited | 10 |

---

## SDK Usage

### Python
```python
from xebot import XeBotClient

client = XeBotClient(api_key="your-key")
result = client.generate_animation("1706.03762")
print(result.videos)
```

### JavaScript
```javascript
import { XeBot } from 'xebot-sdk';

const client = new XeBot({ apiKey: 'your-key' });
const result = await client.generateAnimation('1706.03762');
console.log(result.videos);
```

---

## Webhooks (Optional)

Register a webhook to get notified when animations complete:

```http
POST /api/webhooks
{
  "url": "https://your-app.com/webhook",
  "events": ["job.completed", "job.failed"]
}
```
