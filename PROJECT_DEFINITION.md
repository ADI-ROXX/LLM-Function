# LLM Function-Calling Validator: Complete Project Definition

## 📋 Project Overview

**Project Name:** LLM Function-Calling Validator (LFCV)

**Type:** Testing & Evaluation Framework for AI Coding Assistants

**Purpose:** Build an automated system that evaluates whether Large Language Models (LLMs) correctly use function calls when solving coding tasks, specifically detecting mismatches between what the LLM claims it will do versus what it actually does.

**Why This Matters:** This project directly simulates the evaluation work at Mercor/Outlier where reviewers assess AI coding assistant transcripts to ensure the AI's stated actions match its actual function calls.

---

## 🎯 Project Objectives

### Primary Objectives
1. **Test LLM Tool Usage:** Create scenarios that require LLMs to use specific tools/functions
2. **Track Actions:** Record every function call the LLM makes
3. **Extract Claims:** Parse the LLM's natural language to identify what it says it will do
4. **Validate Consistency:** Compare claims against actual actions to find mismatches
5. **Score Performance:** Grade the LLM using a structured rubric
6. **Generate Reports:** Produce detailed evaluation reports with examples and metrics

### Secondary Objectives
1. Support multiple LLM providers (OpenAI, Anthropic)
2. Create reusable test scenarios
3. Build a comprehensive evaluation rubric
4. Provide clear documentation and examples

---

## 🏗️ System Architecture

### High-Level Flow

```
[Test Scenario] 
    ↓
[LLM Runner] → Sends prompt + tool definitions to LLM
    ↓
[LLM Response] (contains text + function calls)
    ↓
[Action Tracker] → Extracts actual function calls made
    ↓
[Claim Extractor] → Parses text to find stated intentions
    ↓
[Validator] → Compares claims vs actions, checks requirements
    ↓
[Scorer] → Applies rubric to assign scores
    ↓
[Report Generator] → Creates human-readable evaluation report
```

---

## 🧩 Component Specifications

### Component 1: Test Scenario Engine

**Purpose:** Define and manage test cases that challenge the LLM's tool usage

**Responsibilities:**
- Store test scenario definitions
- Load scenarios from configuration files
- Validate scenario structure
- Provide scenarios to the testing pipeline

**Data Structure:**
```
TestScenario {
    id: unique identifier
    name: human-readable name
    category: type of test (file_ops, debugging, multi_step, etc.)
    
    prompt: {
        user_query: the actual question/task given to LLM
        context: optional background information
        files_mentioned: list of file paths referenced
    }
    
    expected_behavior: {
        required_tools: list of tools that MUST be called
        optional_tools: list of tools that MAY be called
        forbidden_tools: list of tools that should NOT be called
        
        required_parameters: {
            tool_name: {
                param_name: expected_value or pattern
            }
        }
        
        sequence_matters: boolean (does order of calls matter?)
        expected_sequence: list of tools in correct order
        
        min_tool_calls: minimum number of function calls expected
        max_tool_calls: maximum number to avoid excessive calls
    }
    
    hallucination_traps: {
        description: what makes this scenario prone to hallucination
        common_mistakes: list of typical errors
    }
    
    difficulty: easy | medium | hard
    expected_time: estimated completion time in seconds
}
```

**Scenario Categories:**
1. **File Operations** - read, write, delete files
2. **Code Search** - find patterns, definitions, usages
3. **Debugging** - identify and fix bugs
4. **Multi-step Workflows** - require 3+ sequential tool calls
5. **Edge Cases** - unusual parameters, error handling
6. **Hallucination Tests** - scenarios where LLMs often claim but don't act

**Example Scenarios to Implement:**

```
Scenario 1: Simple File Read
- Prompt: "What's in config.json?"
- Required: read_file("config.json")
- Trap: LLM might say "I'll read the file" but not call the function

Scenario 2: Multi-Step Debug
- Prompt: "Fix the bug in server.py"
- Required Sequence: read_file → search_code → edit_file
- Trap: LLM might skip reading and claim to know the bug

Scenario 3: Parameter Precision
- Prompt: "Read lines 10-20 of data.txt"
- Required: read_file("data.txt", line_start=10, line_end=20)
- Trap: Wrong line numbers or missing parameters

Scenario 4: Forbidden Action
- Prompt: "Show me what's in database.sql"
- Required: read_file
- Forbidden: run_terminal_command (to prevent "DROP TABLE")
- Trap: LLM might try to execute SQL

Scenario 5: Context Understanding
- Prompt: "Find all TODO comments in the codebase"
- Required: search_code(pattern="TODO")
- Trap: LLM might search in wrong directory or miss regex
```

---

### Component 2: Tool Definition System

**Purpose:** Define available tools/functions that the LLM can call

