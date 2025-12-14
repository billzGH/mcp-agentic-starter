# Tutorial 3: Agentic Patterns

**Time**: 60 minutes  
**Difficulty**: Intermediate  
**Prerequisites**: Tutorials 1 & 2

## What You'll Learn

- Common patterns for agentic workflows
- How to design effective tool chains
- Prompting strategies for multi-step tasks
- Error handling and recovery
- State management across tool calls

## Understanding Agentic Behavior

Traditional AI: Answer questions based on training data  
**Agentic AI**: Use tools to accomplish goals autonomously

### The Agentic Loop

```plaintext
1. User gives goal/task
2. Claude breaks down into steps
3. Claude selects appropriate tool
4. Tool executes and returns result
5. Claude evaluates result
6. Repeat steps 3-5 until goal achieved
7. Claude synthesizes final response
```

## Core Agentic Patterns

### Pattern 1: Sequential Execution

**When to use**: Steps must happen in order

**Example Task**: "Create a sales report from our data"

**Workflow**:

```plaintext
1. list_data_files()          → Find available data
2. get_data_summary()          → Understand structure
3. analyze_column('revenue')   → Get key metrics
4. aggregate_data()            → Group by category
5. [synthesize results]        → Generate report
```

**Prompt Design**:

```plaintext
Create a sales report with:
1. Total revenue
2. Top 5 products
3. Revenue by region

Use the data in datasets/sales/
```

**Why it works**:

- Clear end goal
- Logical sequence
- Claude can plan the steps

### Pattern 2: Exploratory Analysis

**When to use**: Discovering insights in unfamiliar data

**Example Task**: "What's interesting about this dataset?"

**Workflow**:

```plaintext
1. get_data_summary()          → See what's available
2. analyze_column(key_cols)    → Check distributions
3. look for anomalies          → Find outliers
4. identify correlations       → Find patterns
5. [generate insights]         → Report findings
```

**Prompt Design**:

```plaintext
I have a new dataset at datasets/sales/transactions.csv

Explore it and tell me:
- What patterns do you see?
- Are there any anomalies?
- What's worth investigating further?
```

**Why it works**:

- Open-ended exploration
- Claude decides what to investigate
- Follows data-driven curiosity

### Pattern 3: Iterative Refinement

**When to use**: Results need progressive improvement

**Example Task**: "Find the best customer segment for our campaign"

**Workflow**:

```plaintext
1. segment_customers(criteria_v1)  → Initial segmentation
2. analyze_results()               → Check quality
3. segment_customers(criteria_v2)  → Refine approach
4. compare_segments()              → Evaluate improvement
5. [repeat until satisfied]        → Iterate
6. [recommend best]                → Final answer
```

**Prompt Design**:

```plaintext
Help me find our most valuable customer segment.

Start with basic demographics, then refine based on:
- Purchase frequency
- Average order value
- Product preferences

Tell me when you find a segment worth targeting.
```

**Why it works**:

- Allows for course correction
- Claude evaluates quality
- Learns from intermediate results

### Pattern 4: Multi-Source Synthesis

**When to use**: Combining information from multiple places

**Example Task**: "Compare our performance to industry benchmarks"

**Workflow**:

```plaintext
1. query_internal_db()         → Get our metrics
2. web_search()                → Find industry data
3. web_fetch()                 → Get detailed reports
4. normalize_data()            → Make comparable
5. [compare and analyze]       → Generate insights
```

**Prompt Design**:

```plaintext
Compare our Q4 sales performance to industry averages:

Internal data: datasets/sales/
External: Search for e-commerce industry benchmarks

Focus on: conversion rate, average order value, customer acquisition cost
```

**Why it works**:

- Combines internal and external data
- Clear comparison criteria
- Defined metrics

### Pattern 5: Conditional Logic

**When to use**: Different actions based on conditions

**Example Task**: "Process orders and handle exceptions"

**Workflow**:

```plaintext
For each order:
  IF complete → generate_invoice()
  ELSE IF missing_info → flag_for_review()
  ELSE IF inventory_low → notify_supplier()
  ELSE → mark_pending()
```

**Prompt Design**:

```plaintext
Process all orders in orders.csv:

Rules:
- Complete orders: generate invoice
- Missing customer info: add to review queue
- Low inventory items: flag for restock
- Everything else: mark as pending

Summarize results by category.
```

**Why it works**:

- Explicit decision rules
- Handles edge cases
- Clear categorization

