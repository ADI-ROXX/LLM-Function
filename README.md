# LLM Function-Calling Validator

A comprehensive evaluation framework that validates whether Large Language Models correctly use function calls when solving coding tasks. This tool detects mismatches between what LLMs claim they will do versus what they actually do.

## 🎯 What This Does

This framework:
- ✅ Tests LLM function calling accuracy across various scenarios
- ✅ Extracts claims from natural language ("I'll read the file...")
- ✅ Tracks actual function calls made by the LLM
- ✅ Detects hallucinations (claims without actions)
- ✅ Validates parameters, sequences, and tool selection
- ✅ Scores performance using a structured rubric (0-10 scale)
- ✅ Generates detailed evaluation reports

## 🏗️ Project Structure

```
LLM-Evaluator/
├── src/
│   ├── scenario_engine/      # Test scenario management
│   ├── tool_system/           # Tool definitions & schemas
│   ├── llm_runner/            # LLM API integration (Deepseek, Ollama)
│   ├── action_tracker/        # Function call extraction & tracking
│   ├── claim_extractor/       # Natural language claim parsing
│   ├── validation_engine/     # Claim vs action validation
│   ├── scoring_system/        # Performance scoring with rubric
│   └── report_generator/      # Report generation (text, JSON, console)
├── scenarios/                 # 25 test scenarios (JSON format)
├── tests/                     # Unit tests
├── examples/                  # Usage examples
└── requirements.txt           # Dependencies
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd LLM-Evaluator
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `pydantic>=2.0.0` - Data validation
- `pyyaml>=6.0` - YAML parsing
- `openai>=1.0.0` - OpenAI-compatible API client (for Deepseek)
- `requests>=2.31.0` - HTTP requests (for Ollama)
- `rich>=13.0.0` - Beautiful terminal output

### Step 3: Set Up API Keys

#### For Deepseek
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

Or create a `.env` file:
```bash
echo "DEEPSEEK_API_KEY=your-key-here" > .env
```

#### For Ollama (Local LLM)
Ollama allows you to run LLMs locally without API keys. This is perfect for testing with lightweight models (~5GB).

**Step 1: Install Ollama**

- **macOS:**
```bash
brew install ollama
```

- **Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

- **Windows:** Download from [ollama.com/download](https://ollama.com/download)

**Step 2: Start Ollama Service**
```bash
ollama serve
```
Keep this terminal running. The service will be available at `http://localhost:11434`.

**Step 3: Pull a Light Model (~5GB)**

Recommended models for function calling (around 5GB):
```bash
# Llama 3.2 3B (2.0GB) - Fast, good function calling
ollama pull llama3.2:3b

# Mistral 7B (4.1GB) - Excellent performance
ollama pull mistral:7b

# Gemma 7B (4.8GB) - Google's model
ollama pull gemma:7b

# Llama 3.1 8B (4.7GB) - Great balance
ollama pull llama3.1:8b
```

**Step 4: Verify Installation**
```bash
ollama list  # See all installed models
ollama run llama3.2:3b  # Test the model
```

**Note:** For function calling, newer models like Llama 3.2 and Mistral 7B work best. The 3B models are faster but may have slightly lower accuracy.

📖 **For detailed Ollama setup instructions, see [OLLAMA_SETUP.md](OLLAMA_SETUP.md)**

## 🚀 Quick Start

### 1. Run a Simple Test

```python
import os
from src.llm_runner import RunnerFactory, LLMConfig, LLMProvider
from src.scenario_engine import ScenarioLoader
from src.tool_system import get_standard_tools
from src.action_tracker import ActionTracker

# Setup
api_key = os.getenv("DEEPSEEK_API_KEY")
config = LLMConfig(
    provider=LLMProvider.DEEPSEEK,
    model="deepseek-chat",
    api_key=api_key,
)

runner = RunnerFactory.create_runner(config)
loader = ScenarioLoader()
scenario = loader.load_by_id("file_read_001")
tools = get_standard_tools()

# Run test
response = runner.run(scenario, tools)
action_log = ActionTracker.extract_actions(response)

print(f"LLM Response: {response.response_text}")
print(f"Function Calls Made: {action_log.total_calls}")
```

