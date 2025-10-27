# MakeGPT

## 🧩 Intent-Driven Scenario Synthesizer for Make.com

**MakeGPT** is an AI-powered compiler that translates natural language user intentions into executable Make.com scenarios, generating valid `blueprint.json` files ready for import.

---

## 🎯 Project Vision

Transform natural language requests like:
> "Create a scenario that sends an email when a new form is submitted"

Into fully functional Make.com blueprints that can be:
- ✅ Validated against schema
- ✅ Imported to Make.com
- ✅ Executed and tested
- ✅ Iteratively improved

---

## 🏗️ System Architecture

```
User Input (Natural Language)
          ↓
    IntentPrompt
          ↓
    Intent JSON (entities, action, triggers)
          ↓
    PlanPrompt
          ↓
    AST Tree (abstract scenario flow)
          ↓
    SynthesizePrompt
          ↓
    blueprint.json (Make.com Schema 2.1)
          ↓
    Base64 Encoding
          ↓
    POST /api/v2/scenarios → Make.com
```

---

## ⚙️ Functional Requirements

| ID | Requirement | Input | Output |
|----|-------------|-------|--------|
| **F1** | Intent Analysis | User text | JSON with intent, entities |
| **F2** | Scenario Planning | Intent JSON | Abstract scenario AST |
| **F3** | Blueprint Synthesis | AST | blueprint.json (schema-compliant) |
| **F4** | Base64 Encoding | blueprint.json | Encoded string for API |
| **F5** | Scenario Creation | API call to Make.com | New scenario ID |
| **F6** | Error Handling | 4xx/5xx responses | Retry with exponential backoff |
| **F7** | Continuous Feedback | Existing scenarios | Update RAG knowledge base |

---

## 🎨 Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Accuracy** | Generate valid blueprint.json compliant with JSON Schema 2.1 |
| **Reliability** | 99% success rate for valid scenario creation |
| **Resilience** | Exponential backoff for API errors |
| **Security** | OAuth2 tokens and IMTCONN stored client-side only |
| **Learning** | Feedback loop for validated blueprints into knowledge base |

---

## 🔌 API Integration

### Create Scenario
```http
POST https://eu1.make.com/api/v2/scenarios
Content-Type: application/json

{
  "blueprint": "<base64-encoded-json>",
  "teamId": 123,
  "folderId": 456,
  "scheduling": {
    "type": "indefinitely"
  }
}
```

### Retrieve Blueprint
```http
GET https://eu1.make.com/api/v2/scenarios/{id}/blueprint
Authorization: Token <your-token>
```

---

## 🧱 System Components

| Component | Description |
|-----------|-------------|
| **LLM Engine** | Natural language processing (OpenAI API) |
| **Schema Validator** | JSON validation against Make.com Schema 2.1 |
| **Morphic Bridge** | API adapter for Make.com endpoints |
| **Knowledge Base (RAG)** | Repository of real-world blueprints for training |
| **UI Layer** | CLI or minimal web interface |

---

## 🚀 MVP (Minimum Viable Product)

### Phase 1: Local Blueprint Generation
- ✅ Python CLI application
- ✅ Natural language → blueprint.json conversion
- ✅ Base64 encoding
- ✅ Console output (no API calls yet)

### Phase 2: API Integration
- ✅ Authentication flow (OAuth2)
- ✅ POST to `/api/v2/scenarios`
- ✅ Error handling and retry logic

### Phase 3: Interactive Connection Setup
- ✅ Guide user through IMTCONN linking
- ✅ Validate connections before execution

### Phase 4: Knowledge Enhancement
- ✅ RAG integration with blueprint library
- ✅ Learning from successful scenarios

---

## 📦 Project Structure

```
makegpt/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore patterns
│
├── src/                        # Core application code
│   ├── __init__.py            # Main MakeGPT class & exports
│   ├── main.py                # CLI entry point
│   ├── intent_parser.py       # F1: Intent analysis (Stage 1)
│   ├── planner.py             # F2: Scenario planning (Stage 2)
│   ├── synthesizer.py         # F3: Blueprint synthesis (Stage 3)
│   ├── encoder.py             # F4: Base64 encoding (critical!)
│   ├── make_api.py            # F5: Make.com API client
│   └── schema_validator.py    # Schema validation (Table 2.1)
│
├── prompts/                    # LLM system prompts
│   ├── intent_prompt.txt      # Intent parsing instructions
│   ├── plan_prompt.txt        # Scenario planning instructions
│   └── synthesize_prompt.txt  # Blueprint synthesis instructions
│
├── schemas/                    # JSON Schema definitions
│   └── blueprint_schema_2.1.json  # Reverse-engineered Make.com schema
│
├── knowledge_base/             # RAG training data
│   ├── README.md
│   └── blueprints/
│       ├── example_simple_form_to_email.json
│       ├── example_conditional_router.json
│       └── example_with_error_handling.json
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_encoder.py        # Base64 encoding tests
│   └── test_validator.py      # Schema validation tests
│
└── examples/                   # Sample outputs
    └── sample_blueprints/
        └── README.md
```

**Status**: ✅ **Fully Implemented** - All core components are functional