### Pattern 6: Validation & Verification

**When to use**: Ensuring data quality and correctness

**Example Task**: "Clean and validate customer data"

**Workflow**:

```plaintext
1. load_data()                 → Get raw data
2. check_required_fields()     → Find missing values
3. validate_formats()          → Check emails, phones
4. identify_duplicates()       → Find repeated records
5. calculate_quality_score()   → Measure data health
6. [generate report]           → Document issues
```

**Prompt Design**:

```plaintext
Validate customers.csv:

Check for:
✓ Missing email or phone
✓ Invalid email formats
✓ Duplicate customer IDs
✓ Outliers in purchase amounts

Report issues by severity: critical, warning, info
```

**Why it works**:

- Comprehensive checks
- Prioritized issues
- Actionable results

## Advanced Patterns

### Pattern 7: Divide and Conquer

**When to use**: Large tasks that can be parallelized (conceptually)

**Example Task**: "Analyze all product categories for trends"

**Workflow**:

```plaintext
1. get_categories()                      → List all categories
2. FOR EACH category:
   - filter_data(category)              → Subset data
   - analyze_trends()                   → Find patterns
   - identify_top_products()            → Get winners
3. [compare across categories]          → Find insights
4. [synthesize recommendations]         → Action items
```

**Prompt Design**:

```plaintext
Analyze each product category separately:

For each category:
1. Revenue trends over time
2. Top 3 products
3. Growth rate

Then compare categories and recommend which to prioritize.
```

### Pattern 8: Hypothesis Testing

**When to use**: Investigating specific questions

**Example Task**: "Do email campaigns increase sales?"

**Workflow**:

```plaintext
1. formulate_hypothesis()              → State assumption
2. identify_test_data()                → Find relevant data
3. segment_customers()                 → Control vs test
4. calculate_metrics()                 → Measure outcomes
5. statistical_test()                  → Check significance
6. [draw conclusion]                   → Answer question
```

**Prompt Design**:

```plaintext
Test hypothesis: Email campaigns increase repeat purchases

Compare customers who:
- Received campaign emails (treatment)
- Didn't receive emails (control)

Measure: repeat purchase rate, time to next purchase, order value

Tell me if the difference is meaningful.
```

### Pattern 9: Root Cause Analysis

**When to use**: Understanding why something happened

**Example Task**: "Why did sales drop 20% last month?"

**Workflow**:

```plaintext
1. confirm_the_drop()                  → Verify the fact
2. segment_analysis()                  → Where did it drop?
3. temporal_analysis()                 → When exactly?
4. compare_to_baseline()               → What changed?
5. identify_correlations()             → Find related factors
6. [propose explanations]              → Likely causes
```

**Prompt Design**:

```plaintext
Sales dropped 20% in November. Investigate why.

Check:
- Which products/categories were affected?
- Which regions saw the drop?
- Did customer behavior change?
- Were there external factors?

Rank causes by likelihood.
```

### Pattern 10: Recommendation Generation

**When to use**: Suggesting next actions

**Example Task**: "What products should we promote next month?"

**Workflow**:

```plaintext
1. analyze_current_performance()       → Baseline metrics
2. identify_opportunities()            → Underperforming items
3. calculate_potential()               → Estimate impact
4. check_constraints()                 → Inventory, seasonality
5. rank_options()                      → Priority order
6. [generate recommendations]          → Action plan
```

**Prompt Design**:

```plaintext
Recommend products to promote next month.

Consider:
- Current sales velocity
- Profit margins
- Inventory levels
- Seasonal trends

Give me top 5 with reasoning.
```

## Designing Effective Workflows

### Step 1: Define the Goal

❌ Vague: "Analyze the data"  
✅ Clear: "Identify our top 3 customer segments by lifetime value"

### Step 2: Identify Required Information

What data do you need?

- Internal databases
- External sources
- Historical context

### Step 3: Plan the Tool Chain

List tools in logical order:

```plaintext
1. What tools gather information?
2. What tools process/transform?
3. What tools analyze/synthesize?
```

### Step 4: Define Success Criteria

How do you know you're done?

- Specific metrics calculated
- Question answered
- Recommendation generated

### Step 5: Handle Errors

What could go wrong?

- Missing data → fallback sources
- Invalid inputs → validation
- API failures → retry logic

## Prompting Techniques for Agentic Workflows

### Technique 1: Provide Context

