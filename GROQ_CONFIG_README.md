# Groq Configuration System

This document describes the centralized Groq configuration system for the BC CrewAI project.

## Overview

The Groq configuration system provides a centralized way to manage Groq LLM instances across different agents and tasks. It includes:

- **`groq_config.py`**: Core configuration module with LLM instances
- **`groq_utils.py`**: Utility functions for LLM selection and validation
- **Updated `crew.py`**: Uses the configuration system for all agents

## Files Structure

```
bc/src/bc/
├── groq_config.py      # Core Groq configuration
├── groq_utils.py       # Utility functions
└── crew.py            # Updated to use Groq config

bc/
├── test_groq_config.py # Test script
└── GROQ_CONFIG_README.md # This file
```

## Quick Start

### 1. Set up your Groq API key

```bash
# Option 1: Environment variable
export GROQ_API_KEY="your-groq-api-key-here"

# Option 2: .env file
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

### 2. Test the configuration

```bash
cd bc
python test_groq_config.py
```

### 3. Use in your code

```python
from bc.groq_config import groq_fast, groq_balanced, groq_powerful
from bc.groq_utils import get_agent_llm_config

# Use pre-configured instances
agent = Agent(llm=groq_fast, ...)

# Or get LLM for specific agent
config = get_agent_llm_config('transit_planner')
agent = Agent(llm=config['llm'], ...)
```

## Available Models

The system supports these Groq models:

| Model Name | Groq Model ID | Use Case |
|------------|---------------|----------|
| `llama3_8b` | `groq/llama3-8b-8192` | Balanced performance |
| `llama3_70b` | `groq/llama3-70b-8192` | High performance |
| `mixtral` | `mixtral-8x7b-32768` | Advanced reasoning |
| `gemma` | `gemma-7b-it` | Fast inference |
| `llama3_1_8b` | `llama-3.1-8b-instant` | Ultra-fast response |

## Pre-configured LLM Instances

```python
from bc.groq_config import (
    groq_fast,      # llama-3.1-8b-instant
    groq_balanced,  # llama3-8b
    groq_powerful,  # llama3-70b
    groq_mixtral,   # mixtral-8x7b
    groq_gemma      # gemma-7b-it
)
```

## Agent-Specific LLM Configuration

The system automatically selects the best LLM for each agent type:

| Agent | Recommended LLM | Reasoning |
|-------|----------------|-----------|
| `transit_planner` | Fast (llama-3.1-8b-instant) | Real-time transit planning |
| `transit_analyst` | Balanced (llama3-8b) | Detailed analysis |
| `route_optimizer` | Balanced (llama3-8b) | Optimization tasks |
| `safety_route_finder` | Fast (llama-3.1-8b-instant) | Safety-critical routing |
| `safety_analyst` | Balanced (llama3-8b) | Safety analysis |
| `route_planner` | Balanced (llama3-8b) | Comprehensive planning |
| `researcher` | Powerful (llama3-70b) | Research tasks |
| `reporting_analyst` | Balanced (llama3-8b) | Report generation |
| `claude_agent` | Powerful (llama3-70b) | Claude-style analysis |

## Usage Examples

### Basic Usage

```python
from bc.groq_config import GroqConfig

# Get specific model
llm = GroqConfig.get_llm('llama3_8b')

# Get by performance level
fast_llm = GroqConfig.get_fast_llm()
balanced_llm = GroqConfig.get_balanced_llm()
powerful_llm = GroqConfig.get_powerful_llm()
```

### Task-Specific LLM Selection

```python
from bc.groq_utils import get_llm_for_task

# Get LLM for specific task and complexity
transit_llm = get_llm_for_task('transit', 'fast')
analysis_llm = get_llm_for_task('analysis', 'powerful')
```

### Agent Configuration

```python
from bc.groq_utils import get_agent_llm_config

# Get LLM config for specific agent
config = get_agent_llm_config('transit_planner')
print(f"LLM: {config['llm'].model}")
print(f"Reasoning: {config['reasoning']}")
```

### Validation and Status

```python
from bc.groq_utils import validate_groq_setup, print_groq_status

# Check setup status
status = validate_groq_setup()
print(f"API Key Valid: {status['api_key_valid']}")
print(f"Available Models: {status['models_available']}")

# Print formatted status
print_groq_status()
```

## Error Handling

The system includes comprehensive error handling:

```python
from bc.groq_config import GroqConfig

try:
    llm = GroqConfig.get_llm('llama3_8b')
except ValueError as e:
    print(f"Invalid model: {e}")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Testing

Run the test script to verify your setup:

```bash
cd bc
python test_groq_config.py
```

The test script will:
- Verify API key setup
- Test all available models
- Check crew integration
- Validate error handling

## Migration from Old System

If you were using the old hardcoded LLM configuration:

**Before:**
```python
groq_llm = LLM(
    model="groq/llama3-8b-8192",
    api_key="your-api-key"
)
```

**After:**
```python
from bc.groq_config import groq_balanced
# or
from bc.groq_utils import get_agent_llm_config
config = get_agent_llm_config('your_agent_name')
```

## Best Practices

1. **Use appropriate LLM for task**: Fast models for real-time tasks, powerful models for analysis
2. **Set API key in environment**: Use `GROQ_API_KEY` environment variable
3. **Test configuration**: Run `test_groq_config.py` after setup
4. **Handle errors gracefully**: Always wrap LLM creation in try-catch blocks
5. **Monitor usage**: Different models have different costs and performance characteristics

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ValueError: No Groq API key provided
   ```
   Solution: Set `GROQ_API_KEY` environment variable

2. **Invalid Model**
   ```
   ValueError: Unknown model: invalid_model
   ```
   Solution: Use one of the supported model names

3. **API Key Invalid**
   ```
   API key validation failed: 401 Unauthorized
   ```
   Solution: Check your Groq API key is correct and active

### Debug Mode

Enable debug mode to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- **Fast models** (llama-3.1-8b-instant): ~50ms response time, good for real-time tasks
- **Balanced models** (llama3-8b): ~200ms response time, good for most tasks
- **Powerful models** (llama3-70b): ~500ms response time, best for complex analysis

Choose the appropriate model based on your performance requirements and cost constraints. 