---

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- Make.com account with API access
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/makegpt.git
cd makegpt
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials:
# OPENAI_API_KEY=your_openai_key
# MAKE_API_TOKEN=your_make_token
# MAKE_TEAM_ID=your_team_id
```

---

## 💻 Usage

### Command Line Interface

```bash
# Generate blueprint from natural language
python -m src.main "Send email when new form submitted"

# Output: blueprint.json + Base64 encoded string

# Create scenario on Make.com
python -m src.main "Send email when new form submitted" --deploy
```

### Python API

```python
from src import MakeGPT

compiler = MakeGPT(
    openai_key="your_key",
    make_token="your_token"
)

# Generate blueprint
blueprint = compiler.compile("Send email when new form submitted")

# Deploy to Make.com
scenario_id = compiler.deploy(blueprint, team_id=123)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Test individual components
pytest tests/test_intent.py
pytest tests/test_synthesizer.py

# Validate blueprint against schema
python -m src.schema_validator examples/sample_blueprint.json
```

---

## 📚 Blueprint Schema Reference

MakeGPT generates blueprints compliant with Make.com JSON Schema 2.1:

```json
{
  "name": "My Scenario",
  "flow": [
    {
      "id": 1,
      "module": "google-forms:watchResponses",
      "version": 1,
      "parameters": {},
      "mapper": {},
      "metadata": {
        "designer": {
          "x": 0,
          "y": 0
        }
      }
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": false,
      "sequential": false,
      "confidential": false,
      "dataloss": false,
      "dlq": false
    }
  }
}
```

---

## 🔐 Security Considerations

1. **API Tokens**: Never commit tokens to git - use `.env` file
2. **OAuth2 Flow**: User authentication handled client-side
3. **Connection IDs (IMTCONN)**: Require user interaction for linking
4. **Data Privacy**: No user data stored; processed in-memory only

---

## 🏗️ Implementation Architecture

### The Compiler Analogy

MakeGPT is designed as a **compiler**, not just a JSON generator:

```
Source Code  →  Lexer/Parser  →  AST Generator  →  Code Gen  →  Object File  →  Linker
     ↓              ↓                 ↓              ↓             ↓            ↓
Natural      Intent           Scenario         Blueprint    Unlinked       User
Language     Parser           Planner          Synthesizer  Scenario       (HIL)
```

**Components**:
- **Lexer/Parser** (`intent_parser.py`): Tokenizes natural language into structured intent
- **AST Generator** (`planner.py`): Creates abstract scenario plan (execution graph)
- **Code Generator** (`synthesizer.py`): Compiles AST to blueprint.json (DSL)
- **Object File**: Valid but unlinked blueprint (contains `__IMTCONN__` placeholders)
- **Linker**: Human user manually connects accounts in Make.com UI

### Critical Implementation Details

**1. Base64 Encoding Protocol** (Section 4.2 of spec)
```python
# This is REQUIRED - not documented officially but essential
blueprint_b64 = Base64Encoder.encode(blueprint_dict)
# Bypasses all JSON escaping issues
```

**2. Schema Compliance** (Table 2.1 of spec)
- Reverse-engineered from community research
- Every module MUST have: `id`, `module`, `version`, `metadata.designer`
- Root MUST have: `name`, `flow`, `metadata.scenario`
- Validated before API transmission

**3. Human-in-the-Loop (HIL)** Architecture
- `__IMTCONN__` placeholders cannot be resolved programmatically
- Security feature, not a bug
- User must manually link connections in Make.com UI
- This is an intentional design constraint

### Theoretical Foundation

Based on the comprehensive architecture specification document, this implementation follows:

**SYNTHOS_∞.Π | ATAOV± Framework**:
- **P-collapse**: Blueprint → Scenario (potential → instantiated)
- **Δ-Engine**: Gap detection and knowledge discovery
- **ATAOV±**: Generate-and-refute validation loops
- **DSL Recognition**: blueprint.json as domain-specific language

**Key Insights**:
1. Blueprint is not just data - it's executable code (DSL)
2. Community knowledge > official docs (Base64 discovery)
3. Security constraints shape architecture (HIL requirement)
4. Feedback loops enable continuous improvement (Section 7.3)

---

## 🗺️ Roadmap

- [x] Core architecture design
- [x] SRS documentation (based on comprehensive spec)
- [x] Intent parser implementation
- [x] Scenario planner
- [x] Blueprint synthesizer
- [x] Schema validator
- [x] Make.com API integration (with Base64 encoding)
- [x] CLI interface
- [x] RAG knowledge base (example blueprints)
- [x] Formal JSON Schema 2.1 (reverse-engineered)
- [x] Test suite (validator, encoder)
- [ ] RAG retrieval integration (future enhancement)
- [ ] Web UI (stretch goal)
- [ ] VSCode extension (future)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Make.com API documentation
- OpenAI for GPT models
- Community contributors and testers

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/makegpt/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/makegpt/discussions)
- **Email**: your.email@example.com

---

## 📖 Additional Resources

- [Make.com API Documentation](https://www.make.com/en/api-documentation)
- [Blueprint Schema Specification](https://www.make.com/en/api-documentation/scenarios-blueprints)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

**Built with ❤️ for the Make.com automation community**