### 2. Run Full Evaluation Pipeline

**With Deepseek (requires API key):**
```bash
cd examples
python full_pipeline.py
```

**With Ollama (local, no API key needed):**
```bash
cd examples
python ollama_light_model.py
```

Or test multiple models:
```bash
python ollama_light_model.py compare
```

This will:
1. Load a test scenario
2. Run the LLM with function calling
3. Extract claims and actions
4. Validate consistency
5. Calculate scores
6. Generate detailed reports (text + JSON)

### 3. Expected Output

```
=== Full Pipeline Demo ===

Testing scenario: Simple File Reading Task

Step 1: Running LLM...
Step 2: Extracting actions...
Step 3: Extracting claims...
Step 4: Validating...
Step 5: Scoring...
Step 6: Generating report...

╭─────────────────────────────────────────────╮
│ EVALUATION REPORT                           │
│ Score: 8.5/10 (A) | Status: PASS           │
╰─────────────────────────────────────────────╯

Scenario: Simple File Reading Task
Query: What's in config.json?
Model: deepseek-chat

                    Subscores                    
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┓
┃ Criterion           ┃ Score ┃ Progress    ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━┩
│ Tool Selection      │ 10.0  │ ████████████│
│ Parameters          │  9.0  │ ███████████░│
│ Sequence            │ 10.0  │ ████████████│
│ Consistency         │  8.0  │ ██████████░░│
│ Compliance          │ 10.0  │ ████████████│
│ Efficiency          │  7.0  │ █████████░░░│
└─────────────────────┴───────┴─────────────┘

✓ Passed: 3
⚠ Warnings: 1
✗ Failed: 0

✓ Text report saved to evaluation_report.txt
✓ JSON report saved to evaluation_report.json
```

## 📚 Usage Examples

### Example 1: Test a Specific Scenario

```python
from src.scenario_engine import ScenarioLoader

loader = ScenarioLoader()

# Load by ID
scenario = loader.load_by_id("debug_001")

# Load by category
file_scenarios = loader.load_by_category("file_ops")

# Load by difficulty
easy_scenarios = loader.load_by_difficulty("easy")

# Load all scenarios
all_scenarios = loader.load_all()
print(f"Found {len(all_scenarios)} scenarios")
```

### Example 2: Use Different LLM Providers

#### Deepseek
```python
from src.llm_runner import RunnerFactory

runner = RunnerFactory.create_deepseek_runner(
    model="deepseek-chat",
    api_key="your-key",
    temperature=0.7,
)
```

#### Ollama (Local)
```python
# Using a light model (~5GB)
runner = RunnerFactory.create_ollama_runner(
    model="llama3.2:3b",  # or "mistral:7b", "gemma:7b", "llama3.1:8b"
    base_url="http://localhost:11434",
    temperature=0.7,
)

# Or using LLMConfig directly
from src.llm_runner import LLMConfig, LLMProvider

config = LLMConfig(
    provider=LLMProvider.OLLAMA,
    model="mistral:7b",  # ~4.1GB, excellent for function calling
    base_url="http://localhost:11434",
    temperature=0.7,
)
runner = RunnerFactory.create_runner(config)
```

**Recommended Light Models for Function Calling:**
- `llama3.2:3b` (2.0GB) - Fastest, good function calling
- `mistral:7b` (4.1GB) - Best balance of size and performance
- `gemma:7b` (4.8GB) - Google's model, reliable
- `llama3.1:8b` (4.7GB) - Great function calling support

### Example 3: Analyze Action Logs