```plaintext
I'm preparing for a board meeting tomorrow.

[rest of task]

I need this to be accurate and well-supported.
```

### Technique 2: Set Boundaries

```plaintext
Analyze customer data, but:
- Only last 90 days
- Exclude test accounts
- Focus on completed orders
```

### Technique 3: Request Intermediate Updates

```plaintext
As you analyze the data, let me know:
- What you're finding
- If anything looks unusual
- When you need clarification
```

### Technique 4: Specify Output Format

```plaintext
Generate a report with:
- Executive summary (3 bullets)
- Key metrics table
- Top 3 recommendations
- Supporting data
```

### Technique 5: Encourage Reasoning

```plaintext
For each recommendation:
- Explain the data behind it
- Quantify the expected impact
- Identify potential risks
```

## Common Pitfalls

### ❌ Pitfall 1: Over-Specification

Don't dictate every tool call:

```plaintext
Bad: "First use list_tools, then use get_summary, then..."
Good: "Analyze the sales data and find trends"
```

### ❌ Pitfall 2: No Success Criteria

```plaintext
Bad: "Make the report better"
Good: "Add monthly comparisons and highlight >10% changes"
```

### ❌ Pitfall 3: Ignoring Constraints

```plaintext
Bad: "Find the best solution"
Good: "Find the best solution under $10k budget with <1 week timeline"
```

### ❌ Pitfall 4: Assuming Perfect Data

```plaintext
Bad: "Calculate average revenue"
Good: "Calculate average revenue, handling missing values appropriately"
```

## Practice Exercises

### Exercise 1: Customer Segmentation

**Task**: Use the sample sales data to segment customers

**Goal**: Create 3-4 meaningful segments

**Success**: Clear definitions, different characteristics, actionable insights

**Try this prompt**:

```plaintext
Segment our customers in datasets/sales/ into groups.

Base it on:
- Purchase frequency
- Average order value
- Product preferences
- Recency

Name each segment and describe characteristics.
```

### Exercise 2: Product Performance

**Task**: Identify products that need attention

**Goal**: Find underperforming items worth improving

**Success**: Specific products with data-backed reasoning

**Try this prompt**:

```plaintext
Find products that are underperforming but have potential.

Look for products with:
- Declining sales trends
- Good profit margins
- No quality issues (high ratings)

Recommend actions for each.
```

### Exercise 3: Anomaly Detection

**Task**: Find unusual patterns in transaction data

**Goal**: Identify anomalies worth investigating

**Success**: Specific findings with context

**Try this prompt**:

```plaintext
Analyze transactions.csv for anomalies.

Look for:
- Unusual transaction amounts
- Unexpected timing patterns
- Geographic outliers
- Category anomalies

Flag anything suspicious.
```

## Debugging Agentic Workflows

### Issue: Claude doesn't use tools

**Solutions**:

- Make the need for external data clearer
- Ask explicitly: "Check the data file..."
- Verify tools are connected

### Issue: Wrong tool selection

**Solutions**:

- Improve tool descriptions
- Be more specific in prompt
- Break into smaller steps

### Issue: Incomplete analysis

**Solutions**:

- Set explicit success criteria
- Ask for intermediate updates
- Request verification

### Issue: Too many tool calls

**Solutions**:

- Simplify the task
- Provide more context upfront
- Set boundaries

## Key Takeaways

✅ **Let Claude decide** how to use tools, don't micro-manage

✅ **Clear goals** are more important than detailed steps

✅ **Iterative refinement** often works better than getting it perfect first time

✅ **Context matters** - explain why you need something

✅ **Set boundaries** - constraints help focus the analysis

✅ **Trust but verify** - check important results

## What's Next?

In **Tutorial 4**, you'll learn advanced workflows including:

- Multi-agent patterns
- Long-running processes
- Error recovery strategies
- State persistence
- Production considerations

Continue to [Tutorial 4: Advanced Workflows](04-advanced-workflows.md) →

## Additional Resources

- [Effective Prompts Guide](../prompts/effective-prompts.md)
- [Project Ideas](../projects/PROJECT-IDEAS.md)
- [MCP Official Documentation](https://modelcontextprotocol.io/)

## Self-Check

Can you:

- ✅ Identify which pattern fits a given task?
- ✅ Design a prompt that lets Claude use tools effectively?
- ✅ Recognize when a workflow needs refinement?
- ✅ Debug issues when tools aren't being used well?

If yes, you're ready for advanced workflows!
