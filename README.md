# 🤖 LangGraph Prospect-to-Lead Workflow

An end-to-end autonomous AI agent system built with LangGraph that automates B2B lead generation from prospect discovery to outreach and feedback analysis.

## 📋 Overview

This system uses 7 specialized AI agents working collaboratively in a LangGraph workflow to:
1. **Search** for prospects matching your ICP (Ideal Customer Profile)
2. **Enrich** lead data with additional company information
3. **Score** and rank leads based on fit criteria
4. **Generate** personalized outreach emails using GPT-4o-mini
5. **Execute** email campaigns (with dry-run mode)
6. **Track** engagement metrics (opens, clicks, replies, meetings)
7. **Analyze** performance and generate improvement recommendations

## 🏗️ Architecture

```
workflow.json (Configuration)
        ↓
langgraph_builder.py (Orchestrator)
        ↓
    LangGraph
        ↓
┌───────────────────────────────────┐
│  ProspectSearchAgent              │ → Find leads
├───────────────────────────────────┤
│  DataEnrichmentAgent              │ → Enrich data
├───────────────────────────────────┤
│  ScoringAgent                     │ → Score & rank
├───────────────────────────────────┤
│  OutreachContentAgent             │ → Generate emails
├───────────────────────────────────┤
│  OutreachExecutorAgent            │ → Send emails
├───────────────────────────────────┤
│  ResponseTrackerAgent             │ → Track engagement
├───────────────────────────────────┤
│  FeedbackTrainerAgent             │ → Analyze & recommend
└───────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (required for email generation)
- Optional: Apollo, Clearbit, SendGrid API keys

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd langgraph-prospect-lead-workflow
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the .env file and add your API keys
cp .env.example .env
# Edit .env and add your keys
```

**Minimum required in .env:**
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Running the Workflow

```bash
python langgraph_builder.py
```

The system will:
- ✅ Load and validate `workflow.json`
- ✅ Build the LangGraph with 7 agent nodes
- ✅ Execute the complete workflow
- ✅ Generate detailed logs in `logs/`
- ✅ Save feedback recommendations in `data/`

## 📁 Project Structure

```
langgraph-prospect-lead-workflow/
│
├── workflow.json              # Workflow configuration (SINGLE SOURCE OF TRUTH)
├── langgraph_builder.py       # Main orchestrator script
├── .env                       # API keys (DO NOT COMMIT)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── agents/                    # Agent implementations
│   ├── __init__.py           # Base agent class
│   ├── prospect_search.py    # ProspectSearchAgent
│   ├── enrichment.py         # DataEnrichmentAgent
│   ├── scoring.py            # ScoringAgent
│   ├── outreach_content.py   # OutreachContentAgent
│   ├── outreach_executor.py  # OutreachExecutorAgent
│   ├── response_tracker.py   # ResponseTrackerAgent
│   └── feedback_trainer.py   # FeedbackTrainerAgent
│
├── utils/                     # Utility modules
│   ├── tool_loader.py        # Load API credentials
│   ├── validators.py         # Validate workflow JSON
│   └── logger.py             # Logging utilities
│
├── logs/                      # Execution logs (auto-generated)
└── data/                      # Feedback data (auto-generated)
```

## ⚙️ Configuration

### workflow.json

This is the **single source of truth** for the entire workflow. Each agent is configured here:

```json
{
  "workflow_name": "OutboundLeadGeneration",
  "steps": [
    {
      "id": "prospect_search",
      "agent": "ProspectSearchAgent",
      "inputs": {
        "icp": {
          "industry": ["SaaS", "Technology"],
          "location": "USA",
          "employee_count": { "min": 100, "max": 1000 },
          "revenue": { "min": 20000000, "max": 200000000 }
        }
      },
      "tools": [...],
      "output_schema": {...}
    },
    ...
  ]
}
```

**To modify the workflow:**
1. Edit `workflow.json`
2. No code changes needed!
3. Run `python langgraph_builder.py`

## 🔑 API Keys Setup

### Required (Minimum)
- **OpenAI**: For email generation
  - Get key: https://platform.openai.com/api-keys
  - Add to `.env`: `OPENAI_API_KEY=sk-...`

### Optional (Recommended)
- **Apollo.io**: For prospect search
  - Free tier: https://www.apollo.io/
  - Add to `.env`: `APOLLO_API_KEY=...`

- **Clearbit**: For data enrichment
  - Trial: https://clearbit.com/
  - Add to `.env`: `CLEARBIT_API_KEY=...`

- **SendGrid**: For email sending
  - Free tier (100 emails/day): https://sendgrid.com/
  - Add to `.env`: `SENDGRID_API_KEY=...`