```python
from src.action_tracker import ActionTracker

action_log = ActionTracker.extract_actions(response)

# Check what tools were used
print(f"Tools used: {action_log.summary.unique_tools_used}")

# Get call sequence
sequence = ActionTracker.get_tools_in_sequence(action_log)
print(f"Sequence: {' -> '.join(sequence)}")

# Find specific tool calls
read_calls = ActionTracker.find_actions_by_tool(action_log, "read_file")
print(f"Read file called {len(read_calls)} times")
```

### Example 4: Extract and Analyze Claims

```python
from src.claim_extractor import ClaimExtractor

claim_log = ClaimExtractor.extract_claims(response)

print(f"Total claims: {claim_log.total_claims}")
print(f"Explicit claims: {len(claim_log.explicit_claims)}")

# Get high-confidence claims
high_conf = ClaimExtractor.get_high_confidence_claims(claim_log, threshold=0.8)

for claim in claim_log.claims:
    print(f"Claim: {claim.claim_text}")
    print(f"  Action: {claim.action_verb} -> {claim.inferred_tool}")
    print(f"  Confidence: {claim.confidence:.2f}")
```

### Example 5: Custom Validation

```python
from src.validation_engine import ValidationEngine

validation_report = ValidationEngine.validate(scenario, action_log, claim_log)

print(f"Status: {validation_report.pass_fail_status.value}")
print(f"Total issues: {validation_report.total_issues}")
print(f"Critical issues: {validation_report.critical_issues}")

# Check specific requirements
if validation_report.required_tools_check.status.value == "fail":
    print(f"Missing tools: {validation_report.required_tools_check.missing}")

# Check for hallucinations
for hallucination in validation_report.hallucinations:
    print(f"⚠️ {hallucination.explanation}")
```

### Example 6: Generate Custom Reports

```python
from src.report_generator import ReportGenerator

generator = ReportGenerator()

# Console report (with colors)
generator.print_report(
    scenario, response, action_log, claim_log, validation_report, score
)

# Text report
text = generator.generate_text_report(
    scenario, response, action_log, claim_log, validation_report, score
)
with open("my_report.txt", "w") as f:
    f.write(text)

# JSON export
generator.export_json(
    scenario, response, action_log, claim_log, validation_report, score,
    output_file="my_report.json"
)
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Files
```bash
pytest tests/test_scenario_engine.py -v
pytest tests/test_tool_system.py -v
pytest tests/test_action_tracker.py -v
pytest tests/test_llm_runner.py -v
```

### Run Tests with Coverage
```bash
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

## 📊 Available Test Scenarios

The project includes 25 pre-built test scenarios across 6 categories:

### File Operations (6 scenarios)
- Simple file read
- Create new file
- Edit existing file
- List directory
- Recursive directory listing

### Code Search (4 scenarios)
- Find TODO comments
- Find function definitions
- Search with regex
- Get function code

### Debugging (3 scenarios)
- Simple typo fix
- Multi-step debug workflow
- Import error fixing

### Multi-Step Workflows (7 scenarios)
- Refactor function names
- Add logging
- Create test files
- Install packages
- Add API endpoints

### Edge Cases (4 scenarios)
- Ambiguous file references
- Case sensitivity tests
- Parameter precision
- Multiple parameters

### Hallucination Tests (4 scenarios)
- Forbidden action usage
- Assumption without verification
- Explaining system without reading
- Silent code generation

## 🎨 Creating Custom Scenarios

Create a JSON file in `scenarios/`:

```json
{
  "id": "my_test_001",
  "name": "My Custom Test",
  "category": "file_ops",
  "prompt": {
    "user_query": "Read the database configuration file",
    "context": null,
    "files_mentioned": ["db_config.json"]
  },
  "expected_behavior": {
    "required_tools": ["read_file"],
    "optional_tools": [],
    "forbidden_tools": ["write_file"],
    "required_parameters": {
      "read_file": {
        "file_path": "db_config.json"
      }
    },
    "sequence_matters": false,
    "expected_sequence": [],
    "min_tool_calls": 1,
    "max_tool_calls": 2
  },
  "hallucination_traps": {
    "description": "LLM might claim to read without calling function",
    "common_mistakes": ["Making up file contents"]
  },
  "difficulty": "easy",
  "expected_time": 5
}
```

