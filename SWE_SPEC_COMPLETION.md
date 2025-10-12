# SWE Specification - Remaining Sections (8.2 - 19)

This document contains the completion of the U-AIP Scoping Assistant SWE Specification.

---

## 8.2 Complete Stage 1 Conversation Flow

**USER TYPES:**
```
Customer Churn Prediction System
```

```
✓ Project name set: "Customer Churn Prediction System"

╔════════════════════════════════════════════════════════════╗
║  STAGE 1 OF 5: BUSINESS TRANSLATION                       ║
║  Goal: Define your AI problem with precision               ║
╚════════════════════════════════════════════════════════════╝

Progress: [████░░░░░░░░░░░░░░░░] 5% complete
Estimated time: 10-12 minutes

Let's start with question group 1: Core Business Objective

Question 1/10: What is the overarching business objective or operational
pain point this AI project aims to address?

Be specific about the problem you're trying to solve.
```

**USER TYPES (First Attempt - VAGUE):**
```
We want to improve customer retention
```

**SYSTEM RESPONSE (Quality Reflection Triggered):**
```
⚠️  Response needs more specificity (Quality Score: 4/10)

Issues identified:
- "Improve customer retention" is too broad and not measurable
- No baseline or target mentioned
- Doesn't specify which aspect of retention (timing, segment, channel)

Let me ask some clarifying questions to get more precise information:

Follow-up 1a: What specific metric do you use to measure customer retention?
(Examples: churn rate %, customer lifetime value, repeat purchase rate,
annual retention rate by cohort)
```

**USER TYPES (Clarification):**
```
We track monthly churn rate - currently it's around 5.2% per month
```

**SYSTEM:**
```
✓ Good! Now I understand you're focused on churn rate.

Follow-up 1b: What is your target churn rate, and by when do you want to
achieve it?
```

**USER TYPES:**
```
We'd like to reduce it to 3.5% within 6 months
```

**SYSTEM:**
```
✓ Excellent! (Quality Score: 8/10 - Accepted)

Summary of Business Objective:
"Reduce monthly customer churn rate from current baseline of 5.2% to 3.5%
within 6 months"

Progress: [████████░░░░░░░░░░░░] 10% complete

Moving to Question 2/10...

Question 2/10: Can this problem be solved effectively using simpler methods
like deterministic rules, traditional software, or basic statistical analysis?
Or is AI/ML genuinely required?

In other words: Why do you need AI for this?
```

**USER TYPES:**
```
We've tried rule-based approaches - like flagging customers who haven't
logged in for 30 days - but they're too simplistic. Churn patterns are
complex and involve multiple signals: usage frequency, support tickets,
billing issues, feature adoption, etc. We need ML to find patterns we're
missing.
```

**SYSTEM:**
```
✓ Strong justification! (Quality Score: 9/10)

You've identified:
- Existing simpler methods were attempted
- Problem has multiple interacting variables
- Pattern complexity exceeds rule-based logic
- Clear need for ML pattern recognition

Progress: [████████████░░░░░░░░] 20% complete

Question 3/10: Let's define your INPUT FEATURES. What specific data variables
will the model use to make predictions?

List all data points you plan to include (demographics, behavior, transaction
history, etc.)
```

**USER TYPES:**
```
- Customer demographics (age, location, account type)
- Usage metrics (login frequency, feature usage, session duration)
- Transaction history (payment method, billing cycle, failed payments)
- Support interactions (ticket count, resolution time, NPS scores)
- Product engagement (features used, onboarding completion)
```

**SYSTEM:**
```
✓ Good feature list! (Quality Score: 7/10)

Follow-up 3a: For PRODUCTION deployment, will ALL these features be
available in real-time when you need to make a prediction?

This is critical: if you train on data that won't be available at inference
time, your model will fail in production.

Are there any features that might have:
- High latency (slow to retrieve)?
- Availability delays (only updated weekly/monthly)?
- Access restrictions in production environment?
```

**USER TYPES:**
```
Good point. Support ticket resolution time might have a lag - tickets aren't
closed immediately. We should exclude that. Everything else is real-time from
our customer data platform.
```

**SYSTEM:**
```
✓ Excellent catch! (Quality Score: 9/10)

Validated Input Features (Production-Ready):
✓ Customer demographics - Available, <100ms latency
✓ Usage metrics - Available, real-time
✓ Transaction history - Available, <200ms latency
✓ Support ticket COUNT - Available, real-time
✗ Support resolution time - EXCLUDED (availability lag)
✓ Product engagement - Available, real-time
✓ NPS scores - Available (last 90 days)

Progress: [████████████████░░░░] 30% complete

Question 4/10: What is the TARGET OUTPUT? What specifically will the model
predict?
```

**USER TYPES:**
```
Predict whether a customer will churn within the next 30 days
```

**SYSTEM:**
```
✓ Clear target! (Quality Score: 8/10)

Output Definition:
- Type: Binary Classification
- Classes: [Will Churn, Won't Churn] within 30-day window
- Format: Probability score (0.0 - 1.0)

Progress: [████████████████████] 40% complete

Question 5/10: Based on your inputs and output, what ML ARCHETYPE best
describes this task?

Options:
a) Classification (predicting categories)
b) Regression (predicting numbers)
c) Clustering (grouping similar items)
d) Recommendation System
e) Anomaly Detection
f) Other
```

**USER TYPES:**
```
a) Classification
```

**SYSTEM:**
```
✓ Correct! (Quality Score: 10/10)

ML Archetype Validation:
✓ Binary Classification matches the problem structure
✓ Input features support classification task
✓ Output format (probability) aligns with archetype

Progress: [████████████████████████] 50% complete

[Questions 6-10 continue covering scope boundaries, feature definitions, etc.]

...

╔════════════════════════════════════════════════════════════╗
║  STAGE 1: GATE VALIDATION CHECK                            ║
╚════════════════════════════════════════════════════════════╝

Running stage completion validation...

Checking mandatory requirements:
✓ Business objective clearly defined
✓ AI necessity justified
✓ Input features enumerated and production-validated
✓ Target output precisely defined
✓ ML archetype correctly mapped
✓ Scope boundaries established

Stage 1 Completeness: 100%
Quality Score: 8.5/10

✅ STAGE 1 COMPLETE!

Generating Stage 1 Deliverable: Problem Statement...

┌─────────────────────────────────────────────────────────────┐
│ PROBLEM STATEMENT                                           │
│ Project: Customer Churn Prediction System                   │
│                                                             │
│ Business Objective:                                         │
│ Reduce monthly customer churn rate from 5.2% to 3.5%       │
│ within 6 months                                             │
│                                                             │
│ AI Justification:                                           │
│ Rule-based methods insufficient for complex multi-signal   │
│ churn patterns. ML required for pattern recognition across │
│ behavioral, transactional, and engagement features.        │
│                                                             │
│ ML Archetype: Binary Classification                         │
│ Target: Predict 30-day churn probability                    │
│                                                             │
│ Input Features (7 feature groups, all production-ready)     │
│ Output: Probability score [0.0-1.0]                         │
└─────────────────────────────────────────────────────────────┘

Progress: [████████████████████████░░░░░░░░░░░░] Stage 1 of 5 complete

💾 Auto-saved: Session checkpoint created

Ready to proceed to Stage 2: Value Quantification?
Type 'yes' to continue, or 'review' to see Stage 1 details again.
```

**USER TYPES:**
```
yes
```

```
╔════════════════════════════════════════════════════════════╗
║  STAGE 2 OF 5: VALUE QUANTIFICATION                        ║
║  Goal: Define measurable success criteria                  ║
╚════════════════════════════════════════════════════════════╝

[Stage 2 conversation continues...]
```

---

## 8.3 Stage Transition and Gate Validation Example

### Scenario: User Tries to Proceed with Incomplete Stage

```
[User has completed 8 of 10 Stage 1 questions]

User: skip to stage 2

System:
❌ Cannot proceed to Stage 2 yet.

Stage 1 is incomplete (80% complete):

Missing required information:
- Scope boundaries not defined (Question 9)
- Feature availability validation incomplete (Question 10)

These are mandatory for Stage 1 completion. Would you like to:
a) Continue with remaining Stage 1 questions
b) Review what you've completed so far
c) Save and pause session

Your choice:
```

---

## 8.4 Session Pause and Resume Example

### Pausing Mid-Session

