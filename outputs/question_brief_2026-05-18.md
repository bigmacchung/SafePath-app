# Question Brief: SafePath DS3 Rubric Audit
**Generated:** 2026-05-18
**Business Context:** Audit SafePath student project against DS3 Deliverables Rubric (50 pts) to maximize score on documentation, code, and meeting sections. App not built; Website/Report section (15 pts) excluded.
**Agent:** `agents/question-framing.md` (Step 1)

## Business Context Summary
- **Goal:** Maximize SafePath's DS3 Deliverables Rubric score on the 4 scorable sections (35 pts max)
- **Decision:** Which documentation gaps, code quality issues, and meeting log deficiencies to fix before submission
- **Constraints:** App/website not built (15 pts forfeited). Student project with 4 members + lead. Data files exist but are large (hosted on Google Drive, not GitHub).
- **Stakeholders:** Max (auditor), Vanshika (project lead), SafePath team (Matthew, Ruhan, Ajay)

## All Candidate Questions (Ranked)

| Rank | Question | Category | Impact | Feasibility | Score | Data Gaps |
|------|----------|----------|--------|-------------|-------|-----------|
| 1 | Does every rubric criterion have documented evidence in the repo? | Diagnostic | 5 | 5 | 25 | None |
| 2 | Are all quantitative claims in the documentation verifiable against actual data files? | Diagnostic | 5 | 5 | 25 | None |
| 3 | Does the code meet professional quality standards (modularization, docstrings, tests)? | Descriptive | 5 | 5 | 25 | None |
| 4 | Are meeting logs complete, consistent with ground truth, and properly attributed? | Diagnostic | 4 | 5 | 20 | Need meeting minutes access |
| 5 | Do all file references in documentation resolve to existing paths? | Descriptive | 4 | 5 | 20 | None |
| 6 | Is the data pipeline reproducible from the README instructions? | Prescriptive | 4 | 4 | 16 | Need full env setup |
| 7 | What is the gap between current state and full marks on each rubric section? | Comparative | 5 | 3 | 15 | Need rubric PDF |
| 8 | Are there inconsistencies between the two edge_scores CSV schemas? | Descriptive | 3 | 5 | 15 | None |

## Deep Dive: Top 3 Questions

### Question 1: Does every rubric criterion have documented evidence in the repo?
**Category:** Diagnostic
**Decision it informs:** Which documentation to add or improve before submission
**Impact:** 5 | **Feasibility:** 5

#### Tracking Gaps
- DS3 rubric PDF -> AVAILABLE (provided as PROJECTS_RUBRIC.pdf)
- All repo documentation -> AVAILABLE (docs/, README.md)
- Code files -> AVAILABLE (src/, tests/, notebooks/)

#### Hypotheses
1. **H1:** The design document covers all 4 sub-criteria (depth, rationale, diagrams, clarity).
   - If true: design_document.md has architecture, design decisions, Mermaid diagrams, clean formatting
   - If false: one or more sub-criteria lack evidence
   - Key metric: count of rubric sub-criteria with documented evidence
   - Data needed: design_document.md, PROJECTS_RUBRIC.pdf
   - Analysis approach: criterion-by-criterion mapping

2. **H2:** Code documentation meets the "docstrings & comments" criterion.
   - If true: all public functions in src/ have docstrings with parameter descriptions
   - If false: some functions lack docstrings or parameter/return documentation
   - Key metric: % of public functions with complete docstrings
   - Data needed: src/scoring/scoring.py, src/data/*.py
   - Analysis approach: Code Reviewer agent

3. **H3:** Meeting logs satisfy all 4 sub-criteria (consistency, detail, industry/faculty meetings, engagement).
   - If true: status.md has weekly entries, decisions, mentor meetings, attendance
   - If false: missing mentor/industry meeting documentation
   - Key metric: count of meeting log sub-criteria fully met
   - Data needed: status.md, meeting minutes ground truth
   - Analysis approach: Source Tie-Out agent

### Question 2: Are all quantitative claims in the documentation verifiable against actual data files?
**Category:** Diagnostic
**Decision it informs:** Which numbers to correct before submission
**Impact:** 5 | **Feasibility:** 5

#### Tracking Gaps
- Data files -> AVAILABLE (all 10 files in data/)
- Documentation claims -> AVAILABLE (AUDIT_REPORT.md, design_document.md, README.md)

#### Hypotheses
1. **H1:** Row counts cited in documentation match actual file row counts.
   - If true: crime=45,742, walkability=1,462, streetlights=55,506, edges=587,375, graph=684,012
   - If false: one or more counts are wrong
   - Key metric: count of mismatched row counts
   - Data needed: all data files via helpers/tieout_helpers.py read_source_direct()
   - Analysis approach: Data Explorer agent + Source Tie-Out agent

2. **H2:** Derived statistics (percentages, differences) are arithmetically correct.
   - If true: 14.1% unscored edges, 1.08% crime outliers, 29% walkability shortfall all compute correctly
   - If false: arithmetic errors in derived claims
   - Key metric: count of arithmetic errors
   - Data needed: documentation + calculator
   - Analysis approach: Validation agent Step 3

3. **H3:** Score value ranges documented match actual data ranges.
   - If true: all scores in [0,1], walk_score min=0.0526, infrastructure_score min=0.2781
   - If false: documented ranges don't match profiled ranges
   - Key metric: count of range mismatches
   - Data needed: edge_scores_infrastructure.csv via helpers/structural_validator.py validate_value_domain()
   - Analysis approach: Data Explorer agent + business_rules.py validate_ranges()

### Question 3: Does the code meet professional quality standards?
**Category:** Descriptive
**Decision it informs:** Which code improvements to make for GitHub Repo rubric section
**Impact:** 5 | **Feasibility:** 5

#### Tracking Gaps
- Source code -> AVAILABLE (src/scoring/, src/data/)
- Tests -> AVAILABLE (tests/)
- .gitignore -> AVAILABLE

#### Hypotheses
1. **H1:** The scoring module is well-organized with clean API boundaries.
   - If true: src/scoring/ has __init__.py exports, scoring.py has public functions with docstrings
   - If false: functions are disorganized or lack documentation
   - Key metric: cyclomatic complexity, docstring coverage
   - Data needed: src/scoring/scoring.py, src/scoring/__init__.py
   - Analysis approach: Code Reviewer agent

2. **H2:** Unit tests cover the core scoring logic and pass.
   - If true: pytest runs 46 tests, all pass, covers cost formulas + weight profiles + streetlight cleaning
   - If false: tests fail or coverage is incomplete
   - Key metric: test count, pass rate
   - Data needed: tests/*.py, pytest output
   - Analysis approach: Code Reviewer agent + pytest execution

3. **H3:** Version control follows good practices.
   - If true: meaningful commit messages, .gitignore excludes data files and secrets
   - If false: vague commit messages, missing .gitignore entries
   - Key metric: commit message quality, .gitignore completeness
   - Data needed: git log, .gitignore
   - Analysis approach: Code Reviewer agent

## Recommended Next Steps
1. Run Data Explorer agent (`agents/data-explorer.md`) to profile all data files
2. Run Source Tie-Out agent (`agents/source-tieout.md`) to verify data claims via dual-path
3. Run Code Reviewer agent (`agents/code-reviewer.md`) to assess code quality for rubric
4. Run Validation agent (`agents/validation.md`) to compile final rubric alignment report