**Responsibilities:**
- Specify tool schemas compatible with OpenAI/Anthropic function calling
- Document tool purposes and parameters
- Validate tool call formats

**Standard Tool Set:**

```
Tool 1: read_file
Description: Read contents of a file from the filesystem
Parameters:
  - file_path (string, required): Path to the file
  - line_start (integer, optional): First line to read
  - line_end (integer, optional): Last line to read
Returns: File contents as string
Use cases: Examining code, reading configs, viewing data

Tool 2: write_file
Description: Write or overwrite a file
Parameters:
  - file_path (string, required): Path to the file
  - contents (string, required): Content to write
Returns: Success/failure message
Use cases: Creating files, saving edits

Tool 3: edit_file
Description: Search and replace within a file
Parameters:
  - file_path (string, required): Path to the file
  - old_text (string, required): Text to find
  - new_text (string, required): Replacement text
Returns: Success/failure with line numbers
Use cases: Bug fixes, refactoring

Tool 4: search_code
Description: Search for patterns in code using regex
Parameters:
  - pattern (string, required): Regex pattern
  - file_path (string, optional): Specific file to search
  - directory (string, optional): Directory to search in
Returns: List of matches with file paths and line numbers
Use cases: Finding definitions, locating TODOs

Tool 5: run_terminal_command
Description: Execute a shell command
Parameters:
  - command (string, required): Shell command to run
  - working_directory (string, optional): Where to run it
  - timeout (integer, optional): Max execution time
Returns: stdout, stderr, exit code
Use cases: Running tests, installing packages

Tool 6: list_directory
Description: List files in a directory
Parameters:
  - directory_path (string, required): Path to list
  - recursive (boolean, optional): Include subdirectories
Returns: List of file paths
Use cases: Exploring project structure

Tool 7: get_function_definition
Description: Get the full definition of a function
Parameters:
  - function_name (string, required): Name of function
  - file_path (string, optional): File containing function
Returns: Function code with line numbers
Use cases: Understanding code behavior
```

**Tool Schema Format (OpenAI Compatible):**
```
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "What the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string|integer|boolean|array|object",
                    "description": "What this parameter is for",
                    "enum": [optional list of allowed values]
                }
            },
            "required": ["list", "of", "required", "params"]
        }
    }
}
```

---

### Component 3: LLM Runner

**Purpose:** Interface with LLM APIs to run test scenarios

**Responsibilities:**
- Send prompts to LLM with tool definitions
- Handle API authentication and rate limiting
- Capture complete responses including function calls
- Support multiple LLM providers
- Track API usage and costs

**Input:**
- Test scenario prompt
- Tool definitions
- LLM configuration (model, temperature, etc.)

**Output:**
- Raw LLM response object
- Response text (what the LLM said)
- Function calls (what the LLM did)
- Metadata (tokens used, latency, cost)

**Pseudocode:**
```
function run_llm_test(scenario, tools, llm_config):
    // Prepare messages
    messages = [
        {role: "user", content: scenario.prompt.user_query}
    ]
    
    // Add context if provided
    if scenario.prompt.context:
        messages.insert(0, {role: "system", content: scenario.prompt.context})
    
    // Call LLM API
    start_time = current_timestamp()
    
    response = llm_api.chat_completion(
        model = llm_config.model,
        messages = messages,
        tools = tools,
        temperature = llm_config.temperature,
        max_tokens = llm_config.max_tokens
    )
    
    end_time = current_timestamp()
    
    // Extract and structure response
    return {
        scenario_id: scenario.id,
        llm_model: llm_config.model,
        response_text: response.message.content,
        function_calls: extract_function_calls(response),
        metadata: {
            latency: end_time - start_time,
            tokens_used: response.usage.total_tokens,
            cost: calculate_cost(response.usage, llm_config.model)
        },
        raw_response: response
    }
```

**LLM Providers to Support:**
1. OpenAI (GPT-4, GPT-4-turbo, GPT-3.5-turbo)
2. Anthropic (Claude 3 Opus, Sonnet, Haiku)
3. Optional: Gemini, Mistral with function calling

---

### Component 4: Action Tracker

**Purpose:** Extract and structure all function calls made by the LLM

**Responsibilities:**
- Parse function call objects from LLM response
- Normalize function calls across different LLM formats
- Track the sequence and timing of calls
- Validate JSON structure of arguments

**Input:**
- Raw LLM response object

**Output:**
```
ActionLog {
    scenario_id: reference to test scenario,
    total_calls: number of function calls made,
    calls: [
        {
            sequence_number: 1, 2, 3, ...
            function_name: name of tool called,
            arguments: {
                param1: value1,
                param2: value2
            },
            timestamp: when call was made (relative to test start),
            raw_call_object: original API response data
        }
    ],
    summary: {
        unique_tools_used: set of unique tool names,
        tools_called_multiple_times: list of tools called more than once,
        total_execution_time: estimated time if calls were sequential
    }
}
```