```
[User is in middle of Stage 3]

User: pause

System:
⏸️  Pausing session...

💾 Session saved successfully!
   Session ID: uaip-20251012-a4f2d8
   Current progress: Stage 3 (Data Feasibility) - 60% complete
   Last updated: 2025-10-12 14:32:18

To resume this session later:
$ python -m uaip_assistant resume uaip-20251012-a4f2d8

Or list all your sessions:
$ python -m uaip_assistant list

Goodbye!
```

### Resuming Session

```bash
$ python -m uaip_assistant resume uaip-20251012-a4f2d8

╔════════════════════════════════════════════════════════════╗
║     Resuming Session                                       ║
╚════════════════════════════════════════════════════════════╝

Project: Customer Churn Prediction System
Session ID: uaip-20251012-a4f2d8
Started: 2025-10-12 13:15:42
Last checkpoint: 2025-10-12 14:32:18

Progress Summary:
  ✅ Stage 1: Business Translation (Complete)
  ✅ Stage 2: Value Quantification (Complete)
  ⏳ Stage 3: Data Feasibility (60% complete)
  ⬜ Stage 4: User Context (Not started)
  ⬜ Stage 5: Ethics & Risk (Not started)

Resuming at Stage 3, Question 6/10...

[Conversation continues from where it left off]
```

---

## 8.5 Final Charter Generation Example

### After Completing All 5 Stages

```
╔════════════════════════════════════════════════════════════╗
║  ALL STAGES COMPLETE!                                      ║
╚════════════════════════════════════════════════════════════╝

Progress: [████████████████████████████████████] 100%

✅ Stage 1: Business Translation
✅ Stage 2: Value Quantification
✅ Stage 3: Data Feasibility
✅ Stage 4: User Context
✅ Stage 5: Ethics & Risk

Running final cross-stage consistency check...

Validating alignment:
✓ Stage 2 KPIs solve Stage 1 problem
✓ Stage 3 data supports Stage 2 metrics
✓ Stage 4 users can access Stage 3 data
✓ Stage 5 ethical risks match project scope

Consistency Check: ✅ PASSED

Calculating governance decision...

Residual Risk Assessment:
- Fairness & Equity: MEDIUM
- Privacy Protection: LOW
- Transparency: LOW
- Safety & Resilience: LOW
- Human Agency: LOW

Maximum Residual Risk: MEDIUM

🎯 GOVERNANCE DECISION: PROCEED WITH MONITORING

Your project can move forward with the following requirements:
- Implement continuous monitoring for bias/fairness
- Quarterly ethical risk reassessments
- Document all mitigation strategies

Generating AI Project Charter...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ AI PROJECT CHARTER GENERATED SUCCESSFULLY ✨

Project: Customer Churn Prediction System
Session ID: uaip-20251012-a4f2d8
Generated: 2025-10-12 15:47:33
Governance Decision: PROCEED WITH MONITORING

Charter includes:
- Executive Summary
- Problem Definition
- Value & Metrics Alignment
- Data Feasibility Assessment
- User Context & Journey
- Ethical Risk Analysis
- Operational Strategy
- APA 7 Citations

Available formats:
1. Markdown (.md)
2. PDF (.pdf)
3. JSON (.json)

Would you like to:
a) Export charter (specify format)
b) Review charter sections
c) Email charter to stakeholders
d) Start a new project evaluation

Your choice:
```

**USER TYPES:**
```
a
```

```
Select export format:
1. Markdown (.md) - Human-readable, version-control friendly
2. PDF (.pdf) - Professional, ready to share with executives
3. JSON (.json) - Machine-readable, integration-friendly
4. All formats

Your choice: 2

Generating PDF...

✓ Charter exported successfully!

📄 File saved: ./charters/Customer_Churn_Prediction_Charter_20251012.pdf
   Size: 847 KB
   Pages: 24

You can also access this charter anytime:
$ python -m uaip_assistant export uaip-20251012-a4f2d8 --format pdf

Would you like to:
a) Start another project evaluation
b) View session history
c) Exit

Your choice:
```

---

## 9. Quality Assurance & Validation

### 9.1 Reflection Agent Testing Strategy

**Objective:** Ensure reflection agents correctly identify response quality issues

#### 9.1.1 Response Quality Agent Tests

**Test Cases:**

| Input Response | Expected Score | Expected Issues | Expected Follow-ups |
|----------------|---------------|-----------------|---------------------|
| "Improve efficiency" | 2-3/10 | Vague, not measurable | What metric defines efficiency? Current baseline? |
| "Reduce claim processing time from 14 days to 7 days" | 8-9/10 | None (maybe ask about feasibility) | Minor clarification only |
| "Use AI for predictions" | 1/10 | Circular, no substance | What are you predicting? From what inputs? |
| "Predict customer LTV using demographics, purchase history, and engagement data" | 9-10/10 | None | None needed |

**Test Implementation (TDD):**
```python
def test_response_quality_agent_rejects_vague_responses():
    """Response quality agent must reject vague responses"""
    agent = ResponseQualityAgent()

    assessment = agent.evaluate(
        question="What is your business objective?",
        response="Improve efficiency"
    )

    assert assessment.quality_score < 5
    assert not assessment.is_acceptable
    assert "vague" in " ".join(assessment.issues).lower()
    assert len(assessment.suggested_followups) >= 2
```

#### 9.1.2 Stage Gate Validator Tests

**Test Case: Incomplete Stage 1**
```python
def test_stage_gate_rejects_incomplete_stage1():
    """Stage gate must reject Stage 1 without all required fields"""
    validator = StageGateValidatorAgent()

    incomplete_data = {
        "business_objective": "Reduce churn",
        "input_features": ["demographics"],
        # Missing: ai_justification, target_output, ml_archetype
    }

    validation = validator.validate_stage_completion(1, incomplete_data)

    assert not validation.can_proceed
    assert "ai_justification" in validation.missing_items
    assert "target_output" in validation.missing_items
```

#### 9.1.3 Consistency Checker Tests

**Test Case: Stage 1-2 Misalignment**
```python
def test_consistency_checker_detects_kpi_problem_mismatch():
    """Consistency checker must detect when KPIs don't solve stated problem"""
    checker = ConsistencyCheckerAgent()

    all_stages = {
        "stage1": {
            "business_objective": "Reduce customer churn rate"
        },
        "stage2": {
            "kpis": [
                {"name": "Increase website traffic by 50%"}  # Wrong KPI!
            ]
        }
    }

    report = checker.check_cross_stage_consistency(all_stages)

    assert not report.is_consistent
    assert any("kpi" in c.lower() and "problem" in c.lower()
               for c in report.contradictions)
```

### 9.2 End-to-End Integration Tests

#### Test: Complete Session Flow
```python
@pytest.mark.asyncio
async def test_complete_session_flow():
    """Test full user journey from start to charter generation"""
    orchestrator = UAIPOrchestrator()

    session_id = await orchestrator.initialize_session({
        "user_id": "test_user",
        "project_name": "Test Project"
    })

    # Simulate Stage 1
    stage1_data = await orchestrator.conduct_stage(1, mock_user_responses_stage1)
    assert stage1_data.is_complete

    # Simulate Stages 2-5
    for stage_num in range(2, 6):
        stage_data = await orchestrator.conduct_stage(
            stage_num,
            mock_user_responses[stage_num]
        )
        assert stage_data.is_complete

    # Generate charter
    charter = await orchestrator.conduct_full_protocol()

    assert charter.governance_decision in GovernanceDecision
    assert len(charter.problem_statement.input_features) > 0
    assert charter.ethical_risk_report is not None
```

### 9.3 Quality Metrics

**Definition of Success:**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Response quality improvement rate | >50% | % of vague responses caught and improved |
| Stage gate false negative rate | <5% | Incomplete stages that pass validation |
| Consistency check accuracy | >95% | Correctly identified contradictions |
| User satisfaction with quality checks | >7/10 | Post-session survey |

---

## 10. Output Specifications

### 10.1 AI Project Charter Structure

**Complete 8-Section Document:**

