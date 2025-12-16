# 🏆 AI Champion Ship Hackathon - Compliance & Roadmap

## Dealfu - Sales Simulation Training App

**Deadline:** December 12, 2025 @ 5:00pm PST  
**Target Categories:** 
- 🎙️ Best Voice Agent (ElevenLabs) - $2K+ prizes
- ⚡ Best Ultra-Low Latency App (Cerebras) - $1K+ prizes
- 🏆 Best Overall Idea - $10K grand prize

---

## 📊 Current Compliance Status

### ✅ COMPLIANT (What You Have)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| ElevenLabs Integration | ✅ | `elevenlabs_client.py` - TTS working |
| Cerebras Integration | ✅ | `cerebras_client.py` - LLM working |
| AI Coding Assistant | ✅ | Built with Kiro |
| Working Application | ✅ | Frontend + Backend functional |
| New Project | ✅ | Created during hackathon |
| Demo Video Ready | ⏳ | Need to create |

### ✅ NOW COMPLIANT (After Implementation)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **Raindrop SmartMemory** | ✅ | `raindrop_client.py` - Working Memory API |
| **ElevenLabs Turbo** | ✅ | `eleven_turbo_v2_5` model for speed |
| **Vultr PostgreSQL** | ✅ | `database.py` - Session tracking & leaderboard |

### ⚠️ STILL NEEDED

| Requirement | Status | Impact | Priority |
|-------------|--------|--------|----------|
| **Backend on Raindrop** | ⚠️ | Deploy via Raindrop MCP | 🟡 P1 |
| **ElevenLabs Showcase Submit** | ❌ | Required for Voice category | 🟡 P1 |
| **WorkOS Authentication** | ❌ | Judging criteria (launch quality) | 🟡 P1 |
| **Payment Processing** | ❌ | Judging criteria (encouraged) | 🟢 P2 |

---

## ✅ ELIGIBILITY STATUS: COMPLIANT

Your app now has:
1. ✅ **Raindrop SmartMemory** - Full API integration in `raindrop_client.py`
2. ✅ **Vultr PostgreSQL** - Session tracking & leaderboard in `database.py`
3. ✅ **Cerebras** - Ultra-low latency LLM inference
4. ✅ **ElevenLabs** - Voice synthesis with turbo model

**Remaining for polish:**
- Deploy backend on Raindrop platform (optional but recommended)
- Add WorkOS authentication (improves judging score)
- Submit to ElevenLabs Showcase

---

## 🎯 Judging Criteria Breakdown

| Criteria | Weight | Your Score | Notes |
|----------|--------|------------|-------|
| Raindrop Smart Components | 20% | 18/20 | ✅ SmartMemory integrated |
| Vultr Services | 20% | 18/20 | ✅ PostgreSQL for sessions/leaderboard |
| Launch Quality | 20% | 12/20 | ⚠️ No auth yet (add WorkOS) |
| Quality of Idea | 20% | 15/20 | ✅ Good concept |
| Submission Quality | 20% | ?/20 | Need video, social posts |

**Current Estimated Score: ~63/100** (eligible and competitive!)

---

## 🛠️ Required Integrations

### 1. Raindrop Platform (MANDATORY)

**What it is:** LiquidMetal's AI-first backend platform accessed via MCP Server

**Smart Components to use:**
- **SmartMemory** → Replace your in-memory dict with actual Raindrop SmartMemory for conversation context
- **SmartBuckets** → Store audio files, session data
- **SmartSQL** → Store user sessions, analytics, leaderboards
- **SmartInference** → Could route AI calls through Raindrop

**Setup:** https://docs.liquidmetal.ai/tutorials/claude-code-mcp-setup/

### 2. Vultr Service (MANDATORY - Pick at least one)

**Options:**
- **Vultr Managed Database (PostgreSQL)** → Store user accounts, session history, leaderboards
- **Vultr Object Storage** → Cache generated audio files for faster replay
- **Vultr Managed Kafka** → Event streaming for real-time analytics
- **Vultr Valkey (Redis)** → Session caching, rate limiting

**Recommended:** Vultr Managed PostgreSQL for user data + session persistence

### 3. WorkOS Authentication (HIGHLY RECOMMENDED)

**Why:** Judging criteria asks "Does it have WorkOS authentication?"
**Benefit:** Free tier supports 1M monthly active users
**Docs:** https://workos.com/docs

### 4. ElevenLabs Showcase (REQUIRED for Voice Category)

**Action:** Submit to https://showcase.elevenlabs.io
**When:** After app is complete

---

## 📋 Implementation Roadmap

### Phase 1: Raindrop Integration (Day 1-2) 🔴 CRITICAL

#### Task 1.1: Set Up Raindrop MCP Server
```bash
# Follow: https://docs.liquidmetal.ai/tutorials/claude-code-mcp-setup/
```

#### Task 1.2: Migrate SmartMemory
Replace `smartmemory_client.py` local storage with actual Raindrop SmartMemory API calls.

**Current (NOT COMPLIANT):**
```python
self._local_storage: dict[str, list[dict]] = {}  # ❌ Local dict
```

**Required (COMPLIANT):**
```python
# Use Raindrop SmartMemory API via MCP or direct API calls
await raindrop.smartmemory.store(session_id, messages)
await raindrop.smartmemory.retrieve(session_id)
```

#### Task 1.3: Deploy Backend on Raindrop
- Move FastAPI backend to Raindrop platform
- Use Raindrop's deployment infrastructure

### Phase 2: Vultr Integration (Day 2-3) 🔴 CRITICAL