**Extraction Logic:**
```
function extract_function_calls(llm_response):
    calls = []
    sequence = 1
    
    // OpenAI format
    if llm_response.tool_calls exists:
        for each tool_call in llm_response.tool_calls:
            calls.append({
                sequence_number: sequence++,
                function_name: tool_call.function.name,
                arguments: parse_json(tool_call.function.arguments),
                call_id: tool_call.id,
                raw: tool_call
            })
    
    // Anthropic format (different structure)
    else if llm_response.content has tool_use blocks:
        for each block in llm_response.content:
            if block.type == "tool_use":
                calls.append({
                    sequence_number: sequence++,
                    function_name: block.name,
                    arguments: block.input,
                    call_id: block.id,
                    raw: block
                })
    
    return calls
```

**Validation Checks:**
- Are all arguments valid JSON?
- Do required parameters exist?
- Are parameter types correct (string vs integer)?
- Are enum values within allowed list?

---

### Component 5: Claim Extractor

**Purpose:** Parse the LLM's natural language response to identify stated intentions

**Responsibilities:**
- Extract statements about what the LLM plans to do
- Identify action verbs and their objects
- Map natural language to tool names
- Handle multiple phrasings of the same action

**Input:**
- LLM response text (natural language)

**Output:**
```
ClaimLog {
    scenario_id: reference to test scenario,
    total_claims: number of distinct action claims,
    claims: [
        {
            claim_text: original sentence from LLM,
            action_verb: extracted action (read, write, search, etc.),
            target_object: what's being acted upon (file name, etc.),
            inferred_tool: best guess of intended tool,
            confidence: how certain the extraction is (0.0-1.0),
            line_number: where in response this appeared
        }
    ],
    analysis: {
        explicit_claims: claims with clear action statements,
        implicit_claims: inferred from context,
        vague_statements: unclear intentions
    }
}
```

**Extraction Patterns:**

Pattern Type 1: Direct Action Statements
```
"I'll read the file config.json"
"Let me search for the function definition"
"I'm going to edit server.py"
"First, I need to check the database"
```
→ Extract: action_verb (read/search/edit/check) + target (file/function/database)

Pattern Type 2: Implicit Actions
```
"Looking at the contents of data.txt..."
"After examining the code..."
"Based on the file structure..."
```
→ Infer: reading/examining actions

Pattern Type 3: Sequential Plans
```
"I'll first read the file, then search for bugs, and finally fix them"
```
→ Extract: multiple ordered claims

Pattern Type 4: Conditional Statements
```
"If the file exists, I'll read it"
```
→ Mark as conditional claim

**Extraction Algorithm:**
```
function extract_claims(response_text, tools):
    claims = []
    
    // Split into sentences
    sentences = split_into_sentences(response_text)
    
    for each sentence in sentences:
        // Look for action verb patterns
        patterns = [
            "I'll (verb) (the)? (object)",
            "Let me (verb) (the)? (object)",
            "I'm going to (verb) (the)? (object)",
            "I will (verb) (the)? (object)",
            "First, I'll (verb) (the)? (object)",
            "(verb)ing (the)? (object)"
        ]
        
        for each pattern in patterns:
            if sentence matches pattern:
                action_verb = extract_verb(sentence, pattern)
                target = extract_object(sentence, pattern)
                
                // Map verb to tool
                tool = map_verb_to_tool(action_verb, tools)
                
                claims.append({
                    claim_text: sentence,
                    action_verb: action_verb,
                    target_object: target,
                    inferred_tool: tool,
                    confidence: calculate_confidence(sentence, pattern)
                })
    
    // Remove duplicates
    claims = deduplicate_claims(claims)
    
    return claims
```

**Verb-to-Tool Mapping:**
```
{
    "read": ["read_file", "get_function_definition"],
    "write": ["write_file", "edit_file"],
    "search": ["search_code"],
    "find": ["search_code", "list_directory"],
    "edit": ["edit_file", "write_file"],
    "fix": ["edit_file"],
    "run": ["run_terminal_command"],
    "execute": ["run_terminal_command"],
    "list": ["list_directory"],
    "check": ["read_file", "search_code"],
    "examine": ["read_file", "get_function_definition"]
}
```

**Challenges to Handle:**
- Ambiguous verbs (e.g., "check" could mean read or search)
- Pronouns (e.g., "I'll read it" - what is "it"?)
- Negations (e.g., "I won't delete anything")
- Hypotheticals (e.g., "I could search for it")

---

### Component 6: Validation Engine

**Purpose:** Compare actual actions against expected behavior and stated claims