```markdown
# AI Project Charter: [Project Name]

**Document ID:** [Charter ID]
**Session ID:** [Session UUID]
**Generated:** [Timestamp]
**Governance Decision:** [PROCEED/PROCEED_WITH_MONITORING/REVISE/HALT]
**Version:** 1.0

---

## Executive Summary

[Auto-generated 2-3 paragraph summary covering:
- Business problem and AI approach
- Key metrics and expected impact
- Major risks and mitigation strategies
- Governance decision rationale]

### Quick Facts

| Attribute | Value |
|-----------|-------|
| ML Archetype | [Classification/Regression/etc.] |
| Primary KPI | [KPI name and target] |
| Data Quality Score | [Average across 6 dimensions] |
| Ethical Risk Level | [Residual risk rating] |
| Decision | [Governance decision] |

---

## 1. Strategic Alignment

### 1.1 Business Objectives

[Stage 1 business objective - detailed statement]

**Problem Context:**
[Why this problem matters, current pain points]

### 1.2 Success Criteria (KPIs)

| KPI | Current Baseline | Target | Timeframe | Impact |
|-----|-----------------|--------|-----------|--------|
| [KPI 1] | [Value] | [Value] | [Timeline] | [$ or % impact] |
| [KPI 2] | [Value] | [Value] | [Timeline] | [$ or % impact] |

**Projected ROI:**
[If calculable, estimated financial impact]

---

## 2. Problem Definition

### 2.1 AI Problem Statement

[Complete problem statement from Stage 1]

**Why AI/ML is Required:**
[Justification for using AI vs. simpler methods]

### 2.2 ML Archetype Mapping

**Archetype:** [e.g., Binary Classification]

**Justification:**
[Why this archetype fits the problem structure]

### 2.3 Input-Output Specification

**Input Features** (Production-Validated):

| Feature Group | Features | Data Type | Source | Latency |
|--------------|----------|-----------|--------|---------|
| Demographics | Age, Location, Segment | Numeric/Categorical | CRM | <100ms |
| Behavioral | Login freq, Session duration | Numeric | Analytics | Real-time |
| [etc.] | [...] | [...] | [...] | [...] |

**Target Output:**
- **Type:** [Categorical/Continuous/Probability]
- **Description:** [What is being predicted]
- **Format:** [Output format specification]

### 2.4 Scope & Boundaries

**In Scope:**
- [What the project will address]

**Out of Scope:**
- [What the project will NOT address]

**Assumptions:**
- [Key assumptions made during scoping]

---

## 3. Technical Feasibility Assessment

### 3.1 Data Inventory

| Data Source | Type | Size | Update Frequency | Access Method |
|-------------|------|------|------------------|---------------|
| [Source 1] | [DB/API/File] | [Records] | [Real-time/Daily] | [SQL/REST] |
| [Source 2] | [...] | [...] | [...] | [...] |

### 3.2 Data Quality Scorecard

**Six Dimensions Assessment:**

| Dimension | Score (0-10) | Notes |
|-----------|--------------|-------|
| Accuracy | [Score] | [Assessment details] |
| Consistency | [Score] | [Assessment details] |
| Completeness | [Score] | [Assessment details] |
| Timeliness | [Score] | [Assessment details] |
| Validity | [Score] | [Assessment details] |
| Integrity | [Score] | [Assessment details] |

**Overall Data Quality:** [Average score]/10

**Critical Issues:**
- [Any scores below 6/10 flagged as risks]

### 3.3 Labeling Strategy

**Approach:** [In-house / Outsourced / Automated / Hybrid]

**Requirements:**
- **Volume needed:** [Number of labeled examples]
- **Estimated cost:** [$X or time investment]
- **Timeline:** [Weeks/months to completion]
- **Quality control:** [Validation methodology]

### 3.4 Infrastructure Readiness

**Current State:**
[Assessment of existing AI/ML infrastructure]

**Gaps Identified:**
- [Any infrastructure bottlenecks]

---

## 4. User Context and Interaction

### 4.1 Primary User Persona

**Name:** [Persona name/title]
**Role:** [Job function]

**Goals:**
- [Primary user goals]

**Pain Points:**
- [Current challenges]

**Technical Proficiency:** [Novice/Intermediate/Expert]
**Decision Authority:** [Level of autonomy]

**AI Interaction Frequency:** [Daily/Weekly/Monthly]

[Additional personas if defined...]

### 4.2 AI User Journey Map

**Pre-Interaction:**
[User state before encountering AI]

**During Interaction:**
[How user interacts with AI system]

**Post-Interaction:**
[Actions taken based on AI output]

**Key Touchpoints:**
1. [Touchpoint 1]
2. [Touchpoint 2]
3. [Touchpoint 3]

### 4.3 Interpretability & Usability Requirements

**Required Interpretability Level:** [None/Low/Medium/High]

**Explainability Features:**
- [e.g., SHAP values, feature importance, narrative explanations]

**Usability Requirements:**
- [Interface requirements]
- [Response time requirements]
- [Accessibility needs]

---

## 5. Metric Alignment Matrix

### 5.1 Business-Technical Metric Mapping

| Business KPI | Technical Metric | Causal Pathway | Assumptions | Failure Modes |
|--------------|------------------|----------------|-------------|---------------|
| [KPI 1] | [Metric like F1] | [How metric → KPI] | [Key assumptions] | [Potential issues] |
| [KPI 2] | [Metric like RMSE] | [How metric → KPI] | [Key assumptions] | [Potential issues] |

### 5.2 Prediction Actionability Window

**Time Available:** [Duration between prediction and action deadline]
**Prediction Latency:** [Model inference time + data retrieval]
**Margin:** [Buffer time]

✓ Actionability window is sufficient / ⚠️ Tight timeline / ❌ Insufficient

### 5.3 Causal Impact Validation Plan

**Post-Deployment Strategy:**
[How true causal impact will be measured]

**Methodology:** [A/B testing / Causal Impact / DML / other]

---

## 6. Ethical Risk Assessment

### 6.1 Risk Framework

Assessment based on: [NIST AI RMF / AIAF / Other framework]

### 6.2 Principle-Specific Risk Analysis

#### Fairness & Equity
**Initial Risk:** [LOW/MEDIUM/HIGH]
**Risk Description:** [Specific fairness concerns]
**Mitigation Strategies:**
- [Strategy 1]
- [Strategy 2]
**Residual Risk:** [LOW/MEDIUM/HIGH]

#### Privacy & Data Protection
**Initial Risk:** [LOW/MEDIUM/HIGH]
**Risk Description:** [Privacy concerns]
**Mitigation Strategies:**
- [Strategy 1]
- [Strategy 2]
**Residual Risk:** [LOW/MEDIUM/HIGH]

#### Transparency & Accountability
**Initial Risk:** [LOW/MEDIUM/HIGH]
**Risk Description:** [Transparency issues]
**Mitigation Strategies:**
- [Strategy 1]
**Residual Risk:** [LOW/MEDIUM/HIGH]

#### Safety & Resilience
**Initial Risk:** [LOW/MEDIUM/HIGH]
**Risk Description:** [Safety concerns]
**Mitigation Strategies:**
- [Strategy 1]
**Residual Risk:** [LOW/MEDIUM/HIGH]

#### Human Agency & Oversight
**Initial Risk:** [LOW/MEDIUM/HIGH]
**Risk Description:** [Automation concerns]
**Mitigation Strategies:**
- [Strategy 1]
**Residual Risk:** [LOW/MEDIUM/HIGH]

### 6.3 Residual Risk Summary

**Maximum Residual Risk:** [MEDIUM]

**Principles at MEDIUM or Higher:**
- [List any principles with MEDIUM/HIGH residual risk]

### 6.4 Governance Checkpoint Decision

╔══════════════════════════════════════════════════════════╗
║  DECISION: PROCEED WITH MONITORING                       ║
╚══════════════════════════════════════════════════════════╝

**Rationale:**
[Explanation of why this decision was made]

**Conditions for Proceeding:**
- [Condition 1 - e.g., implement fairness monitoring]
- [Condition 2 - e.g., quarterly ethical reviews]
- [Condition 3 - e.g., document all mitigation implementations]

**Escalation Criteria:**
[Conditions that would require project halt or committee review]

---

## 7. Operational Strategy

### 7.1 Continuous Monitoring Plan

**Model Drift Monitoring:**
- Frequency: [Daily/Weekly]
- Metrics tracked: [Performance metrics]
- Alert thresholds: [Threshold values]

**Data Drift Monitoring:**
- Frequency: [Daily/Weekly]
- Features monitored: [Critical features]
- Statistical tests: [KS test, PSI, etc.]

**Fairness Monitoring:**
- Frequency: [Weekly/Monthly]
- Protected attributes: [List]
- Fairness metrics: [Demographic parity, equal opportunity, etc.]

### 7.2 Maintenance & Retraining

**Retraining Triggers:**
- Performance degrades below [threshold]
- Data distribution shifts detected
- [Time-based: every X months]

**Retraining Process:**
[Brief description of retraining workflow]

### 7.3 Incident Response

**If Model Fails:**
1. [Step 1 - immediate action]
2. [Step 2 - investigation]
3. [Step 3 - remediation]

**Escalation Path:**
[Who to notify and when]

---

## 8. References

[Auto-generated APA 7 citations]

Example:
```
Barocas, S., Hardt, M., & Narayanan, A. (2019). Fairness and machine learning:
    Limitations and opportunities. MIT Press.

