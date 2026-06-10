# Changelog

All notable changes to RPG LLM Adventure will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] — 2026-06-10

### Added

- Bilingual support (Portuguese/English) with browser language detection and manual selector ([#i18n])
- Configurable adventure rounds: 8, 12, 20, or unlimited ("Until the end") ([#rounds])
- "End Adventure" button to conclude the story at any round ([#rounds])
- Book Mode theme toggle (parchment-style light theme) with localStorage persistence ([#ui])
- Full History accordion showing all past rounds during gameplay ([#ui])
- Ollama model discovery endpoint (`GET /api/ollama/models`) with "Load Models" button ([#models])
- Collapsible "Advanced" section for temperature and max_tokens configuration ([#models])
- Contextual loading messages ("Preparing adventure...", "Consulting the oracle...") ([#ui])
- Inline error display with auto fade-out (replaces browser alert dialogs) ([#ui])

### Changed

- Model input replaced with dynamic `<select>` populated by provider (OpenAI, Anthropic) or Ollama API ([#models])
- System prompts refined with Fighting Fantasy tone guidelines, recurring character consistency, and anti-immersion-break rules ([#prompts])
- LLM config moved into a collapsible "Options" menu for a cleaner start screen ([#i18n])

### Fixed

- Double-click on action buttons no longer corrupts round progression (`isSubmitting` guard) ([#fix])
- Path traversal vulnerability in log file download endpoint ([#security])
- Session ID collision with 1-second granularity replaced by UUID-based IDs ([#security])

## [0.1.0] — 2026-05-31

### Added

- Initial release: text-based RPG adventure powered by Ollama, OpenAI, and Anthropic
- FastAPI backend with Web UI and CLI interfaces
- 20-round adventure format with automatic Markdown log generation
- Custom action input for free-form player choices
- CRT terminal aesthetic with VT323 monospace font and scanline effects
- Mobile-responsive design

[0.1.2]: https://github.com/ClaudioDrews/rpg-llm-adventure/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/ClaudioDrews/rpg-llm-adventure/releases/tag/v0.1.0

[#i18n]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Ai18n
[#rounds]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Arounds
[#ui]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Aui
[#models]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Amodels
[#prompts]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Aprompts
[#fix]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Abug
[#security]: https://github.com/ClaudioDrews/rpg-llm-adventure/issues?q=label%3Asecurity