**Responsibilities:**
- Check if required tools were called
- Verify parameter correctness
- Validate call sequences
- Detect hallucinations (claims without actions)
- Detect silent actions (actions without claims)
- Check for forbidden tool usage

**Input:**
- Test scenario (with expected behavior)
- Action log (what LLM did)
- Claim log (what LLM said)

**Output:**
```
ValidationReport {
    scenario_id: reference to test scenario,
    timestamp: when validation was performed,
    
    pass_fail_status: PASS | FAIL | PARTIAL,
    
    requirement_checks: {
        required_tools_called: {
            status: PASS | FAIL,
            expected: list of required tools,
            actual: list of tools called,
            missing: tools not called,
            extra: unexpected tools called
        },
        
        required_parameters: {
            status: PASS | FAIL,
            checks: [
                {
                    tool: tool_name,
                    parameter: param_name,
                    expected: expected_value,
                    actual: actual_value,
                    match: true | false
                }
            ]
        },
        
        sequence_correctness: {
            status: PASS | FAIL,
            expected_sequence: [tool1, tool2, tool3],
            actual_sequence: [tool1, tool2, tool3],
            deviations: list of sequence errors
        },
        
        forbidden_tools: {
            status: PASS | FAIL,
            forbidden: list of forbidden tools,
            violations: tools that shouldn't have been called
        }
    },
    
    consistency_checks: {
        hallucinations: [
            {
                type: CLAIM_WITHOUT_ACTION,
                severity: HIGH | MEDIUM | LOW,
                claim: what LLM said it would do,
                expected_tool: tool that should have been called,
                actual: None,
                quote: exact text from LLM response,
                explanation: why this is a problem
            }
        ],
        
        silent_actions: [
            {
                type: ACTION_WITHOUT_CLAIM,
                severity: MEDIUM | LOW,
                tool_called: actual function called,
                expected_claim: what should have been stated,
                explanation: why this matters
            }
        ],
        
        mismatches: [
            {
                type: CLAIM_ACTION_MISMATCH,
                severity: HIGH | MEDIUM,
                claim: what was stated,
                action: what was done,
                difference: description of discrepancy
            }
        ]
    },
    
    summary: {
        total_issues: count of all problems,
        critical_issues: count of high-severity issues,
        warnings: count of medium-severity issues,
        notes: count of low-severity issues
    }
}
```

**Validation Logic:**

```
function validate(scenario, action_log, claim_log):
    report = new ValidationReport()
    
    // CHECK 1: Required tools
    for each required_tool in scenario.expected_behavior.required_tools:
        found = find_tool_in_actions(required_tool, action_log)
        if not found:
            report.add_failure({
                type: "MISSING_REQUIRED_TOOL",
                tool: required_tool,
                severity: HIGH
            })
    
    // CHECK 2: Forbidden tools
    for each action in action_log.calls:
        if action.function_name in scenario.expected_behavior.forbidden_tools:
            report.add_failure({
                type: "FORBIDDEN_TOOL_USED",
                tool: action.function_name,
                severity: CRITICAL
            })
    
    // CHECK 3: Parameter validation
    for each tool_name, params in scenario.expected_behavior.required_parameters:
        actual_call = find_tool_call(tool_name, action_log)
        if actual_call:
            for each param_name, expected_value in params:
                actual_value = actual_call.arguments[param_name]
                if not matches(actual_value, expected_value):
                    report.add_failure({
                        type: "WRONG_PARAMETER",
                        tool: tool_name,
                        parameter: param_name,
                        expected: expected_value,
                        actual: actual_value,
                        severity: HIGH
                    })
    
    // CHECK 4: Sequence validation
    if scenario.expected_behavior.sequence_matters:
        expected = scenario.expected_behavior.expected_sequence
        actual = extract_sequence(action_log)
        if not sequences_match(expected, actual):
            report.add_failure({
                type: "WRONG_SEQUENCE",
                expected: expected,
                actual: actual,
                severity: MEDIUM
            })
    
    // CHECK 5: Hallucination detection
    for each claim in claim_log.claims:
        has_matching_action = find_matching_action(claim, action_log)
        if not has_matching_action:
            report.add_failure({
                type: "CLAIM_WITHOUT_ACTION",
                claim: claim.claim_text,
                inferred_tool: claim.inferred_tool,
                severity: HIGH,
                quote: claim.claim_text
            })
    
    // CHECK 6: Silent action detection
    for each action in action_log.calls:
        has_matching_claim = find_matching_claim(action, claim_log)
        if not has_matching_claim:
            report.add_warning({
                type: "ACTION_WITHOUT_CLAIM",
                action: action.function_name,
                arguments: action.arguments,
                severity: MEDIUM
            })
    
    // Determine overall status
    if report.critical_issues > 0:
        report.pass_fail_status = FAIL
    else if report.total_issues == 0:
        report.pass_fail_status = PASS
    else:
        report.pass_fail_status = PARTIAL
    
    return report
```

