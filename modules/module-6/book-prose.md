# Module 6 Book Prose

## Intervention targeting and evaluation

How should interventions be prioritized and measured?

### Professional Scenario

You are advising **a population health team prioritizing outreach for patients with elevated near-term risk**. The immediate task is to decide what evidence would make a recommendation credible, what risks remain unresolved, and what should happen next. The module's work product is: **risk stratification brief with equity checks, intervention criteria, and monitoring plan focused on intervention targeting and evaluation: Design an intervention evaluation plan.**.

The available lab data is deliberately limited: synthetic patient-level risk factors including utilization, chronic-condition count, access burden, and prior intervention. Treat it as a proxy for reasoning and method practice, not as proof that a real deployment is ready. A graduate-level submission must distinguish between what the proxy exercise demonstrates and what would still require institutional data, stakeholder review, and operational testing.

### Core Concepts

- **Problem framing:** define the decision, population, workflow, or system boundary before choosing a method.
- **Baseline discipline:** compare the proposed AI-enabled approach with an existing process, simple rule, or manual review pattern.
- **Evidence quality:** separate measured results from assumptions, anecdotes, vendor claims, and synthetic-data artifacts.
- **Failure modes:** identify where the system can fail technically, operationally, legally, ethically, or socially.
- **Deployment readiness:** connect metrics to decision thresholds, monitoring, escalation, and rollback.

## Why This Module Matters

In **AINS6101: Predictive Analytics in Population Health**, this module contributes to the larger course arc by requiring students to turn a domain problem into an inspectable technical artifact. The standard is not "the notebook ran." The standard is that another reviewer can understand the decision, reproduce the reasoning, and challenge the assumptions.

### Method Pattern

1. State the stakeholder decision in one sentence.
2. Identify the evidence source and why it is adequate or inadequate.
3. Produce a baseline result using the lab or an equivalent transparent method.
4. Compare one alternative design, threshold, policy, or model.
5. Document false positives, false negatives, unintended incentives, and operational constraints.
6. Recommend a next action: continue research, run a controlled pilot, redesign the system, or stop.

### Failure Modes To Check

- **Measurement mismatch:** the metric optimizes something adjacent to, but not identical with, the real decision.
- **Context loss:** important operational or human factors are absent from the data.
- **Automation bias:** users may over-trust a score, classification, or recommendation.
- **Equity and access risk:** affected groups may experience different error rates or burdens.
- **Governance gap:** no one owns monitoring, escalation, or rollback after launch.

## Study Questions

1. What decision does the module artifact support?
2. What does the proxy lab evidence prove, and what does it not prove?
3. Which baseline or manual process should the AI-enabled approach be compared against?
4. Which stakeholder would object to the recommendation, and on what grounds?
5. What monitoring signal would tell you the system is failing after deployment?