### Mock Data Mode
If APIs aren't configured, the system automatically uses **mock data** for demonstration purposes. This allows you to test the complete workflow without any paid APIs!

## 📊 Agent Details

### 1. ProspectSearchAgent
- **Purpose**: Find prospects matching ICP
- **APIs**: Apollo (or mock data)
- **Output**: List of leads with contact info

### 2. DataEnrichmentAgent
- **Purpose**: Enrich leads with company data
- **APIs**: Clearbit (or mock data)
- **Output**: Enriched leads with technologies, news

### 3. ScoringAgent
- **Purpose**: Score and rank leads
- **Logic**: Weighted scoring (revenue, employees, tech, signals)
- **Output**: Ranked leads with scores 0-100

### 4. OutreachContentAgent
- **Purpose**: Generate personalized emails
- **APIs**: OpenAI GPT-4o-mini
- **Output**: Email subject + body for each lead

### 5. OutreachExecutorAgent
- **Purpose**: Send emails
- **APIs**: SendGrid (or dry-run mode)
- **Output**: Campaign ID + send status

### 6. ResponseTrackerAgent
- **Purpose**: Track email engagement
- **Metrics**: Opens, clicks, replies, meetings
- **Output**: Engagement data per email

### 7. FeedbackTrainerAgent
- **Purpose**: Analyze performance & recommend improvements
- **Output**: Metrics + actionable recommendations
- **Storage**: Google Sheets (or local JSON)

## 🎯 ReAct Prompting Pattern

Each agent implements the **ReAct (Reasoning + Acting)** pattern:

```python
agent.think("What should I do?")        # Reasoning
agent.act("Calling API", {...})         # Action
agent.observe("Got 10 results")         # Observation
```

This is logged for transparency and debugging.

## 🧪 Testing

### Run with Mock Data (No APIs needed)
```bash
python langgraph_builder.py
```

All agents will use realistic mock data if APIs aren't configured.

### Run with Real APIs
1. Add API keys to `.env`
2. Set `dry_run: false` in workflow.json (for email sending)
3. Run: `python langgraph_builder.py`

## 📈 Output & Logs

### Console Output
- Real-time progress with colored logs
- Execution summary with key metrics
- Recommendations printed at the end

### Log Files
- Location: `logs/workflow_YYYYMMDD_HHMMSS.log`
- Contains: Complete execution trace, reasoning logs, API calls

### Feedback Data
- Location: `data/feedback_YYYYMMDD_HHMMSS.json`
- Contains: Performance metrics + recommendations

## 🔧 Extending the System

### Add a New Agent

1. **Create agent file**: `agents/my_new_agent.py`
```python
from . import BaseAgent

class MyNewAgent(BaseAgent):
    def execute(self, inputs):
        self.think("Starting my task")
        # Your logic here
        return {'result': 'data'}
```

2. **Register in** `agents/__init__.py`
```python
from .my_new_agent import MyNewAgent
```

3. **Add to** `langgraph_builder.py` AGENT_REGISTRY
```python
AGENT_REGISTRY = {
    ...
    'MyNewAgent': MyNewAgent
}
```

4. **Add step to** `workflow.json`
```json
{
  "id": "my_step",
  "agent": "MyNewAgent",
  "inputs": {...},
  "tools": [...],
  "output_schema": {...}
}
```

### Modify ICP Criteria

Edit `workflow.json` → `steps[0].inputs.icp`:
```json
"icp": {
  "industry": ["FinTech", "HealthTech"],
  "location": "USA",
  "employee_count": { "min": 50, "max": 500 },
  "revenue": { "min": 10000000, "max": 100000000 }
}
```

### Change Scoring Weights

Edit `workflow.json` → `config.scoring.weights`:
```json
"weights": {
  "revenue_match": 0.4,
  "employee_match": 0.2,
  "technology_match": 0.3,
  "signal_strength": 0.1
}
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the virtual environment
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Issues
```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

### LangGraph Errors
```bash
# Update to latest version
pip install --upgrade langgraph langchain langchain-core
```

## 📝 Design Choices

1. **JSON-driven architecture**: All workflow logic in `workflow.json` makes it easy to modify without touching code

2. **Mock data fallback**: Allows testing without API costs

3. **ReAct pattern**: Makes agent reasoning transparent and debuggable

4. **Modular agents**: Each agent is independent and testable

5. **Dry-run mode**: Safe testing of email campaigns

## 🎬 Demo Video

[Link to your demo video - upload to YouTube/Drive]

## 📧 Contact

Created by: [Your Name]
Email: [Your Email]
GitHub: [Your GitHub]

## 📄 License

MIT License - feel free to use for your projects!