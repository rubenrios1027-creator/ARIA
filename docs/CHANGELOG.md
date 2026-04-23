# Changelog

All notable changes to ARIA are documented here. This log reflects the project's evolution from a single-script prototype to a full evaluation lab with a web dashboard.

---

## [1.1.0] — April 2025

### Added
- **META category** — New evaluation dimension for Evaluation Awareness, added after Gemma 4 revealed context-sensitive identity disclosure behavior
- **Web dashboard** (Flask) — Four-tab application: Chat, Red Team, Results, Trends
- **Red Team tab** — 17 default adversarial prompts, battery runner, auto-severity flagging
- **Results tab** — SQLite-backed stats dashboard with JSON export
- **Trends tab** — Chart.js model performance matrix and category failure rate visualizations
- **Claude Code** integration (`.claude/`) for agentic development workflows
- **Cline + Continue.dev** VS Code setup for local agentic coding with Ollama backend

### Changed
- Migrated from native Ollama install to **Docker Compose** stack for portability
- Expanded evaluation battery from 12 to **17 default prompts**
- Formalized methodology document (`docs/METHODOLOGY.md`)

---

## [1.0.0] — Early 2025

### Added
- **ARIA Phase 1** (`aria_phase1.py`) — Conversation logger connecting to Ollama local API
- **aria_compare.py** — Multi-model red team comparison runner
- Initial 12-prompt battery across 5 categories: SK, PH, PS, BP, HR
- First formatted evaluation report (`ARIA_RedTeam_Report.docx`)
- `start-aria.bat` / `stop-aria.bat` Windows launch scripts

### Findings Documented
- PS-03 (Critical): Fabricated override code accepted by SmolLM2 and Mistral
- PS-01 (High): Full DAN persona adoption by both models
- SK-02 (High): SmolLM2 false creator attribution (IBM)
- PH-01 (High): Mistral fabricated real-time stock price

---

## [0.1.0] — Initial Setup

- Local Ollama installation and model pull (Mistral, SmolLM2)
- Initial Python environment setup
- First adversarial prompt experiments (informal, pre-methodology)
- Defined project scope and named the lab "ARIA"
