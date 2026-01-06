A focused prototype to monitor 5 California counties for rent control, fair housing, and landlord-impacting legislation using Firecrawl for web scraping, AI agents for content analysis, and Streamlit for visualization. This MVP will demonstrate core functionality before scaling to full state coverage.
## Technical Architecture
### System Overview
![Architecture Diagram]
```
Firecrawl API → Content Collection → AI Agents Pipeline → PostgreSQL DB → Streamlit Dashboard
                          ↓              ↓            ↓
                    [Scraping]    [Filtering]  [Deduplication]  [Summarization]
```

### Component Breakdown

#### 1. Data Collection Layer
- **Firecrawl API**: Web scraping service for county websites
  - Target counties: Los Angeles, San Francisco, San Diego, Orange, Alameda (representative mix)
  - Scraping targets:
    - County council meeting agendas
    - Legislative archives
    - Housing department pages
    - Planning commission documents
- **Scheduled Execution**: Daily scraping via cron jobs/Airflow

#### 2. AI Agent Pipeline (LangGraph Workflow)

```python
# Agent Workflow Structure
1. Content Filtering Agent (Relevance Classifier)
   → Input: Raw scraped content
   → Process: OpenAI API + RAG with legislation knowledge base
   → Output: Filtered relevant legislation only
   
2. Deduplication Agent (Database Checker)
   → Input: Filtered content + metadata
   → Process: Semantic similarity check + exact URL matching
   → Output: New vs existing content flag
   
3. Summarization Agent
   → Input: New relevant content
   → Process: Structured summary generation with OpenAI
   → Output: {heading, summary, source_link, county, date, relevance_score}
```

#### 3. Storage Layer
- **PostgreSQL Database** (Digital Ocean Managed DB):
  - `legislation` table: id, title, summary, url, county, scraped_date, processed_date, is_new
  - `sources` table: county, website_url, last_scraped, status
  - `summaries` table: legislation_id, heading, summary_text, ai_confidence

#### 4. Presentation Layer
- **Streamlit Dashboard** with:
  - Real-time summary feed
  - County filters and date range selectors
  - Alert notifications for new legislation
  - Source link verification
  - Download as PDF/CSV functionality

#### 5. Deployment Infrastructure
- **Digital Ocean**:
  - Droplet: $24/month (4GB RAM, 2 CPU, 80GB SSD)
  - Managed PostgreSQL: $15/month (1GB storage)
  - Docker containers for:
    - Scraping service
    - Agent processing pipeline
    - Streamlit app
    - Scheduler/cron service

---

## Technology Stack

| Layer | Technology | Purpose | Cost/Month |
|-------|------------|---------|------------|
| **Scraping** | Firecrawl API | Web content extraction | $25 (50K requests) |
| **AI Processing** | OpenAI API (GPT-4o) | Content analysis & summarization | $15-30 (est. 10K tokens/day) |
| **Framework** | LangChain + LangGraph | Agent workflow orchestration | Free (open source) |
| **Database** | PostgreSQL | Data storage & deduplication | $15 (Digital Ocean managed) |
| **Frontend** | Streamlit | Dashboard & visualization | Free (self-hosted) |
| **Infrastructure** | Docker + Digital Ocean | Deployment & scaling | $24 (droplet) |
| **Monitoring** | UptimeRobot | Service health checks | Free tier |

---

## Implementation Plan (4 Weeks)

### Week 1: Setup & Core Infrastructure
- [ ] Digital Ocean droplet setup with Docker
- [ ] PostgreSQL database configuration
- [ ] Firecrawl API integration and test scraping
- [ ] Basic Streamlit skeleton app

### Week 2: Agent Development
- [ ] Content Filtering Agent (RAG-enhanced classifier)
  - Fine-tune on housing legislation examples
  - Confidence threshold configuration
- [ ] Deduplication Agent (hybrid approach)
  - Exact URL matching
  - Semantic similarity using sentence embeddings
- [ ] Summarization Agent (structured output format)

### Week 3: Integration & Workflow
- [ ] LangGraph workflow assembly
- [ ] Database schema implementation
- [ ] Error handling and retry mechanisms
- [ ] Alert system for new legislation

### Week 4: UI & Deployment
- [ ] Streamlit dashboard with filtering
- [ ] Summary cards with expandable details
- [ ] Production deployment pipeline
- [ ] Performance testing and optimization

---

## Cost Breakdown

### Development Costs (One-time)
| Task | Hours | Rate | Total |
|------|-------|------|-------|
| System Architecture & Setup | 16 | $75 | $1,200 |
| Agent Development (3 agents) | 40 | $75 | $3,000 |
| Database & Storage Design | 12 | $75 | $900 |
| Streamlit Dashboard UI | 24 | $75 | $1,800 |
| Testing & Debugging | 16 | $75 | $1,200 |
| Documentation | 8 | $75 | $600 |
| **Total Development Cost** | **116** | | **$8,700** |

### Monthly Operational Costs
| Service | Cost/ Month |
|---------|-------------|
| Digital Ocean Droplet | $24.00 |
| Digital Ocean Managed PostgreSQL | $15.00 |
| Firecrawl API (50K requests) | $25.00 |
| OpenAI API (est. usage) | $25.00 |
| **Total Monthly Cost** | **$89.00** |

---

## Key Features & Deliverables

### Core Functionality
✅ **Automated Scraping**: Daily monitoring of 5 county websites  
✅ **Smart Filtering**: AI-powered relevance detection for housing legislation  
✅ **Deduplication**: Prevents duplicate alerts for same content  
✅ **Structured Summaries**: Clean, readable summaries with source links  
✅ **Real-time Dashboard**: Web interface for monitoring new legislation  

### Sample Output Format
```json
{
  "county": "Los Angeles",
  "heading": "New Rent Stabilization Proposal for Unincorporated Areas",
  "summary": "The LA County Board of Supervisors is considering expanding rent stabilization to unincorporated communities. The proposal would limit annual rent increases to 5% and require just cause eviction protections. Public hearing scheduled for March 15th.",
  "source_link": "https://lacounty.gov/housing/meetings/2024-03-01",
  "date_posted": "2024-03-01",
  "relevance_score": 0.92,
  "is_new": true
}
```

### Streamlit UI Features
- 📊 **Dashboard View**: Cards for each new legislation item
- 🔍 **Search & Filter**: By county, date range, relevance score
- 📈 **Trends**: Visualizations of legislation frequency by county
- ⏰ **Alert System**: Email/Slack notifications for new items
- 📥 **Export**: Download summaries as PDF or CSV

---

## Risk Mitigation & Contingencies

### Technical Risks
- **Website Structure Changes**: 
  - Implement robust error handling
  - Weekly manual verification process
  - Fallback scraping strategies
  
- **API Rate Limits**:
  - Intelligent request scheduling
  - Caching layer for frequent requests
  - Multi-provider strategy (backup scrapers)

- **AI Accuracy**:
  - Human-in-the-loop verification option
  - Confidence score thresholds
  - Feedback mechanism to improve models
