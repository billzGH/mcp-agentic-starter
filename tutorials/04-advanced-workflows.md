# Tutorial 4: Advanced Workflows

**Time**: 90 minutes  
**Difficulty**: Advanced  
**Prerequisites**: Tutorials 1-3

## What You'll Learn

- Building complex multi-step workflows
- Error handling and recovery strategies
- State management across sessions
- Performance optimization
- Production-ready patterns
- Testing and monitoring

## Advanced Workflow Patterns

### Pattern 1: Multi-Stage Processing Pipeline

**Use Case**: Process data through multiple transformation stages

**Example**: Customer data enrichment pipeline

```python
# Conceptual workflow
Stage 1: Data Ingestion
  → validate_input()
  → clean_data()
  → store_raw()

Stage 2: Enrichment
  → lookup_demographics()
  → calculate_metrics()
  → append_segments()

Stage 3: Analysis
  → identify_patterns()
  → generate_insights()
  → create_recommendations()

Stage 4: Output
  → format_results()
  → generate_report()
  → deliver_output()
```

**Implementation Pattern**:

```python
@server.call_tool()
async def call_tool(name: str, arguments: Any):
    # Track pipeline stage
    stage = arguments.get('stage', 'ingestion')
    
    # Stage-specific processing
    if stage == 'ingestion':
        result = await ingest_data(arguments)
        # Automatically trigger next stage
        return result, {"next_stage": "enrichment"}
    
    elif stage == 'enrichment':
        # Process and continue
        ...
```

**Prompt Strategy**:

```plaintext
Process customer data through this pipeline:

1. Validation: Check for required fields, fix formats
2. Enrichment: Add segment data, calculate lifetime value
3. Analysis: Identify high-value customers, find patterns
4. Output: Create segmented lists and summary report

After each stage, show me what you found before continuing.
```

### Pattern 2: Branching Workflows

**Use Case**: Different paths based on conditions

**Example**: Content moderation workflow

```plaintext
Input: User-submitted content
  ↓
Automated check
  ├─→ PASS → Publish immediately
  ├─→ UNCERTAIN → Flag for human review
  └─→ FAIL → Reject with explanation
```

**Prompt Strategy**:

```plaintext
Review submitted articles in queue/:

For each article:
- If clearly appropriate: approve and publish
- If borderline: add to review queue with concerns
- If inappropriate: reject with specific reason

Process all and give me summary statistics.
```

### Pattern 3: Parallel Analysis

**Use Case**: Analyze multiple datasets simultaneously

**Example**: Cross-regional performance analysis

```plaintext
FOR EACH region IN [North, South, East, West]:
  analyze_sales(region)
  calculate_metrics(region)
  identify_trends(region)

THEN:
  compare_regions()
  find_best_practices()
  generate_recommendations()
```

**Prompt Strategy**:

```plaintext
Analyze sales performance for each region:

For North, South, East, West regions separately:
1. Calculate revenue, growth, customer count
2. Identify top products
3. Find unique patterns

Then compare regions and tell me:
- Which region is performing best and why
- What other regions can learn from them
```

### Pattern 4: Feedback Loop

**Use Case**: Iterative improvement based on results

**Example**: A/B test optimization

```plaintext
Loop:
  1. Run experiment with current parameters
  2. Measure results
  3. Analyze performance
  4. Adjust parameters
  5. If improved → Continue
     Else → Revert and try different approach
  6. Repeat until convergence or max iterations
```

**Prompt Strategy**:

```plaintext
Optimize email subject lines for open rates:

Test variations and:
- Track which performs best
- Identify what makes them effective
- Generate new variations based on learnings
- Continue until we find a clear winner

Keep me updated on each iteration.
```

## State Management

### Challenge: MCP servers are stateless

Each tool call is independent - no automatic memory between calls.

### Solution 1: Conversation Context

Claude maintains context within a conversation:

```plaintext
User: "Analyze sales data"
Claude: [calls tools, analyzes]

User: "Now do the same for last quarter"
Claude: [remembers what "same" means, repeats analysis]
```

### Solution 2: Explicit State Passing

Pass state as tool arguments:

```python
Tool: process_data
Arguments: {
  "data_file": "sales.csv",
  "state": {
    "current_step": 3,
    "processed_rows": 1500,
    "errors": []
  }
}
```

### Solution 3: Persistent Storage

Store state in files or databases:

```python
@server.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "continue_processing":
        # Load previous state
        state = load_state(arguments['session_id'])
        
        # Resume from checkpoint
        result = process_from_checkpoint(state)
        
        # Save updated state
        save_state(arguments['session_id'], result.state)
        
        return result
```

