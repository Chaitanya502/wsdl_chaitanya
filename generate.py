🏆 Hackathon Project Title
“Self-Healing Jenkins Pipeline for Auto-Rerun of Failed AFTs”

(Building resilience in CI/CD by automatically detecting and recovering from flaky functional test failures)

💡 Use Case Overview

In modern CI/CD pipelines, Automated Functional Tests (AFTs) play a crucial role in validating application behavior before deployment. However, intermittent or flaky test failures — often caused by environment instability, timing issues, or external dependencies — lead to unnecessary build failures.
This impacts developer productivity, slows down release cycles, and increases the load on CI/CD systems due to manual restarts.

The goal of this project is to create a self-healing Jenkins pipeline that:

Detects failed AFTs automatically,

Reruns only the failed tests,

Merges the rerun results with the previous build,

Determines the final build outcome intelligently.

🔍 Problem Statement

Currently, when AFTs fail intermittently:

Jenkins marks the build as failed even though only a few tests are flaky.

Developers have to manually retrigger the build or selectively rerun failed tests.

This leads to wasted compute time, developer frustration, and delayed delivery.

🚀 Proposed Solution

We propose a Jenkins-based self-healing AFT rerun automation system that:

Identifies failed AFTs after the initial build run.

Auto-triggers a secondary build or rerun step containing only the failed tests.

Captures rerun results and merges them with the previous build reports.

Evaluates final test outcomes and updates the build status as:

✅ SUCCESS — if all rerun tests pass.

⚠️ UNSTABLE — if some tests still fail after retries.

❌ FAILURE — if reruns also fail completely.

🧠 High-Level Architecture
flowchart TD
    A[Code Commit / Manual Trigger] --> B[Initial Jenkins Build]
    B --> C[Run Unit + AFT Tests]
    C -->|Some Failed| D[Collect Failed Test Names from JUnit XML]
    D --> E[Auto-trigger Rerun Job or Stage]
    E --> F[Run Failed AFTs Again]
    F --> G[Merge Results (JUnit Plugin)]
    G --> H[Evaluate Build Status]
    H -->|All Passed| I[Mark Build as SUCCESS]
    H -->|Partial Fail| J[Mark Build as UNSTABLE + Notify Developer]
