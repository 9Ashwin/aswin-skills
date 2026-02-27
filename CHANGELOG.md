# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-27

### Added
- **git-review**: Local code review tool for pre-push self-check
  - Support for three review scopes: unstaged, staged, committed
  - Four review styles: professional, sarcastic, gentle, humorous
  - Auto-select review scope based on current changes
  - Output review report to `docs/reviews/` directory
  - Scoring criteria aligned with AI-Codereview-Gitlab project