**Example Implementation**:

```python
import json
from pathlib import Path

STATE_DIR = Path("./state")
STATE_DIR.mkdir(exist_ok=True)

def save_state(session_id: str, state: dict):
    """Save workflow state"""
    state_file = STATE_DIR / f"{session_id}.json"
    with open(state_file, 'w') as f:
        json.dump(state, f)

def load_state(session_id: str) -> dict:
    """Load workflow state"""
    state_file = STATE_DIR / f"{session_id}.json"
    if state_file.exists():
        with open(state_file, 'r') as f:
            return json.load(f)
    return {}
```

## Error Handling Strategies

### Strategy 1: Graceful Degradation

Continue with partial results rather than failing completely:

```python
@server.call_tool()
async def call_tool(name: str, arguments: Any):
    results = []
    errors = []
    
    for item in items:
        try:
            result = process_item(item)
            results.append(result)
        except Exception as e:
            errors.append({
                "item": item,
                "error": str(e)
            })
    
    return {
        "successful": results,
        "failed": errors,
        "success_rate": len(results) / len(items)
    }
```

### Strategy 2: Automatic Retry

Retry transient failures:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def fetch_external_data(url: str):
    """Retry on failure with exponential backoff"""
    response = await http_client.get(url)
    response.raise_for_status()
    return response.json()
```

### Strategy 3: Validation Gates

Validate before proceeding:

```python
def process_pipeline(data):
    # Stage 1: Validation
    if not validate_data(data):
        return {"error": "Invalid input data", "stage": "validation"}
    
    # Stage 2: Processing
    processed = transform_data(data)
    if not verify_output(processed):
        return {"error": "Processing failed validation", "stage": "processing"}
    
    # Stage 3: Analysis
    results = analyze(processed)
    return {"success": True, "results": results}
```

### Strategy 4: Detailed Error Context

Provide actionable error information:

```python
try:
    result = process_file(filepath)
except FileNotFoundError:
    return {
        "error": f"File not found: {filepath}",
        "suggestion": "Check the file path and try again",
        "available_files": list_available_files()
    }
except ValueError as e:
    return {
        "error": f"Invalid data format: {str(e)}",
        "suggestion": "Ensure file is valid CSV with required columns",
        "required_columns": ["date", "amount", "category"]
    }
```

## Performance Optimization

### Optimization 1: Batch Operations

Process multiple items in one tool call:

```python
# Instead of:
for customer in customers:
    result = process_customer(customer)  # N tool calls

# Do:
results = process_customers_batch(customers)  # 1 tool call
```

### Optimization 2: Caching

Cache expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_customer_segment(customer_id: str):
    """Cache segment lookups"""
    return calculate_segment(customer_id)
```

### Optimization 3: Lazy Loading

Load data only when needed:

```python
class DataAnalyzer:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._data = None  # Not loaded yet
    
    @property
    def data(self):
        """Lazy load data"""
        if self._data is None:
            self._data = self._load_data()
        return self._data
```

### Optimization 4: Progressive Results

Return partial results as they're ready:

```python
async def analyze_large_dataset(filepath: str):
    """Stream results as they're computed"""
    
    # Quick initial summary
    yield {"status": "started", "rows": count_rows(filepath)}
    
    # Process in chunks
    for chunk in read_chunks(filepath):
        results = process_chunk(chunk)
        yield {"status": "progress", "results": results}
    
    # Final aggregation
    yield {"status": "complete", "summary": final_summary()}
```

## Production Considerations

### 1. Logging

Comprehensive logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    logger.info(f"Tool called: {name}", extra={"arguments": arguments})
    
    try:
        result = execute_tool(name, arguments)
        logger.info(f"Tool succeeded: {name}", extra={"result_summary": summarize(result)})
        return result
    except Exception as e:
        logger.error(f"Tool failed: {name}", extra={"error": str(e)}, exc_info=True)
        raise
```

### 2. Monitoring

Track tool usage and performance:

```python
from datetime import datetime
import time

class ToolMetrics:
    def __init__(self):
        self.calls = []
    
    def record_call(self, tool_name: str, duration: float, success: bool):
        self.calls.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "duration": duration,
            "success": success
        })
    
    def get_stats(self):
        return {
            "total_calls": len(self.calls),
            "success_rate": sum(c["success"] for c in self.calls) / len(self.calls),
            "avg_duration": sum(c["duration"] for c in self.calls) / len(self.calls)
        }