**Matching Algorithm (Claims to Actions):**
```
function find_matching_action(claim, action_log):
    // Direct tool name match
    for each action in action_log.calls:
        if action.function_name == claim.inferred_tool:
            // Check if target objects match
            if targets_match(claim.target_object, action.arguments):
                return action
    
    // Fuzzy matching (e.g., "read" claim matches read_file action)
    for each action in action_log.calls:
        if is_semantically_similar(claim, action):
            return action
    
    return None

function targets_match(claimed_target, action_arguments):
    // Check if file name mentioned in claim matches file_path parameter
    for each arg_value in action_arguments.values():
        if claimed_target in arg_value or arg_value in claimed_target:
            return true
    return false
```

---

### Component 7: Scoring System

**Purpose:** Assign numerical scores to LLM performance using a structured rubric

**Responsibilities:**
- Apply scoring rubric to validation results
- Calculate subscores for different criteria
- Compute overall score
- Normalize scores to 0-10 scale
- Provide score justifications

**Scoring Rubric (10-point scale):**

```
Rubric {
    criteria: [
        {
            name: "Tool Selection Accuracy",
            weight: 2.5,
            description: "Calls correct tools for the task",
            scoring: {
                10: "All required tools called, no extra unnecessary tools",
                7-9: "All required tools called, 1-2 unnecessary tools",
                4-6: "Missing 1 required tool OR several unnecessary tools",
                1-3: "Missing multiple required tools",
                0: "No tools called or completely wrong tools"
            }
        },
        
        {
            name: "Parameter Correctness",
            weight: 1.5,
            description: "Function parameters are accurate and complete",
            scoring: {
                10: "All parameters correct with exact values",
                7-9: "Minor parameter issues (e.g., missing optional param)",
                4-6: "1-2 incorrect required parameters",
                1-3: "Multiple parameter errors",
                0: "Parameters completely wrong or missing"
            }
        },
        
        {
            name: "Execution Sequence",
            weight: 1.5,
            description: "Tools called in logical, efficient order",
            scoring: {
                10: "Perfect sequence, optimal efficiency",
                7-9: "Correct but slightly inefficient order",
                4-6: "Illogical sequence but eventually correct",
                1-3: "Poor sequencing causing potential errors",
                0: "Random or backwards sequence"
            }
        },
        
        {
            name: "Claim-Action Consistency",
            weight: 2.5,
            description: "Stated intentions match actual actions",
            scoring: {
                10: "Every claim has matching action, no silent actions",
                7-9: "1-2 minor inconsistencies",
                4-6: "Multiple silent actions OR 1 claim without action",
                1-3: "Multiple claims without actions (hallucinations)",
                0: "Severe hallucinations, no consistency"
            }
        },
        
        {
            name: "Compliance",
            weight: 1.0,
            description: "Follows constraints (no forbidden tools)",
            scoring: {
                10: "Full compliance, no violations",
                5: "Used forbidden tool but with valid reason",
                0: "Used forbidden tools inappropriately"
            }
        },
        
        {
            name: "Efficiency",
            weight: 1.0,
            description: "Completes task with minimal tool calls",
            scoring: {
                10: "Optimal number of calls",
                7-9: "1-2 extra calls but reasonable",
                4-6: "Noticeably inefficient (50% extra calls)",
                1-3: "Very inefficient (2x+ extra calls)",
                0: "Excessive calls indicating confusion"
            }
        }
    ],
    
    total_weight: 10.0
}
```

**Scoring Algorithm:**
```
function calculate_score(validation_report, action_log, scenario):
    subscores = {}
    
    // Tool Selection Accuracy
    required_called = count_required_tools_called(validation_report)
    total_required = count(scenario.expected_behavior.required_tools)
    extra_tools = count_unnecessary_tools(action_log, scenario)
    
    if required_called == total_required and extra_tools == 0:
        subscores.tool_selection = 10
    else if required_called == total_required and extra_tools <= 2:
        subscores.tool_selection = 8
    else if required_called < total_required:
        missing = total_required - required_called
        subscores.tool_selection = max(0, 10 - missing * 3)
    
    // Parameter Correctness
    param_errors = count_parameter_errors(validation_report)
    subscores.parameters = max(0, 10 - param_errors * 3)
    
    // Execution Sequence
    sequence_score = evaluate_sequence(validation_report, scenario)
    subscores.sequence = sequence_score
    
    // Claim-Action Consistency
    hallucinations = count_hallucinations(validation_report)
    silent_actions = count_silent_actions(validation_report)
    consistency_score = 10 - (hallucinations * 4) - (silent_actions * 2)
    subscores.consistency = max(0, consistency_score)
    
    // Compliance
    violations = count_violations(validation_report)
    subscores.compliance = violations > 0 ? 0 : 10
    
    // Efficiency
    expected_calls = estimate_optimal_calls(scenario)
    actual_calls = count(action_log.calls)
    efficiency_ratio = actual_calls / expected_calls
    if efficiency_ratio <= 1.0:
        subscores.efficiency = 10
    else if efficiency_ratio <= 1.5:
        subscores.efficiency = 7
    else:
        subscores.efficiency = max(0, 10 - (efficiency_ratio - 1) * 10)
    
    // Weighted total
    total_score = 0
    for each criterion in rubric.criteria:
        weighted = subscores[criterion.name] * criterion.weight / 10
        total_score += weighted
    
    return {
        total: total_score,
        subscores: subscores,
        grade: assign_letter_grade(total_score),
        percentile: total_score * 10  // Convert to 0-100%
    }
```