National Institute of Standards and Technology. (2023). AI Risk Management
    Framework (AI RMF 1.0). U.S. Department of Commerce.
    https://doi.org/10.6028/NIST.AI.100-1
```

---

## Appendices

### Appendix A: Session Conversation Log
[Optional: Full Q&A transcript]

### Appendix B: Validation Reports
[Detailed validation outputs from reflection agents]

---

**Document Generated By:** U-AIP Scoping Assistant v1.0
**Generation Date:** [Timestamp]
**Session Duration:** [Minutes]

---

**Charter Approval:**

Approved by: ___________________________ Date: __________

Title: ___________________________

Signature: ___________________________
```

### 10.2 Export Formats

#### 10.2.1 Markdown (.md)
- Human-readable format
- Version control friendly (Git)
- Easy to convert to other formats

#### 10.2.2 PDF (.pdf)
- Professional appearance
- Executive-ready
- Includes proper formatting, headers, page numbers
- Generated using: WeasyPrint or Pandoc

#### 10.2.3 JSON (.json)
- Machine-readable structured data
- Integration-friendly
- Enables programmatic access to charter components

**JSON Structure:**
```json
{
  "charter_id": "charter-20251012-a4f2d8",
  "session_id": "uaip-20251012-a4f2d8",
  "project_name": "Customer Churn Prediction System",
  "generated_at": "2025-10-12T15:47:33Z",
  "governance_decision": "PROCEED_WITH_MONITORING",
  "stage1": {
    "business_objective": "...",
    "ai_justification": "...",
    "ml_archetype": "classification",
    "input_features": [...]
  },
  "stage2": {...},
  "stage3": {...},
  "stage4": {...},
  "stage5": {
    "residual_risks": {
      "fairness_equity": "MEDIUM",
      "privacy_protection": "LOW",
      ...
    },
    "governance_decision": "PROCEED_WITH_MONITORING"
  }
}
```

---

## 11. Technology Stack

### 11.1 Core Framework
- **Claude Agent SDK (Python)**: v0.x.x
  - Agent orchestration
  - Conversation management
  - Tool integration

### 11.2 Language & Runtime
- **Python**: 3.11+
- **Environment Manager**: `uv` (per CLAUDE.md requirements)
- **Package Management**: `pyproject.toml`

### 11.3 Database
- **PostgreSQL**: 15+
  - Session persistence
  - Conversation history
  - Charter storage
- **Connection Pool**: `asyncpg`

### 11.4 Document Generation
- **Markdown Processing**: `markdown-it-py`
- **PDF Generation**: `WeasyPrint` or `Pandoc`
- **Citation Formatting**: Custom APA 7 formatter

### 11.5 CLI Framework
- **Rich**: Terminal formatting, progress bars
- **Click** or **Typer**: Command-line interface
- **Prompt_toolkit**: Interactive input

### 11.6 Testing
- **pytest**: Unit and integration testing
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage
- **faker**: Test data generation

### 11.7 Containerization
- **Docker**: 24+
- **Docker Compose**: v2+
- **Base Images**:
  - `python:3.11-slim` for application
  - `postgres:15-alpine` for database

### 11.8 API Client
- **Anthropic SDK**: Latest Claude API client
- **httpx**: Async HTTP requests

### 11.9 Configuration
- **YAML**: `pyyaml` for config files
- **Pydantic**: Settings validation and env management
- **python-dotenv**: Environment variables

### 11.10 Logging & Monitoring
- **structlog**: Structured logging
- **prometheus-client**: Metrics export (for global monitoring stack per CLAUDE.md)

### 11.11 Development Tools
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

### 11.12 Dependencies Summary

**pyproject.toml:**
```toml
[project]
name = "uaip-scoping-assistant"
version = "1.0.0"
description = "AI Project Scoping Assistant using Claude Agent SDK"
requires-python = ">=3.11"

dependencies = [
    "anthropic>=0.18.0",
    "claude-agent-sdk>=0.1.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    "rich>=13.7.0",
    "click>=8.1.7",
    "httpx>=0.26.0",
    "structlog>=24.1.0",
    "markdown-it-py>=3.0.0",
    "weasyprint>=60.2",
    "prometheus-client>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.1.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "faker>=22.0.0",
    "pre-commit>=3.6.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term"

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 12. Development Phases

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Core infrastructure and orchestrator

**Deliverables:**
- Project structure setup
- Database schema implementation
- Orchestrator agent skeleton
- Session management system
- Basic CLI interface
- Docker containerization

**TDD Requirements:**
- Test orchestrator initialization
- Test session CRUD operations
- Test database connectivity
- Test container health checks

**Completion Criteria:**
- ✓ Can start/save/resume sessions
- ✓ Database persists session state
- ✓ Docker containers run successfully
- ✓ 80%+ test coverage

---

### Phase 2: Stage Interview Agents (Weeks 3-4)

**Goal:** Implement all 5 stage agents

**Week 3: Stages 1-2**
- Stage1BusinessTranslationAgent
  - 4 question groups
  - ML archetype validation
  - Feature availability checker
- Stage2ValueQuantificationAgent
  - KPI validation
  - Metric alignment logic
  - Causal pathway mapping

**Week 4: Stages 3-5**
- Stage3DataFeasibilityAgent
  - 6-dimension quality assessment
  - Labeling strategy planner
- Stage4UserCentricityAgent
  - Persona templates
  - Journey map structure
- Stage5EthicsAgent
  - Risk assessment questionnaire
  - Residual risk calculator
  - Governance decision engine

**TDD Requirements:**
- Test each question flow
- Test deliverable generation
- Test stage-specific validations
- Mock user responses for testing

**Completion Criteria:**
- ✓ All 5 agents ask mandated questions
- ✓ All agents generate correct deliverables
- ✓ Stage-specific validation logic works
- ✓ 80%+ test coverage per agent

---

### Phase 3: Reflection Agent System (Week 5)

**Goal:** Quality assurance automation

**Deliverables:**
- ResponseQualityAgent
  - Quality scoring algorithm
  - Follow-up generation logic
- StageGateValidatorAgent
  - Stage completion checkers
  - Missing field detection
- ConsistencyCheckerAgent
  - Cross-stage alignment validation
  - Contradiction detection

**TDD Requirements:**
- Test quality scoring accuracy
- Test stage gate rejection scenarios
- Test consistency detection
- Test reflection loop limits (max 3)

**Completion Criteria:**
- ✓ Correctly scores response quality
- ✓ Prevents incomplete stage progression
- ✓ Detects cross-stage contradictions
- ✓ 85%+ test coverage

---

### Phase 4: Document Generation (Week 6)

**Goal:** Charter creation and export

**Deliverables:**
- Charter template system
- APA 7 citation formatter
- Markdown generator
- PDF generator
- JSON exporter

**TDD Requirements:**
- Test charter completeness
- Test APA citation formatting
- Test PDF generation pipeline
- Test export format validation

**Completion Criteria:**
- ✓ Generates complete 8-section charter
- ✓ All export formats work
- ✓ APA 7 citations correctly formatted
- ✓ 80%+ test coverage

---

### Phase 5: Integration & Polish (Week 7)

**Goal:** End-to-end testing and UX improvements

**Deliverables:**
- E2E integration tests
- CLI UX enhancements (progress bars, colors)
- Error handling improvements
- Performance optimization
- Documentation

**TDD Requirements:**
- Test complete session flows
- Test error recovery
- Test concurrent sessions
- Load testing

**Completion Criteria:**
- ✓ Full session completes successfully
- ✓ Handles errors gracefully
- ✓ Meets performance requirements
- ✓ 80%+ overall test coverage

---

### Phase 6: Deployment Prep (Week 8)

**Goal:** Production-ready deployment

**Deliverables:**
- Docker Compose configuration
- Environment variable management
- Health check endpoints
- Monitoring integration (Prometheus metrics)
- Deployment documentation

**Completion Criteria:**
- ✓ Docker Compose starts all services
- ✓ Database migrations automated
- ✓ Metrics exported to Prometheus
- ✓ Deployment guide complete

---

## 13. Testing Strategy (TDD Compliance)

### 13.1 TDD Methodology (Per CLAUDE.md)

**NON-NEGOTIABLE RULES:**
1. ✅ Write tests FIRST before implementation
2. ✅ Use conditional imports for components not yet built
3. ✅ Specification tests pass immediately (always passing)
4. ✅ Implementation tests skip until component exists
5. ✅ Red-Green-Refactor cycle enforced

### 13.2 Test Structure

```
tests/
├── test_orchestrator.py
│   ├── TestOrchestratorSpecification (always passing)
│   ├── TestOrchestratorStructure (skipped until impl)
│   ├── TestOrchestratorExecution (skipped until impl)
│   └── TestOrchestratorIntegration (skipped until impl)
│
├── agents/
│   ├── test_stage1_agent.py
│   ├── test_stage2_agent.py
│   ├── test_stage3_agent.py
│   ├── test_stage4_agent.py
│   ├── test_stage5_agent.py
│   ├── test_response_quality_agent.py
│   ├── test_stage_gate_validator.py
│   └── test_consistency_checker.py
│
├── tools/
│   ├── test_validators.py
│   ├── test_calculators.py
│   └── test_document_generator.py
│
├── integration/
│   ├── test_complete_session_flow.py
│   ├── test_reflection_loops.py
│   └── test_stage_transitions.py
│
└── fixtures/
    ├── mock_responses.py
    └── test_data.py
