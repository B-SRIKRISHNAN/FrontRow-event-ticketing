# Phase 0 Research: Init Script & README Finalization

**Feature Branch**: `007-init-script-readme-finalization`
**Date**: 2026-09-25

## Technical Decisions & Analysis

### 1. One-Shot Script Cross-Platform Execution Architecture

- **Decision**: Provide both `init.py` (pure Python 3.11+ cross-platform runner) and `init.ps1` (PowerShell convenience entry point for Windows).
- **Rationale**:
  - `init.py` uses standard library modules (`subprocess`, `sys`, `pathlib`, `os`, `shutil`) to run identically across Windows, Linux, and macOS without extra dependencies.
  - `init.ps1` allows Windows developers to launch the setup directly via `.\init.ps1`.
- **Alternatives Considered**:
  - Bash script (`init.sh` only): Not natively supported on Windows PowerShell without WSL or Git Bash.
  - Makefile: Requires `make` utility which is not pre-installed on standard Windows environments.

---

### 2. Environment File Creation Strategy

- **Decision**: Idempotently copy `.env.example` -> `.env` if `.env` does not already exist. Preserve existing `.env` files if present to protect user overrides.
- **Rationale**: Prevents accidental overwriting of custom database passwords or API keys while guaranteeing zero-config defaults for first-time cloners.
- **Alternatives Considered**:
  - Force overwrite: Would wipe out existing developer environment variables.

---

### 3. Service Process Orchestration

- **Decision**: Launch Backend API (`uvicorn app.main:app --port 8000`), LLM Engine (`uvicorn app.main:app --port 8001`), and Frontend (`npm run dev` on port 3000) using asynchronous sub-processes with graceful shutdown (Ctrl+C handling).
- **Rationale**: Allows developers to run the entire FrontRow platform from a single terminal window during demonstration and testing.

---

### 4. Documentation & Concurrency Design Note Structure

- **Decision**: Format `README.md` into 6 clear, high-impact sections:
  1. Executive Summary & Architecture Diagram
  2. Tech Stack & Project Directory Structure
  3. Quickstart & One-Shot Setup Guide
  4. Environment Variables Reference (`.env.example` Walkthrough)
  5. Concurrency Correctness — Design Note (6-Step Guarantee)
  6. Automated Testing & Concurrency Test Reproduction Guide (`test_concurrency.py`)
- **Rationale**: Provides technical reviewers and auditors with both high-level design context and empirical proof commands.