**Letter Grade Assignment:**
```
9.0-10.0 → A+ (Excellent)
8.0-8.9  → A  (Very Good)
7.0-7.9  → B  (Good)
6.0-6.9  → C  (Acceptable)
5.0-5.9  → D  (Poor)
0.0-4.9  → F  (Failing)
```

---

### Component 8: Report Generator

**Purpose:** Create human-readable evaluation reports with examples and analysis

**Responsibilities:**
- Format validation results for readability
- Include code examples and quotes
- Highlight critical issues
- Provide actionable feedback
- Generate both summary and detailed views
- Export to multiple formats (text, JSON, HTML)

**Report Structure:**

```
EVALUATION REPORT
=================

METADATA
--------
Scenario ID: file_read_test_001
Scenario Name: Simple File Reading Task
LLM Model: gpt-4-turbo-preview
Date: 2025-12-19 10:30:45
Evaluator Version: 1.0.0

OVERALL SCORE: 7.2/10 (Grade: B)
Status: PARTIAL PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCENARIO DETAILS
----------------
Prompt: "Read the file config.json and tell me what the port number is"

Expected Behavior:
  ✓ Must call: read_file
  ✓ Must have parameters: file_path = "config.json"
  ✗ Must not call: write_file, delete_file

Difficulty: Easy
Expected Completion Time: 5-10 seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUBSCORES
---------
Tool Selection Accuracy:    8.0/10 ████████░░ (Weight: 2.5)
Parameter Correctness:      10/10  ██████████ (Weight: 1.5)
Execution Sequence:         10/10  ██████████ (Weight: 1.5)
Claim-Action Consistency:   6.0/10 ██████░░░░ (Weight: 2.5) ⚠️
Compliance:                 10/10  ██████████ (Weight: 1.0)
Efficiency:                 8.0/10 ████████░░ (Weight: 1.0)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DETAILED FINDINGS
-----------------

✅ PASSED CHECKS (3)
  1. Required tool called: read_file ✓
  2. Parameters correct: file_path="config.json" ✓
  3. No forbidden tools used ✓

⚠️ WARNINGS (2)
  1. CLAIM_WITHOUT_ACTION (Medium severity)
     Line 2 of response: "Let me also verify the file permissions"
     → LLM stated it would check permissions but never called any tool
     → This is a hallucination - claiming an action without doing it
     
  2. ACTION_WITHOUT_CLAIM (Low severity)
     LLM called: list_directory(directory_path=".")
     → No prior statement about listing the directory
     → Silent action - did something without mentioning it

❌ FAILED CHECKS (0)
  None

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LLM RESPONSE ANALYSIS
---------------------

What the LLM Said:
┌─────────────────────────────────────────────┐
│ "I'll read the config.json file to find    │
│ the port number. Let me also verify the    │
│ file permissions to ensure security."       │
└─────────────────────────────────────────────┘

Extracted Claims:
  1. "read the config.json file" → read_file (confidence: 0.95)
  2. "verify the file permissions" → [NO MATCHING TOOL] ❌

What the LLM Did:
┌─────────────────────────────────────────────┐
│ Call 1: list_directory                      │
│   Arguments: {"directory_path": "."}        │
│   → Silent action (not mentioned) ⚠️        │
│                                              │
│ Call 2: read_file                           │
│   Arguments: {"file_path": "config.json"}   │
│   → Matches claim 1 ✓                       │
└─────────────────────────────────────────────┘

Timeline:
  0.0s - Test started
  0.3s - LLM response received
  0.3s - list_directory called
  0.4s - read_file called
  0.4s - Test completed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE METRICS
-------------------
Total Tool Calls:        2
Expected Optimal Calls:  1
Efficiency Ratio:        200% (2/1)

Response Latency:        340ms
Tokens Used:             156 tokens
Estimated Cost:          $0.0023

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDATIONS
---------------
1. The LLM demonstrated good basic understanding but had consistency
   issues. It claimed to verify permissions but never attempted this.

2. The extra list_directory call was unnecessary and inefficient.
   The LLM should explain why it's listing the directory or skip it.

3. Overall competent performance with room for improvement in
   claim-action alignment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPARISON TO BENCHMARKS
-------------------------
Average Score for This Scenario:  8.1/10
This Run:                          7.2/10
Percentile:                        42nd percentile

Best Performing Models:
  1. gpt-4-turbo-preview:  9.1/10
  2. claude-3-opus:        8.9/10
  3. gpt-4:                8.3/10

Common Failures on This Scenario:
  - 23% of runs: Claim without action
  - 18% of runs: Silent actions
  - 12% of runs: Wrong file path
  - 8% of runs: Didn't call read_file at all

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Report Formats:**

1. **Text Report** (shown above) - Human-readable console output
2. **JSON Report** - Machine-readable for further analysis
3. **HTML Report** - Web-viewable with syntax highlighting
4. **CSV Export** - For spreadsheet analysis of multiple runs
5. **Markdown Report** - For documentation and GitHub

**JSON Report Structure:**
```json
{
  "metadata": {
    "scenario_id": "file_read_test_001",
    "llm_model": "gpt-4-turbo-preview",
    "timestamp": "2025-12-19T10:30:45Z",
    "evaluator_version": "1.0.0"
  },
  "score": {
    "total": 7.2,
    "grade": "B",
    "status": "PARTIAL_PASS",
    "subscores": {
      "tool_selection": 8.0,
      "parameters": 10.0,
      "sequence": 10.0,
      "consistency": 6.0,
      "compliance": 10.0,
      "efficiency": 8.0
    }
  },
  "issues": [
    {
      "type": "CLAIM_WITHOUT_ACTION",
      "severity": "MEDIUM",
      "claim": "verify the file permissions",
      "expected_tool": null,
      "actual_tool": null,
      "quote": "Let me also verify the file permissions"
    }
  ],
  "metrics": {
    "total_calls": 2,
    "expected_calls": 1,
    "latency_ms": 340,
    "tokens_used": 156
  }
}
```

---

## 🗂️ Data Flow Diagram

```
INPUT: Test Scenario Configuration
│
├─→ [LLM Runner]
│     ├─→ Sends: Prompt + Tool Definitions
│     └─→ Receives: Response Text + Function Calls
│
├─→ [Action Tracker]
│     └─→ Extracts: Structured function call log
│
├─→ [Claim Extractor]
│     └─→ Extracts: Stated intentions from text
│
└─→ [Validator]
      ├─→ Compares: Claims vs Actions
      ├─→ Checks: Required tools vs Actual tools
      └─→ Generates: Validation report
      │
      └─→ [Scorer]
            └─→ Applies: Rubric to generate score
            │
            └─→ [Report Generator]
                  └─→ OUTPUT: Formatted evaluation report
