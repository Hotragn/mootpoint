## LLM Usage Statement

I used Claude Code (Anthropic, Claude Opus models) as a research assistant throughout the sprint: to search and summarise literature, write and test the harness and analysis code, run the experiments, and draft text from verified result files. I directed the work, chose the research direction, and reviewed the outputs. Every number in this paper is produced by committed scripts from committed model outputs, and every reference was opened and checked against its arXiv or ACL Anthology record.

Codex CLI and the ChatGPT web interface were available but not used: an attempted ChatGPT cross-check was blocked by the assistant's permission settings, and no Codex tasks were run.

The experiments themselves use open-weight models through the Adaption API (sprint credits; about 25 credits in total): qwen3.8-27b wrote the case files; gemma-4-31b-it, deepseek-v4-flash and glm-53-flash wrote descriptions; qwen3.5-397b and deepseek-v4-flash labelled claims; qwen3.5-397b, deepseek-v4-flash, qwen3.8-27b and glm-5.2 served as readers.

Preexisting work: the Adaption API endpoint and payload fields follow what I learned in my earlier project (approve-what-you-see). No code, data or analysis from earlier projects is reused.