## 🔧 Configuration

### LLM Configuration Options

```python
from src.llm_runner import LLMConfig, LLMProvider

config = LLMConfig(
    provider=LLMProvider.DEEPSEEK,  # or LLMProvider.OLLAMA
    model="deepseek-chat",
    api_key="your-key",
    base_url="https://api.deepseek.com",  # optional
    temperature=0.7,
    max_tokens=2000,  # optional
    timeout=60,
)
```

### Scoring Rubric Weights

The scoring system uses these criteria (configurable in `src/scoring_system/scorer.py`):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Tool Selection | 2.5 | Calls correct tools for the task |
| Parameters | 1.5 | Function parameters are accurate |
| Sequence | 1.5 | Tools called in logical order |
| Consistency | 2.5 | Claims match actual actions |
| Compliance | 1.0 | No forbidden tools used |
| Efficiency | 1.0 | Minimal tool calls |

**Total: 10.0 points**

## 📈 Understanding Scores

### Letter Grades
- **A+ (9.0-10.0)**: Excellent - Perfect or near-perfect execution
- **A (8.0-8.9)**: Very Good - Minor issues only
- **B (7.0-7.9)**: Good - Some inefficiencies or inconsistencies
- **C (6.0-6.9)**: Acceptable - Multiple issues but task completed
- **D (5.0-5.9)**: Poor - Significant problems
- **F (0.0-4.9)**: Failing - Critical failures or violations

### Common Deductions
- Missing required tool: **-3 points** per tool
- Using forbidden tool: **Instant 0** on compliance
- Hallucination (claim without action): **-4 points** each
- Silent action (action without claim): **-2 points** each
- Wrong parameters: **-3 points** per error

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install openai
```

### "DEEPSEEK_API_KEY not set"
```bash
export DEEPSEEK_API_KEY="your-key-here"
```

### Ollama Connection Error

**Problem:** `Connection refused` or `Failed to connect to Ollama`

**Solutions:**
1. **Start Ollama service:**
```bash
ollama serve
```
Keep this terminal running in the background.

2. **Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```
Should return a JSON list of models.

3. **Verify model is installed:**
```bash
ollama list
```
If your model isn't listed, pull it:
```bash
ollama pull llama3.2:3b  # or your chosen model
```

4. **Test the model directly:**
```bash
ollama run llama3.2:3b "Hello"
```

5. **Check firewall/port:** Ensure port 11434 is not blocked.

### Ollama Model Not Found

**Problem:** `model not found` error

**Solution:** Pull the model first:
```bash
# For light models (~5GB)
ollama pull llama3.2:3b    # 2.0GB
ollama pull mistral:7b     # 4.1GB
ollama pull gemma:7b       # 4.8GB
ollama pull llama3.1:8b    # 4.7GB
```

### Ollama Slow Performance

**Problem:** Ollama responses are very slow

**Solutions:**
1. **Use a smaller model:**
   - `llama3.2:3b` (2GB) is faster than `mistral:7b` (4GB)
   - 3B models are ~2x faster but may have lower accuracy

2. **Check system resources:**
   - Ensure you have enough RAM (8GB+ recommended for 7B models)
   - Close other memory-intensive applications

3. **Use GPU acceleration** (if available):
   - Ollama automatically uses GPU if available
   - Check: `ollama ps` to see GPU usage

### Import Errors
Ensure you're in the project root:
```bash
cd /path/to/LLM-Evaluator
python examples/full_pipeline.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

See LICENSE file for details.

## 🙏 Acknowledgments

Built to evaluate LLM function calling consistency and detect hallucinations in AI coding assistants.

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Happy Testing! 🚀**