#### Task 2.1: Set Up Vultr Managed PostgreSQL
```sql
-- User sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID,
    patience_score INT,
    deal_closed BOOLEAN,
    created_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Conversation history (backup to SmartMemory)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    role VARCHAR(20),
    content TEXT,
    timestamp TIMESTAMP
);

-- Leaderboard
CREATE TABLE leaderboard (
    user_id UUID PRIMARY KEY,
    wins INT DEFAULT 0,
    total_sessions INT DEFAULT 0,
    best_patience_score INT DEFAULT 0
);
```

#### Task 2.2: Add Vultr Object Storage (Optional but impressive)
- Cache generated TTS audio for common responses
- Faster playback on repeated objections

### Phase 3: Authentication (Day 3-4) 🟡 HIGH PRIORITY

#### Task 3.1: Integrate WorkOS
```typescript
// Frontend: Add WorkOS AuthKit
import { AuthKitProvider } from '@workos-inc/authkit-nextjs';
```

```python
# Backend: Verify WorkOS tokens
from workos import WorkOS
workos = WorkOS(api_key=os.getenv("WORKOS_API_KEY"))
```

**Features to add:**
- Sign up / Sign in
- User profiles
- Session history per user
- Personal leaderboard

### Phase 4: Polish & Submission (Day 4-5) 🟢 IMPORTANT

#### Task 4.1: Create Demo Video (Max 3 minutes)
**Must show:**
- App functioning end-to-end
- Raindrop integration (show SmartMemory working)
- Vultr integration (show database queries)
- Voice interaction (ElevenLabs)
- Fast responses (Cerebras)

#### Task 4.2: Social Media Posts
- Post on X/Twitter tagging @LiquidMetalAI and @Vultr
- Post on LinkedIn
- Include demo video or screenshots

#### Task 4.3: Submit to ElevenLabs Showcase
- https://showcase.elevenlabs.io

#### Task 4.4: Write Project Description
- Problem you're solving
- Features and functionality
- How you used Raindrop, Vultr, ElevenLabs, Cerebras
- PRD (can be Raindrop-generated)

#### Task 4.5: Provide Platform Feedback
- Write meaningful feedback on Raindrop experience
- Write meaningful feedback on Vultr experience
- This is part of judging criteria!

---

## 🏗️ Architecture After Compliance

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                   (Vercel/Netlify)                          │
│  Next.js 14 + WorkOS Auth + ElevenLabs Voice               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAINDROP PLATFORM                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ SmartMemory │  │  SmartSQL   │  │SmartBuckets │         │
│  │ (Context)   │  │ (Analytics) │  │  (Audio)    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────────────────────────────────────┐           │
│  │           FastAPI Backend                    │           │
│  │  • Orchestrator                              │           │
│  │  • Cerebras Client (Ultra-low latency)      │           │
│  │  • ElevenLabs Client (Voice)                │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    VULTR SERVICES                            │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Managed PostgreSQL  │  │   Object Storage    │          │
│  │ (Users, Sessions,   │  │   (Audio Cache)     │          │
│  │  Leaderboard)       │  │                     │          │
│  └─────────────────────┘  └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Submission Checklist

### Required:
- [ ] Live deployed app URL
- [ ] Source code (public GitHub with open source license OR .zip)
- [ ] Demo video (max 3 min) on YouTube/Vimeo
- [ ] Project description explaining:
  - [ ] Problem being solved
  - [ ] Features and functionality
  - [ ] How Raindrop was used
  - [ ] How Vultr was used
  - [ ] Additional integrations (Cerebras, ElevenLabs)
- [ ] Submit to ElevenLabs Showcase (for Voice category)

### Optional but Scored:
- [ ] PRD (Raindrop-generated)
- [ ] Feedback on Raindrop platform
- [ ] Feedback on Vultr platform
- [ ] Social media posts tagging @LiquidMetalAI and @Vultr

---

## 🎯 Winning Strategy

### For Voice Agent Category ($2K first place):
1. ✅ ElevenLabs integration (you have this)
2. 🔧 Make voice feel natural and human
3. 🔧 Reduce latency for real-time conversation
4. 🔧 Submit to ElevenLabs Showcase

### For Ultra-Low Latency Category ($1K first place):
1. ✅ Cerebras integration (you have this)
2. 🔧 Optimize for speed - show millisecond response times
3. 🔧 Use streaming responses
4. 🔧 Benchmark and display latency metrics

### For Best Overall ($10K grand prize):
1. 🔧 Polish everything
2. 🔧 Add authentication (WorkOS)
3. 🔧 Add leaderboard/gamification
4. 🔧 Make it feel "launch ready"
5. 🔧 Great demo video
6. 🔧 Strong social media presence

---

## 📞 Resources & Support

- **Raindrop Docs:** https://docs.liquidmetal.ai/
- **Vultr Docs:** https://docs.vultr.com/
- **ElevenLabs Docs:** https://elevenlabs.io/docs/overview
- **Cerebras Docs:** https://inference-docs.cerebras.ai/quickstart
- **WorkOS Docs:** https://workos.com/docs
- **Discord:** https://discord.gg/j7HHdx3jkm (#ai-champion-ship)
- **Email:** hackathon@liquidmetal.ai

---

## 🚀 LET'S WIN THIS!

You have a solid app concept. The voice + low-latency angle is perfect for two categories. 
The main work is integrating Raindrop and Vultr properly - that's what makes you eligible.

**Priority order:**
1. Raindrop SmartMemory integration
2. Deploy backend on Raindrop
3. Vultr PostgreSQL for user data
4. WorkOS authentication
5. Demo video + submission

You've got this! 💪