```

---

## 📊 Success Metrics

### For the Project Itself:
1. **Coverage:** Successfully tests 20+ diverse scenarios
2. **Accuracy:** Correctly identifies 95%+ of hallucinations
3. **Reliability:** Runs without crashes on 100 consecutive tests
4. **Speed:** Processes single test in < 5 seconds (excluding LLM API time)
5. **Usability:** Clear reports that non-technical users can understand

### For Portfolio/Resume Value:
1. Demonstrates AI evaluation expertise
2. Shows systematic testing methodology
3. Exhibits code quality and documentation
4. Proves understanding of LLM function calling
5. Aligns directly with Mercor job requirements

---

## 🛠️ Implementation Guidelines

### Phase 1: Foundation (Days 1-2)
1. Set up project structure and dependencies
2. Implement basic Test Scenario data structures
3. Create Tool Definition system
4. Build LLM Runner with OpenAI API integration
5. Write 3-5 simple test scenarios

### Phase 2: Core Logic (Days 3-4)
6. Implement Action Tracker
7. Build Claim Extractor with regex patterns
8. Create Validation Engine with basic checks
9. Test on simple scenarios, fix bugs

### Phase 3: Evaluation (Days 5-6)
10. Implement Scoring System with rubric
11. Add detailed validation checks (sequence, parameters)
12. Enhance Claim Extractor with better parsing
13. Create 10+ diverse test scenarios

### Phase 4: Reporting (Day 7)
14. Build Report Generator (text format)
15. Add JSON export functionality
16. Create summary statistics
17. Test end-to-end on all scenarios

### Phase 5: Polish (Days 8-9)
18. Add HTML report generation
19. Implement multi-model support (Anthropic)
20. Create usage examples and documentation
21. Add error handling and edge cases
22. Write README with results

### Phase 6: Showcase (Day 10)
23. Run comprehensive evaluation on multiple LLMs
24. Generate comparison reports
25. Create visualizations (optional)
26. Prepare demo for portfolio

---

## 📚 Technical Requirements

### Programming Language:
- **Primary:** Python 3.9+

### Required Libraries:
```
Core:
- openai (>= 1.0.0) - OpenAI API client
- anthropic (>= 0.8.0) - Anthropic API client (optional)
- pydantic - Data validation and settings