```

### 13.3 Test Example (TDD Pattern)

**File: `tests/agents/test_stage1_agent.py`**

```python
"""
TDD tests for Stage1BusinessTranslationAgent
Following CLAUDE.md TDD requirements
"""
import pytest
from uuid import uuid4

# Conditional import - component may not exist yet
try:
    from src.agents.stage1_agent import Stage1BusinessTranslationAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    class Stage1BusinessTranslationAgent:
        pass

class TestStage1Specification:
    """
    Specification tests - ALWAYS PASSING
    Documents requirements and expected behavior
    """

    def test_stage1_requirements_specification(self):
        """Document Stage 1 agent requirements"""
        requirements = {
            "purpose": "Translate business needs into AI problem statements",
            "question_groups": 4,
            "deliverable": "ProblemStatement object",
            "critical_validations": [
                "ML archetype matches inputs/outputs",
                "All features production-accessible",
                "AI necessity justified"
            ]
        }
        assert requirements["question_groups"] == 4
        assert "ProblemStatement" in requirements["deliverable"]

    def test_stage1_workflow_position(self):
        """Stage 1 is first in U-AIP protocol"""
        assert 1 == 1  # Stage 1 comes first
        # Stage 1 outputs feed into Stage 2 metric definition

class TestStage1Structure:
    """
    Structure tests - SKIPPED until implementation
    """

    @pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
    def test_agent_has_required_methods(self):
        """Agent must implement required interface methods"""
        agent = Stage1BusinessTranslationAgent()
        assert hasattr(agent, "ask_question")
        assert hasattr(agent, "validate_response")
        assert hasattr(agent, "generate_deliverable")

    @pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
    def test_agent_has_question_groups(self):
        """Agent must have 4 question groups defined"""
        agent = Stage1BusinessTranslationAgent()
        assert len(agent.question_groups) == 4

class TestStage1Execution:
    """
    Execution tests - SKIPPED until implementation
    """

    @pytest.fixture
    def agent(self):
        if not AGENT_AVAILABLE:
            pytest.skip("Stage1Agent not implemented yet")
        return Stage1BusinessTranslationAgent()

    @pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
    async def test_successful_problem_statement_generation(self, agent):
        """Agent generates ProblemStatement with valid inputs"""
        responses = {
            "business_objective": "Reduce churn from 5.2% to 3.5%",
            "ai_justification": "Complex multi-signal patterns exceed rules",
            "input_features": ["demographics", "behavior", "transactions"],
            "target_output": "30-day churn probability",
            "ml_archetype": "classification"
        }

        problem_statement = await agent.generate_deliverable(responses)

        assert problem_statement.business_objective == responses["business_objective"]
        assert problem_statement.ml_archetype == "classification"
        assert len(problem_statement.input_features) > 0

class TestStage1Integration:
    """
    Integration tests - SKIPPED until implementation
    """

    @pytest.mark.skipif(not AGENT_AVAILABLE, reason="Stage1Agent not implemented yet")
    async def test_integration_with_response_quality_agent(self, agent):
        """Stage 1 agent integrates with quality reflection"""
        from src.agents.response_quality_agent import ResponseQualityAgent

        quality_agent = ResponseQualityAgent()

        question = "What is your business objective?"
        vague_response = "Improve things"

        assessment = await quality_agent.evaluate(question, vague_response)

        assert assessment.quality_score < 7
        assert not assessment.is_acceptable
```

### 13.4 Test Coverage Requirements

| Component Type | Minimum Coverage | Target Coverage |
|----------------|-----------------|-----------------|
| Orchestrator | 85% | 90% |
| Stage Agents | 80% | 85% |
| Reflection Agents | 85% | 90% |
| Tools/Utilities | 80% | 85% |
| Integration Tests | 70% | 80% |
| **Overall** | **80%** | **85%** |

### 13.5 Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only specification tests (should always pass)
uv run pytest -k "Specification"

# Run only non-skipped tests (implemented components)
uv run pytest -v --tb=short

# Run specific test file
uv run pytest tests/agents/test_stage1_agent.py -v
```

---

## 14. Deployment Architecture

### 14.1 Docker Compose Configuration

**Per CLAUDE.md requirements:**
- ✅ All services containerized
- ✅ 5-digit port numbers only (10000-99999)
- ✅ No usage of reserved monitoring ports
- ✅ Integration with global monitoring stack

**File: `docker-compose.yml`**

```yaml
version: "3.9"

services:
  # PostgreSQL Database
  uaip-db:
    image: postgres:15-alpine
    container_name: uaip-postgres
    environment:
      POSTGRES_DB: uaip_assistant
      POSTGRES_USER: uaip_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - uaip-db-data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "15432:5432"  # 5-digit external port
    networks:
      - uaip-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U uaip_user -d uaip_assistant"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # U-AIP Assistant Application
  uaip-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: uaip-assistant
    environment:
      DATABASE_URL: postgresql://uaip_user:${POSTGRES_PASSWORD}@uaip-db:5432/uaip_assistant
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
      PROMETHEUS_PORT: 18080  # Internal metrics port
    volumes:
      - ./charters:/app/charters  # Output directory for generated charters
      - ./config:/app/config:ro   # Read-only config files
    ports:
      - "18000:8000"  # 5-digit external port for API (future web interface)
      - "18080:18080" # Prometheus metrics endpoint
    networks:
      - uaip-network
      - monitoring  # Connect to global monitoring stack
    depends_on:
      uaip-db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=18080"
      - "prometheus.path=/metrics"

volumes:
  uaip-db-data:
    driver: local

networks:
  uaip-network:
    driver: bridge
  monitoring:
    external: true  # Connect to global monitoring stack
    name: global-monitoring-network
```

### 14.2 Dockerfile

```dockerfile
# Multi-stage build for smaller image size
FROM python:3.11-slim AS builder

WORKDIR /build

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -r pyproject.toml

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set virtual environment in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY templates/ /app/templates/

# Create output directories
RUN mkdir -p /app/charters /app/logs

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Health check endpoint (for future web interface)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"  # Replace with actual health check

# Default command (can be overridden)
CMD ["python", "-m", "src.cli.main"]
```

### 14.3 Environment Configuration

**File: `.env.example`**

```bash
# Database Configuration
POSTGRES_PASSWORD=change_me_in_production
DATABASE_URL=postgresql://uaip_user:change_me_in_production@uaip-db:5432/uaip_assistant

# Claude API
ANTHROPIC_API_KEY=sk-ant-api...

# Application Settings
LOG_LEVEL=INFO
MAX_CONCURRENT_SESSIONS=100
SESSION_TIMEOUT_MINUTES=120

# Quality Thresholds
RESPONSE_QUALITY_THRESHOLD=7
MAX_REFLECTION_LOOPS=3

# Monitoring (connects to global stack)
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=18080

# Export Settings
CHARTER_OUTPUT_DIR=/app/charters
DEFAULT_EXPORT_FORMAT=markdown
```