metrics = ToolMetrics()

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    start = time.time()
    success = False
    
    try:
        result = execute_tool(name, arguments)
        success = True
        return result
    finally:
        duration = time.time() - start
        metrics.record_call(name, duration, success)
```

### 3. Rate Limiting

Protect external APIs:

```python
from asyncio import Semaphore
import time

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.semaphore = Semaphore(calls_per_minute)
        self.call_times = []
    
    async def acquire(self):
        async with self.semaphore:
            # Clean old entries
            now = time.time()
            self.call_times = [t for t in self.call_times if now - t < 60]
            
            # Wait if at limit
            if len(self.call_times) >= self.calls_per_minute:
                wait_time = 60 - (now - self.call_times[0])
                await asyncio.sleep(wait_time)
            
            self.call_times.append(now)

limiter = RateLimiter(calls_per_minute=60)

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "call_external_api":
        await limiter.acquire()
    
    return execute_tool(name, arguments)
```

### 4. Input Validation

Validate all inputs:

```python
from pydantic import BaseModel, validator

class AnalysisRequest(BaseModel):
    filepath: str
    date_range: tuple[str, str]
    metrics: list[str]
    
    @validator('filepath')
    def filepath_exists(cls, v):
        if not Path(v).exists():
            raise ValueError(f"File not found: {v}")
        return v
    
    @validator('metrics')
    def valid_metrics(cls, v):
        valid = ['revenue', 'orders', 'customers']
        if not all(m in valid for m in v):
            raise ValueError(f"Invalid metrics. Must be in: {valid}")
        return v

@server.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "analyze_data":
        # Validate with Pydantic
        request = AnalysisRequest(**arguments)
        return execute_analysis(request)
```

## Testing Strategies

### Unit Tests

Test individual tools:

```python
import pytest
from server import DataAnalyzer

def test_analyze_column_numeric():
    analyzer = DataAnalyzer()
    result = analyzer.analyze_column(
        "test_data.csv",
        "revenue"
    )
    
    assert result["type"] == "numeric"
    assert "mean" in result
    assert "median" in result

def test_filter_data():
    analyzer = DataAnalyzer()
    result = analyzer.filter_data(
        "test_data.csv",
        [{"column": "status", "operator": "==", "value": "completed"}]
    )
    
    assert all(row["status"] == "completed" for row in result)
```

### Integration Tests

Test tool chains:

```python
@pytest.mark.asyncio
async def test_full_analysis_workflow():
    """Test complete analysis workflow"""
    
    # Step 1: List files
    files = await call_tool("list_data_files", {})
    assert len(files) > 0
    
    # Step 2: Get summary
    summary = await call_tool("get_data_summary", {
        "filepath": "sales/transactions.csv"
    })
    assert "num_records" in summary
    
    # Step 3: Analyze column
    analysis = await call_tool("analyze_column", {
        "filepath": "sales/transactions.csv",
        "column": "total_amount"
    })
    assert analysis["type"] == "numeric"
```

### Load Tests

Test performance under load:

```python
import asyncio

async def load_test():
    """Simulate 100 concurrent tool calls"""
    tasks = []
    
    for i in range(100):
        task = call_tool("analyze_column", {
            "filepath": "sales/transactions.csv",
            "column": "total_amount"
        })
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Verify all succeeded
    assert all(r is not None for r in results)
    
    # Check performance
    # (add timing logic)

