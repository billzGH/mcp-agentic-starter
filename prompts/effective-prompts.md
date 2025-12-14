# Effective Prompts for Agentic AI

A collection of proven prompt patterns that help Claude use MCP tools effectively to accomplish complex tasks.

## Table of Contents

1. [Basic Principles](#basic-principles)
2. [Prompt Templates](#prompt-templates)
3. [Common Workflows](#common-workflows)
4. [Advanced Techniques](#advanced-techniques)

## Basic Principles

### 1. Be Clear About the Outcome

✅ **Good**: "Analyze sales data and create a report showing top products by revenue"  
❌ **Poor**: "Look at the sales data"

### 2. Provide Context

✅ **Good**: "I'm preparing for a board meeting. Find our Q4 metrics..."  
❌ **Poor**: "Get the metrics"

### 3. Let Claude Use Tools

✅ **Good**: "Find the most expensive products in our catalog"  
❌ **Poor**: "Here's our product list [paste 1000 rows]"

### 4. Break Complex Tasks into Steps (Optional)

Sometimes Claude benefits from step-by-step guidance:

```text
Please help me analyze customer behavior:
1. First, get a summary of the transactions data
2. Then identify our top 10 customers by total spend
3. Finally, analyze what products they buy most
```

## Prompt Templates

### Data Analysis

**Template**:

```text
Analyze [data source] to [objective].

Focus on:
- [metric 1]
- [metric 2]
- [metric 3]

Present findings as [format: table/chart/summary].
```

**Example**:

```text
Analyze the sales transactions to identify revenue trends.

Focus on:
- Monthly revenue over time
- Top-performing categories
- Regional differences

Present findings as a summary with key insights.
```

### Research & Synthesis

**Template**:

```text
Research [topic] by:
1. [search/gather from source]
2. [analyze/filter criteria]
3. [synthesize into format]

I need this for [purpose/audience].
```

**Example**:

```text
Research our competitors' pricing by:
1. Searching for their product catalogs
2. Comparing similar products to ours
3. Summarizing in a comparison table

I need this for a pricing strategy meeting.
```

### Automation

**Template**:

```text
Automate [task] for [items/targets]:
- Input: [where to find inputs]
- Process: [what to do]
- Output: [where/how to save]
- Handle errors by [error handling]
```

**Example**:

```text
Automate invoice generation for pending orders:
- Input: Orders with status "pending_invoice"
- Process: Calculate totals, apply discounts, add tax
- Output: Save as PDF in invoices/YYYY-MM/
- Handle errors by logging to errors.txt
```

### Reporting

**Template**:

```text
Create a [report type] covering [time period]:
- Data sources: [list]
- Key sections: [sections]
- Audience: [who will read it]
- Format: [PowerPoint/Word/PDF]
```

**Example**:

```text
Create a weekly sales report covering last 7 days:
- Data sources: transactions.csv, products.csv
- Key sections: Total revenue, top products, regional breakdown
- Audience: Sales team
- Format: Bullet points with key numbers
```

## Common Workflows

### 1. Exploratory Data Analysis

**Goal**: Understand a new dataset

**Prompt**:

```text
I have a new dataset at datasets/sales/transactions.csv. 
Help me understand it:
1. What data is available?
2. What's the time range?
3. What are the key statistics?
4. Are there any notable patterns or anomalies?
```

**Why it works**: Gives Claude freedom to explore systematically while providing structure.

### 2. Comparison Analysis

**Goal**: Compare two or more things

**Prompt**:

```text
Compare our Q3 vs Q4 performance:
- Revenue by category
- Customer acquisition
- Average order value

Highlight significant changes (>10% difference).
```

**Why it works**: Clear comparison criteria, specific threshold for "significant."

### 3. Trend Identification

**Goal**: Find patterns over time

**Prompt**:

```text
Analyze monthly trends in customer_support.csv:
- Are tickets increasing or decreasing?
- Which categories are growing?
- What's the resolution time trend?

Flag any concerning trends.
```

**Why it works**: Specific questions + asks for interpretation ("concerning").

### 4. Data Quality Check

**Goal**: Validate data integrity

**Prompt**:

```text
Check data quality in customers.csv:
- Missing values in critical fields
- Duplicate records
- Invalid formats (email, phone)
- Outliers in numeric fields

Summarize issues by severity.
```

**Why it works**: Comprehensive checklist, prioritization requested.

### 5. Insight Generation

**Goal**: Extract business insights

**Prompt**:

```text
Analyze transactions and identify:
- Our most valuable customer segments
- Products frequently bought together
- Underperforming categories

Recommend 3 actions we should take.
```

**Why it works**: Asks for patterns AND actionable recommendations.

## Advanced Techniques

### Multi-Source Analysis

When you need data from multiple places:

```text
Compare our internal sales data (datasets/sales/) with 
industry benchmarks. For industry data, search for:
- Average e-commerce conversion rates
- Typical customer lifetime value in our sector
- Industry growth rates

Present as: Our performance vs. industry average.
```

### Iterative Refinement

Start broad, then drill down:

```text
First pass: Identify the top 5 products by revenue.

Second pass: For each top product, analyze:
- Which customers buy it most?
- What time of year is it popular?
- What's the profit margin?
```

### Conditional Logic

Use "if/then" for complex scenarios:

```text
Analyze customer segments:
- IF segment has >$10k lifetime value, label "VIP"
- IF segment hasn't purchased in 90 days, label "At Risk"
- ELSE label "Standard"

Then summarize how many customers are in each category.
```

### Error-Resilient Prompts

Handle potential issues gracefully:

```text
Process all invoices in invoices/pending/:
- Try to extract customer ID, amount, date
- If any field is missing, log to errors.txt and skip
- For successful extractions, add to processed.csv
- At the end, report: success count, error count
```

## Prompt Anti-Patterns

### ❌ Too Vague

"Analyze the data"

- Claude doesn't know what you want to learn

### ❌ Over-Specifying Tools

"Use the list_data_files tool, then the get_data_summary tool..."

- Let Claude choose the right tools

### ❌ Pasting Large Data

"Here's 500 rows of data: [paste]"

- Point to files instead; let Claude use tools

### ❌ No Success Criteria

"Make the report better"

- Define what "better" means

### ❌ Assuming Context

"Fix the issue"

- What issue? Where? With what?

## Tips for Better Results

### 1. Start Simple, Then Iterate

```text
First: "What's in the sales data?"
Then: "Show me trends over time"
Finally: "Create a monthly report format"
```

### 2. Specify Formats

- "as a table"
- "as bullet points"
- "as a JSON file"
- "in plain English"

### 3. Set Boundaries

- "top 10 results"
- "only Q4 data"
- "products priced above $100"
- "last 30 days"

### 4. Request Explanations

- "and explain why this matters"
- "with context for each finding"
- "show your reasoning"

### 5. Ask for Validation

- "double-check the calculations"
- "verify the data quality first"
- "confirm before making changes"

## Example Workflows by Role

### Data Analyst

```text
Daily: "Update my dashboard with yesterday's metrics"
Weekly: "Generate the weekly performance report"
Ad-hoc: "Why did revenue drop 15% on Tuesday?"
```

### Product Manager

```text
"What features are most requested in support tickets?"
"Which customers haven't used feature X?"
"Compare adoption rates between segments"
```

### Marketing

```text
"Which campaigns have the best ROI?"
"Create customer personas from our transaction data"
"Find email addresses of customers who bought product X"
```

### Operations

```text
"Which products are low on inventory?"
"Calculate average fulfillment time by region"
"Identify orders stuck in pending status"
```

## Testing Your Prompts

Good prompts should:

1. ✅ Work the first time (or need only minor clarification)
2. ✅ Give consistent results when repeated
3. ✅ Scale to similar tasks
4. ✅ Handle edge cases gracefully

To test:

- Try with different data files
- Test with empty/missing data
- Verify Claude asks for clarification when needed
- Check if outputs are actually useful

## Next Steps

Try these prompts with your MCP servers:

1. Pick a template from above
2. Adapt it to your data/task
3. Run it and see what happens
4. Refine based on results
5. Save successful prompts for reuse

The best prompts come from iteration. Start with these templates, but customize them for your specific needs!