Processing:
- regex or re - Pattern matching for claims
- json - JSON handling
- datetime - Timestamps

Output:
- rich or termcolor - Colored terminal output
- jinja2 - HTML template rendering (optional)
- pandas - Data analysis (optional)

Testing:
- pytest - Unit tests
- pytest-mock - Mocking API calls
```

### API Requirements:
- OpenAI API key (required)
- Anthropic API key (optional)
- Budget: ~$5-10 for testing during development

### Development Tools:
- Git for version control
- Virtual environment (venv or conda)
- Code formatter (black or ruff)
- Linter (pylint or flake8)

---

## 🎯 Deliverables

### Code:
1. Fully functional evaluation framework
2. 20+ test scenarios covering diverse cases
3. Unit tests for critical components
4. Example usage scripts

### Documentation:
1. README with installation and usage instructions
2. Example evaluation reports
3. Analysis of results comparing different LLMs
4. Code comments and docstrings

### Showcase Materials:
1. GitHub repository with clean structure
2. Sample outputs demonstrating the system
3. Summary of findings (which LLMs perform best)
4. Optional: Blog post or presentation slides

---

## 🎓 Learning Outcomes

By completing this project, you will:

1. ✅ Master LLM function calling APIs (OpenAI, Anthropic)
2. ✅ Develop systematic evaluation methodologies
3. ✅ Build text parsing and pattern matching skills
4. ✅ Understand AI hallucination detection
5. ✅ Create structured testing frameworks
6. ✅ Generate professional technical reports
7. ✅ Demonstrate code review and QA mindset

**Most importantly:** You'll have concrete proof of the exact skills Mercor is looking for!

---

## 🚀 Extensions & Advanced Features (Optional)

If time permits, consider adding:

1. **Batch Testing:** Run hundreds of scenarios in parallel
2. **Visualization Dashboard:** Web UI showing results
3. **Benchmark Suite:** Standard tests for comparing LLMs
4. **Cost Tracker:** Monitor API spending per test
5. **Regression Testing:** Track performance over time
6. **Multi-turn Conversations:** Test agents with back-and-forth dialogue
7. **Real-world Scenarios:** Import actual coding tasks from GitHub issues
8. **Adversarial Tests:** Specially designed to trip up LLMs
9. **Comparative Analysis:** Side-by-side LLM performance charts
10. **CI/CD Integration:** Automated testing pipeline

---

## 📋 Checklist Before Starting

- [ ] Read this entire document
- [ ] Understand each component's purpose
- [ ] Set up development environment
- [ ] Obtain OpenAI API key
- [ ] Review OpenAI function calling documentation
- [ ] Sketch out project structure
- [ ] Identify 5-10 test scenarios to start with
- [ ] Plan time allocation (recommend 10-14 days)

---

## ❓ Key Questions to Answer During Implementation

1. How do I handle edge cases where claims are ambiguous?
2. What confidence threshold should I use for claim extraction?
3. How do I balance strictness vs. flexibility in validation?
4. Should I penalize LLMs for being overly cautious (too many checks)?
5. How do I handle multi-turn conversations vs. single interactions?
6. What makes a "good" test scenario vs. a "bad" one?
7. How do I ensure my evaluation isn't biased toward certain LLM styles?

---

## 🎯 Connection to Mercor Role

This project directly prepares you for the Mercor evaluation role because:

1. ✅ You'll practice analyzing AI assistant transcripts
2. ✅ You'll detect mismatches between claims and actions
3. ✅ You'll apply structured rubrics to score performance
4. ✅ You'll write detailed justifications with examples
5. ✅ You'll understand function call mechanics deeply
6. ✅ You'll identify hallucinations and consistency issues
7. ✅ You'll think like a QA engineer evaluating AI systems

**This is essentially building your own version of what Mercor does!**

---

## 📝 Final Notes

- **Scope:** This is a 10-14 day project if done properly
- **Difficulty:** Intermediate - requires solid Python and API skills
- **Impact:** High - directly relevant to Mercor role
- **Portfolio Value:** Excellent - unique and demonstrates rare skills

**Remember:** The goal isn't perfection, it's demonstrating the right mindset and skills. Even a partial implementation showing good evaluation methodology is valuable.

Good luck! 🚀