### 14.4 Port Allocation

**U-AIP Assistant Services:**

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| PostgreSQL | 5432 | 15432 | Database access |
| Application API | 8000 | 18000 | Future web interface |
| Prometheus Metrics | 18080 | 18080 | Metrics export to global monitoring |

**Notes:**
- All external ports are 5-digit per CLAUDE.md requirements
- Avoids all reserved global monitoring ports (60000-61100 range)
- Metrics exported to global Prometheus instance

### 14.5 Deployment Commands

```bash
# Initial setup
cp .env.example .env
# Edit .env with actual credentials

# Build and start services
docker compose up -d --build

# Check service health
docker compose ps
docker compose logs -f uaip-app

# Access CLI inside container
docker compose exec uaip-app python -m src.cli.main start

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v

# View logs
docker compose logs -f uaip-app
docker compose logs -f uaip-db

# Database migrations (when schema changes)
docker compose exec uaip-db psql -U uaip_user -d uaip_assistant -f /migrations/001_add_column.sql
```

### 14.6 Database Initialization

**File: `database/init.sql`**

```sql
-- Initialize U-AIP Assistant Database
-- This runs automatically on first container start

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Sessions table (from section 5.3)
CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    project_name VARCHAR(500) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_stage INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_sessions ON sessions(user_id, started_at);
CREATE INDEX idx_status ON sessions(status);

-- Stage data table
CREATE TABLE IF NOT EXISTS stage_data (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    field_value JSONB NOT NULL,
    quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, stage_number, field_name)
);

-- Conversation history
CREATE TABLE IF NOT EXISTS conversation_history (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stage_number INTEGER,
    metadata JSONB
);

CREATE INDEX idx_session_messages ON conversation_history(session_id, timestamp);

-- Checkpoints
CREATE TABLE IF NOT EXISTS checkpoints (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL,
    checkpoint_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_snapshot JSONB NOT NULL,
    validation_passed BOOLEAN NOT NULL
);

-- Generated charters
CREATE TABLE IF NOT EXISTS project_charters (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    charter_content JSONB NOT NULL,
    governance_decision VARCHAR(50) NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    markdown_path VARCHAR(500),
    pdf_path VARCHAR(500),
    version VARCHAR(50) NOT NULL DEFAULT '1.0'
);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to stage_data table
CREATE TRIGGER update_stage_data_updated_at
    BEFORE UPDATE ON stage_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to sessions table
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## 15. Security & Compliance

### 15.1 API Key Management

**Anthropic API Key:**
- ✅ Store in `.env` file (never commit to Git)
- ✅ `.gitignore` includes `.env`
- ✅ Use environment variable injection in Docker
- ✅ Rotate keys regularly (every 90 days recommended)

**File: `.gitignore`**
```
.env
.env.local
*.key
*.pem
charters/*
!charters/.gitkeep
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
```

### 15.2 Data Encryption

#### At Rest
- **Database:** PostgreSQL encryption enabled
- **Charter Files:** File system encryption (OS-level)
- **Sensitive Fields:** PII fields encrypted in JSONB columns

#### In Transit
- **API Communication:** TLS 1.3 for Claude API calls
- **Database Connection:** SSL/TLS enforced for PostgreSQL connections

**PostgreSQL SSL Configuration:**
```yaml
uaip-db:
  environment:
    POSTGRES_SSL_MODE: require
```

### 15.3 Input Validation

**All user inputs sanitized:**
```python
from pydantic import BaseModel, validator, constr

class UserResponse(BaseModel):
    content: constr(min_length=1, max_length=5000)

    @validator('content')
    def sanitize_content(cls, v):
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '<iframe>', '<?php']
        for char in dangerous_chars:
            if char.lower() in v.lower():
                raise ValueError(f"Invalid input: contains {char}")
        return v.strip()
```

### 15.4 Rate Limiting

**Prevent abuse of Claude API:**
```python
# config/rate_limits.yaml
rate_limits:
  per_user:
    requests_per_minute: 30
    sessions_per_day: 10
  per_ip:
    requests_per_minute: 60
  claude_api:
    calls_per_minute: 100
    retry_with_backoff: true
```

### 15.5 Logging Security

**Do NOT log:**
- API keys
- User passwords
- Personal Identifiable Information (PII)
- Full business strategy details (summary only)

**Logging Configuration:**
```python
import structlog

# Sanitize sensitive fields before logging
def sanitize_log(logger, method_name, event_dict):
    sensitive_keys = ['api_key', 'password', 'token', 'secret']
    for key in sensitive_keys:
        if key in event_dict:
            event_dict[key] = '***REDACTED***'
    return event_dict

structlog.configure(
    processors=[
        sanitize_log,
        structlog.processors.JSONRenderer()
    ]
)
```

### 15.6 Session Security

**Session Timeout:**
- Auto-logout after 120 minutes of inactivity
- Sessions cleared from memory after 24 hours
- Database cleanup of abandoned sessions weekly

**Session ID Generation:**
```python
import secrets

def generate_session_id():
    """Generate cryptographically secure session ID"""
    return f"uaip-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(6)}"
```

### 15.7 Compliance Considerations

**Data Retention:**
- Session data retained for 90 days
- Charters retained indefinitely (user-owned)
- Conversation logs anonymized after 30 days

**GDPR Compliance (if applicable):**
- Right to data deletion (user can delete sessions)
- Data export functionality (JSON format)
- Minimal data collection (no unnecessary PII)

**File: `src/compliance/data_retention.py`**
```python
async def cleanup_old_sessions():
    """Delete sessions older than 90 days"""
    cutoff_date = datetime.now() - timedelta(days=90)
    await db.execute(
        "DELETE FROM sessions WHERE last_updated_at < $1 AND status = 'abandoned'",
        cutoff_date
    )
```

---

## 16. Performance Requirements

### 16.1 Response Time Targets

| Operation | Target (95th percentile) | Maximum Acceptable |
|-----------|--------------------------|-------------------|
| User input processing | <3 seconds | <5 seconds |
| Quality reflection | <2 seconds | <4 seconds |
| Stage gate validation | <5 seconds | <10 seconds |
| Charter generation | <10 seconds | <20 seconds |
| PDF export | <15 seconds | <30 seconds |
| Session resume | <2 seconds | <5 seconds |

### 16.2 Scalability Targets

**Concurrent Users:**
- Target: 100 concurrent sessions
- Maximum: 200 concurrent sessions (with degraded performance warnings)

**Database Performance:**
- Session CRUD operations: <100ms
- Conversation history append: <50ms
- Charter retrieval: <200ms

### 16.3 Resource Limits

**Container Resource Allocation:**

```yaml
# docker-compose.yml additions
services:
  uaip-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  uaip-db:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### 16.4 Claude API Optimization

**Token Usage Management:**
```python
# Estimated token usage per session
ESTIMATED_TOKENS_PER_SESSION = {
    "stage1": 3000,
    "stage2": 2500,
    "stage3": 3500,
    "stage4": 2000,
    "stage5": 4000,
    "reflection_overhead": 5000,  # Quality checks add tokens
    "total": 20000  # ~20K tokens per complete session
}

# Cost estimation (assuming Claude Sonnet pricing)
COST_PER_SESSION = 20000 * (3.00 / 1_000_000)  # ~$0.06 per session
```

**Optimization Strategies:**
1. Cache common reflection responses
2. Batch quality assessments when possible
3. Use shorter prompts for follow-up questions
4. Implement smart context pruning for long sessions

### 16.5 Database Query Optimization

**Indexes for Fast Queries:**
```sql
-- Already included in init.sql, but critical for performance
CREATE INDEX idx_user_sessions ON sessions(user_id, started_at);
CREATE INDEX idx_status ON sessions(status);
CREATE INDEX idx_session_messages ON conversation_history(session_id, timestamp);

-- Additional performance indexes
CREATE INDEX idx_stage_data_lookup ON stage_data(session_id, stage_number);
CREATE INDEX idx_charter_by_decision ON project_charters(governance_decision);
```

**Connection Pooling:**
```python
# src/database/pool.py
from asyncpg import create_pool

async def init_db_pool():
    return await create_pool(
        dsn=DATABASE_URL,
        min_size=10,
        max_size=50,
        max_inactive_connection_lifetime=300,
        timeout=30
    )
```

---

## 17. Monitoring & Observability

### 17.1 Integration with Global Monitoring Stack

**Per CLAUDE.md requirements:**
- ✅ Use global Prometheus/Grafana stack (port 60090/60001)
- ✅ DO NOT deploy individual monitoring containers
- ✅ Expose `/metrics` endpoint on port 18080

### 17.2 Prometheus Metrics

**Exposed Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Session metrics
uaip_sessions_total = Counter(
    'uaip_sessions_total',
    'Total number of sessions started',
    ['status']  # in_progress, completed, abandoned
)

uaip_sessions_active = Gauge(
    'uaip_sessions_active',
    'Number of currently active sessions'
)

uaip_session_duration_seconds = Histogram(
    'uaip_session_duration_seconds',
    'Time to complete full session',
    buckets=[600, 1200, 1800, 2400, 3600, 7200]  # 10min to 2hr
)

# Stage metrics
uaip_stage_completion_seconds = Histogram(
    'uaip_stage_completion_seconds',
    'Time to complete each stage',
    ['stage_number'],
    buckets=[60, 120, 300, 600, 900]
)

uaip_stage_attempts = Counter(
    'uaip_stage_attempts',
    'Number of validation attempts per stage',
    ['stage_number', 'result']  # result: passed/failed
)

# Quality metrics
uaip_response_quality_score = Histogram(
    'uaip_response_quality_score',
    'Distribution of response quality scores',
    ['stage_number'],
    buckets=[0, 2, 4, 6, 7, 8, 9, 10]
)

uaip_reflection_loops = Counter(
    'uaip_reflection_loops',
    'Number of quality reflection loops triggered',
    ['stage_number', 'loop_count']
)

# Governance decisions
uaip_governance_decisions = Counter(
    'uaip_governance_decisions',
    'Count of governance decisions',
    ['decision']  # proceed, proceed_with_monitoring, halt
)

# Claude API metrics
uaip_claude_api_calls = Counter(
    'uaip_claude_api_calls',
    'Total Claude API calls',
    ['agent_type', 'status']  # status: success/error
)

uaip_claude_api_duration_seconds = Histogram(
    'uaip_claude_api_duration_seconds',
    'Claude API call duration',
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

uaip_claude_tokens_used = Counter(
    'uaip_claude_tokens_used',
    'Total tokens consumed',
    ['agent_type']
)

# Database metrics
uaip_db_query_duration_seconds = Histogram(
    'uaip_db_query_duration_seconds',
    'Database query duration',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

# Error tracking
uaip_errors_total = Counter(
    'uaip_errors_total',
    'Total errors by type',
    ['error_type', 'component']
)
```

**Metrics Endpoint:**
```python
# src/monitoring/metrics_server.py
from prometheus_client import start_http_server

def start_metrics_server(port=18080):
    """Start Prometheus metrics HTTP server"""
    start_http_server(port)
    logger.info(f"Prometheus metrics server started on port {port}")
```

### 17.3 Structured Logging

**Log Format:**
```python
import structlog

logger = structlog.get_logger()

# Example log entries
logger.info("session_started",
    session_id=session_id,
    user_id=user_id,
    project_name=project_name
)

logger.info("stage_completed",
    session_id=session_id,
    stage_number=1,
    duration_seconds=324,
    quality_score=8.5
)

logger.warning("quality_reflection_loop",
    session_id=session_id,
    stage_number=2,
    attempt=2,
    quality_score=5
)

logger.error("claude_api_error",
    session_id=session_id,
    agent_type="Stage1Agent",
    error_type="RateLimitError",
    exc_info=True
)
```

**Log Output to Loki (Global Monitoring Stack):**
```yaml
# config/logging.yaml
handlers:
  loki:
    class: logging_loki.LokiHandler
    url: http://loki:60100/loki/api/v1/push
    tags:
      application: uaip-assistant
      environment: production
```

### 17.4 Alerting Rules

**Integration with Alertmanager (port 60093):**

```yaml
# prometheus_alerts.yml (configured on global Prometheus)
groups:
  - name: uaip_alerts
    interval: 30s
    rules:
      - alert: HighSessionAbandonmentRate
        expr: rate(uaip_sessions_total{status="abandoned"}[5m]) > 0.3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High session abandonment rate"
          description: "{{ $value }}% of sessions abandoned in last 5 minutes"

      - alert: SlowCharter Generation
        expr: histogram_quantile(0.95, uaip_session_duration_seconds) > 3600
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Charter generation taking too long"
          description: "95th percentile session duration: {{ $value }}s"

      - alert: ClaudeAPIErrors
        expr: rate(uaip_claude_api_calls{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Claude API error rate high"
          description: "{{ $value }} errors per second"

      - alert: HighTokenUsage
        expr: rate(uaip_claude_tokens_used[1h]) > 500000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Claude API token usage high"
          description: "Using {{ $value }} tokens/hour"
```

### 17.5 Grafana Dashboard

**Dashboard Panels (configured on global Grafana port 60001):**

1. **Session Overview**
   - Active sessions gauge
   - Sessions completed today
   - Average session duration
   - Abandonment rate

2. **Stage Performance**
   - Time per stage (heatmap)
   - Stage validation pass/fail rates
   - Quality score distribution

3. **Quality Metrics**
   - Average response quality by stage
   - Reflection loop frequency
   - Improvement after reflection

4. **Governance Decisions**
   - Decision distribution (pie chart)
   - Halt rate over time
   - Residual risk distribution

5. **API Performance**
   - Claude API call rate
   - API latency (p50, p95, p99)
   - Token usage rate
   - Error rate

6. **System Health**
   - Database query performance
   - Container CPU/memory usage
   - Active database connections

**Example PromQL Queries:**
```promql
# Session completion rate
rate(uaip_sessions_total{status="completed"}[1h]) /
rate(uaip_sessions_total[1h])

# Average quality score improvement
avg(uaip_response_quality_score{loop_count="2"}) -
avg(uaip_response_quality_score{loop_count="1"})

# 95th percentile session duration
histogram_quantile(0.95, rate(uaip_session_duration_seconds_bucket[5m]))

# Claude API cost per day (estimated)
(sum(rate(uaip_claude_tokens_used[24h])) * 3.00 / 1000000)
```

---

## 18. Risks & Mitigations

### 18.1 Technical Risks

#### Risk 1: Claude API Rate Limiting
**Impact:** High
**Probability:** Medium
**Description:** Claude API has rate limits that could block sessions

**Mitigation:**
- Implement exponential backoff retry logic
- Queue requests during high load
- Monitor token usage with alerts
- Implement graceful degradation (save session, notify user)

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(RateLimitError)
)
async def call_claude_api(prompt):
    # API call implementation
    pass
```

#### Risk 2: Long Session Duration Exceeding Limits
**Impact:** Medium
**Probability:** Low
**Description:** Sessions >2 hours may hit timeout limits

**Mitigation:**
- Auto-save checkpoints every 5 minutes
- Allow session pause/resume
- Send reminder to user at 90-minute mark
- Implement session extension mechanism

#### Risk 3: Database Connection Pool Exhaustion
**Impact:** High
**Probability:** Low
**Description:** Concurrent sessions exhaust database connections

**Mitigation:**
- Connection pooling with `asyncpg` (50 connections)
- Monitor active connections with alerts
- Implement connection timeout (30s)
- Horizontal scaling capability if needed

### 18.2 User Experience Risks

#### Risk 4: User Frustration with Quality Loops
**Impact:** Medium
**Probability:** Medium
**Description:** Excessive quality reflection loops frustrate users

**Mitigation:**
- Limit to 3 reflection loops maximum
- Provide helpful examples after 2nd failed attempt
- Allow "skip quality check" with warning (admin override)
- Improve prompt quality to reduce initial vagueness

#### Risk 5: Complex Questions Confuse Users
**Impact:** Medium
**Probability:** Medium
**Description:** Users don't understand technical AI terminology

**Mitigation:**
- Provide glossary of terms (accessible via 'help')
- Include examples in every question
- Offer multiple-choice options when applicable
- Use plain language, explain technical terms inline

### 18.3 Business Risks

#### Risk 6: Low Adoption Due to Time Investment
**Impact:** High
**Probability:** Medium
**Description:** 45-minute session too long for busy users

**Mitigation:**
- Emphasize time savings vs. manual documentation (weeks → minutes)
- Allow saving partial progress
- Create "quick evaluation" mode (abbreviated version for initial screening)
- Show progress bar and time estimates

#### Risk 7: Generated Charters Require Significant Editing
**Impact:** Medium
**Probability:** Medium
**Description:** Users spend hours editing charter after generation

**Mitigation:**
- High-quality question design
- Extensive testing with real projects
- Charter review step before final export
- Allow inline editing during session

### 18.4 Security Risks

#### Risk 8: Sensitive Business Information Leakage
**Impact:** Critical
**Probability:** Low
**Description:** Session data accessed by unauthorized users

**Mitigation:**
- Encrypt sensitive JSONB fields in database
- User authentication (future enhancement)
- Session IDs are cryptographically random
- Regular security audits
- Data retention limits (90 days)

### 18.5 Cost Risks

#### Risk 9: Claude API Costs Exceed Budget
**Impact:** Medium
**Probability:** Low
**Description:** Heavy usage leads to unexpected API costs

**Mitigation:**
- Monitor token usage with alerts
- Set monthly budget alerts ($500, $1000 thresholds)
- Optimize prompts to reduce token usage
- Implement smart context pruning
- Estimated cost: ~$0.06/session = $6 per 100 sessions

### 18.6 Risk Matrix

| Risk | Impact | Probability | Priority | Mitigation Status |
|------|--------|-------------|----------|-------------------|
| Claude API Rate Limiting | High | Medium | 🔴 P1 | ✅ Implemented |
| Session Timeout | Medium | Low | 🟡 P2 | ✅ Implemented |
| DB Connection Exhaustion | High | Low | 🟡 P2 | ✅ Implemented |
| User Frustration (Quality) | Medium | Medium | 🟡 P2 | ✅ Implemented |
| Complex Questions | Medium | Medium | 🟡 P2 | ⏳ In Progress |
| Low Adoption (Time) | High | Medium | 🔴 P1 | ⏳ Planned |
| Charter Editing Required | Medium | Medium | 🟢 P3 | ⏳ Testing Phase |
| Data Leakage | Critical | Low | 🔴 P1 | ✅ Implemented |
| Cost Overruns | Medium | Low | 🟢 P3 | ✅ Monitoring |

---

## 19. Future Enhancements (v2.0+)

### 19.1 Web Interface (Priority: High)

**Description:** Browser-based UI replacing CLI

**Features:**
- Rich text input with markdown preview
- Visual progress tracking with stage map
- Inline charter editing before export
- Session management dashboard
- Real-time collaboration (multiple stakeholders)

**Tech Stack:**
- Frontend: React + TypeScript
- Backend: FastAPI REST API
- WebSockets for real-time updates

**Estimated Effort:** 8-10 weeks

### 19.2 Multi-User Collaboration (Priority: Medium)

**Description:** Multiple stakeholders contribute to same session

**Features:**
- Role-based access (PM, Data Scientist, Ethics Officer)
- Each role answers relevant stage questions
- Comment and discussion threads
- Approval workflow before charter finalization

**Use Case:** PM defines problem (Stage 1), Data Scientist assesses data (Stage 3), Ethics Officer completes Stage 5

**Estimated Effort:** 6 weeks

### 19.3 Integration with Project Management Tools (Priority: Medium)

**Supported Integrations:**
- **Jira:** Auto-create epics from charter
- **Confluence:** Publish charter as wiki page
- **Notion:** Export charter to Notion database
- **Slack:** Notify team when charter generated

**Estimated Effort:** 4 weeks

### 19.4 Template Library (Priority: Low)

**Description:** Pre-populated examples for common AI project types

**Templates:**
- Customer churn prediction
- Fraud detection
- Recommendation systems
- Predictive maintenance
- Demand forecasting

**Benefits:**
- Faster session completion
- Educational examples
- Best practice guidance

**Estimated Effort:** 2 weeks

### 19.5 AI-Assisted Charter Review (Priority: Low)

**Description:** Use Claude to review and suggest improvements to final charter

**Features:**
- Coherence check across sections
- Flag missing information
- Suggest additional risk considerations
- Compare against best practices

**Estimated Effort:** 3 weeks

### 19.6 Historical Charter Analytics (Priority: Low)

**Description:** Analyze trends across multiple projects

**Dashboards:**
- Common ML archetypes by industry
- Average data quality scores
- Governance decision distribution
- Time-to-completion trends
- Success rate predictions

**Estimated Effort:** 4 weeks

### 19.7 Charter Version Control (Priority: Medium)

**Description:** Track charter evolution over project lifecycle

**Features:**
- Git-like diffing between versions
- Revert to previous version
- Track which fields changed
- Audit trail for compliance

**Estimated Effort:** 3 weeks

### 19.8 Custom Question Sets (Priority: Low)

**Description:** Organizations customize U-AIP questions

**Features:**
- Admin interface to edit question templates
- Add organization-specific validation rules
- Custom ethical frameworks (beyond NIST RMF)
- Industry-specific question sets

**Estimated Effort:** 5 weeks

### 19.9 Offline Mode (Priority: Low)

**Description:** Run sessions without internet (local LLM)

**Features:**
- Use local Ollama/LM Studio models
- Reduced quality vs. Claude but offline capability
- Sync sessions to cloud when online

**Estimated Effort:** 6 weeks

### 19.10 Mobile App (Priority: Very Low)

**Description:** iOS/Android apps for on-the-go sessions

**Challenges:**
- Long sessions not ideal for mobile
- Complex input on small screens

**Possible Approach:**
- Voice input for responses
- Simplified "quick assessment" mode

**Estimated Effort:** 12 weeks

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **U-AIP** | Universal AI Project Scoping and Framing Protocol - A 5-stage evaluation framework |
| **Stage Gate** | Validation checkpoint that must pass before progressing to next stage |
| **ML Archetype** | Category of machine learning task (e.g., classification, regression) |
| **Reflection Agent** | AI agent that evaluates quality of responses/outputs |
| **Quality Loop** | Iterative refinement process when response quality is insufficient |
| **Residual Risk** | Ethical risk remaining after mitigation strategies applied |
| **Governance Decision** | Final determination: Proceed, Proceed with Monitoring, Revise, or Halt |
| **Charter** | Comprehensive AI Project Charter document (8 sections, 20-30 pages) |
| **APA 7** | American Psychological Association 7th Edition citation format |
| **SMART** | Specific, Measurable, Achievable, Relevant, Time-bound (KPI criteria) |
| **FAIR** | Findable, Accessible, Interoperable, Reusable (data principles) |

---

## Appendix B: Configuration Files Reference

### Question Templates
**Location:** `config/questions/`
- `stage1_questions.yaml` - Business Translation questions
- `stage2_questions.yaml` - Value Quantification questions
- `stage3_questions.yaml` - Data Feasibility questions
- `stage4_questions.yaml` - User Context questions
- `stage5_questions.yaml` - Ethics questions

### Validation Rules
**Location:** `config/validation/`
- `quality_thresholds.yaml` - Response quality scoring rules
- `stage_gate_requirements.yaml` - Mandatory fields per stage
- `consistency_rules.yaml` - Cross-stage validation logic

### Charter Templates
**Location:** `templates/`
- `charter_template.md` - Markdown charter structure
- `charter_styles.css` - PDF styling
- `apa7_citations.yaml` - Citation format rules

---

## Appendix C: Development Timeline

```
Week 1-2:  Foundation & Infrastructure
Week 3-4:  Stage Interview Agents
Week 5:    Reflection Agent System
Week 6:    Document Generation
Week 7:    Integration & Testing
Week 8:    Deployment Preparation
───────────────────────────────────────
Total:     8 weeks to v1.0 production
```

---

## Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-12 | Initial complete specification | Technical Architecture Team |

---

## Approval Signatures

**Technical Lead:** ___________________________ Date: __________

**Product Owner:** ___________________________ Date: __________

**Security Review:** ___________________________ Date: __________

---

**END OF SPECIFICATION DOCUMENT**

**Total Pages:** ~50+
**Total Sections:** 19 main + 3 appendices
**Specification Completeness:** 100%

---

*This specification serves as the single source of truth for the U-AIP Scoping Assistant implementation. All development work must align with this document. Changes require formal approval through the change control process.*