asyncio.run(load_test())
```

## Real-World Example: Data Pipeline

Let's build a complete production-ready pipeline:

```python
#!/usr/bin/env python3
"""
Production-ready data analysis pipeline
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum

from mcp.server import Server
from mcp.types import Tool, TextContent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class PipelineStage(Enum):
    INGESTION = "ingestion"
    VALIDATION = "validation"
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    REPORTING = "reporting"

@dataclass
class PipelineState:
    session_id: str
    stage: PipelineStage
    input_file: str
    records_processed: int = 0
    errors: List[Dict] = None
    results: Dict = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.results is None:
            self.results = {}

class DataPipeline:
    """Production data pipeline with state management"""
    
    def __init__(self):
        self.state_dir = Path("./pipeline_state")
        self.state_dir.mkdir(exist_ok=True)
    
    def save_state(self, state: PipelineState):
        """Persist pipeline state"""
        state_file = self.state_dir / f"{state.session_id}.json"
        state_file.write_text(json.dumps(asdict(state)))
        logger.info(f"Saved state for session {state.session_id}")
    
    def load_state(self, session_id: str) -> PipelineState:
        """Load pipeline state"""
        state_file = self.state_dir / f"{session_id}.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())
            return PipelineState(**data)
        raise ValueError(f"No state found for session {session_id}")
    
    async def run_stage(self, state: PipelineState) -> PipelineState:
        """Execute current pipeline stage"""
        logger.info(f"Running stage: {state.stage.value}")
        
        try:
            if state.stage == PipelineStage.INGESTION:
                return await self._ingest(state)
            elif state.stage == PipelineStage.VALIDATION:
                return await self._validate(state)
            elif state.stage == PipelineStage.PROCESSING:
                return await self._process(state)
            elif state.stage == PipelineStage.ANALYSIS:
                return await self._analyze(state)
            elif state.stage == PipelineStage.REPORTING:
                return await self._report(state)
        except Exception as e:
            logger.error(f"Stage failed: {state.stage.value}", exc_info=True)
            state.errors.append({
                "stage": state.stage.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def _ingest(self, state: PipelineState) -> PipelineState:
        """Load and prepare data"""
        # Implementation
        state.stage = PipelineStage.VALIDATION
        return state
    
    async def _validate(self, state: PipelineState) -> PipelineState:
        """Validate data quality"""
        # Implementation
        state.stage = PipelineStage.PROCESSING
        return state
    
    async def _process(self, state: PipelineState) -> PipelineState:
        """Transform data"""
        # Implementation
        state.stage = PipelineStage.ANALYSIS
        return state
    
    async def _analyze(self, state: PipelineState) -> PipelineState:
        """Analyze processed data"""
        # Implementation
        state.stage = PipelineStage.REPORTING
        return state
    
    async def _report(self, state: PipelineState) -> PipelineState:
        """Generate final report"""
        # Implementation
        return state

# Initialize server and pipeline
server = Server("data-pipeline")
pipeline = DataPipeline()

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="start_pipeline",
            description="Start a new data pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["input_file", "session_id"]
            }
        ),
        Tool(
            name="continue_pipeline",
            description="Continue an existing pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            }
        ),
        Tool(
            name="get_pipeline_status",
            description="Check pipeline status",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"}
                },
                "required": ["session_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    try:
        if name == "start_pipeline":
            # Create new pipeline
            state = PipelineState(
                session_id=arguments["session_id"],
                stage=PipelineStage.INGESTION,
                input_file=arguments["input_file"]
            )
            
            # Run first stage
            state = await pipeline.run_stage(state)
            pipeline.save_state(state)
            
            return [TextContent(
                type="text",
                text=f"Pipeline started. Current stage: {state.stage.value}"
            )]
        
        elif name == "continue_pipeline":
            # Load and continue
            state = pipeline.load_state(arguments["session_id"])
            state = await pipeline.run_stage(state)
            pipeline.save_state(state)
            
            if state.stage == PipelineStage.REPORTING:
                message = f"Pipeline complete! Results: {state.results}"
            else:
                message = f"Stage complete. Next: {state.stage.value}"
            
            return [TextContent(type="text", text=message)]
        
        elif name == "get_pipeline_status":
            state = pipeline.load_state(arguments["session_id"])
            
            status = f"""
Pipeline Status:
- Session: {state.session_id}
- Current Stage: {state.stage.value}
- Records Processed: {state.records_processed}
- Errors: {len(state.errors)}
"""
            return [TextContent(type="text", text=status)]
    
    except Exception as e:
        logger.error(f"Tool call failed: {name}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

## Key Takeaways

✅ **State Management**: Critical for long-running workflows

✅ **Error Handling**: Plan for failures, provide context

✅ **Performance**: Batch operations, cache, lazy load

✅ **Production Ready**: Logging, monitoring, validation

✅ **Testing**: Unit, integration, and load tests

✅ **Modularity**: Build reusable components

## Final Project: Build Your Pipeline

Create a production-ready pipeline that:

1. Ingests data from multiple sources
2. Validates and cleans
3. Processes and enriches
4. Analyzes and generates insights
5. Produces formatted reports

Include:

- State persistence
- Error recovery
- Progress tracking
- Comprehensive logging
- Full test suite

## Congratulations

You've completed the MCP tutorial series. You now know:

- ✅ What MCP is and how it works
- ✅ How to build MCP servers
- ✅ Common agentic patterns
- ✅ Production-ready implementations

**Next steps**:

- Build your own project from [PROJECT-IDEAS.md](../projects/PROJECT-IDEAS.md)
- Contribute to the community
- Share your learnings

Happy building! 🚀
