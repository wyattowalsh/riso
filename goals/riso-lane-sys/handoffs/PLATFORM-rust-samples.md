# PLATFORM handoff: optional `samples/rust-*` answer files

**From:** SYS lane  
**To:** PLATFORM  
**Priority:** P1  

## Problem

Go has matrix samples:

- `samples/go-api/copier-answers.yml`
- `samples/go-cli/copier-answers.yml`
- `samples/go-mcp/copier-answers.yml`

There are **no** `samples/rust-api`, `rust-cli`, or `rust-mcp` variants. SYS modernized `template/files/rust/**` but cannot author sample answers (PLATFORM ownership).

## Requested change

Add optional sample answer files (and wire into render matrix if appropriate):

| Sample | Suggested answers |
|--------|-------------------|
| `samples/rust-api` | `api_module: enabled`, `api_languages: [rust]`, Actix path |
| `samples/rust-cli` | `cli_module: enabled`, `cli_languages: [rust]`, Clap path |
| `samples/rust-mcp` | `mcp_module: enabled`, `mcp_languages: [rust]`, transport stdio |

Do **not** hand-edit `samples/*/render/`; regenerate via render scripts after answers land.

## SYS scope

Templates under `template/files/rust/**` are ready for validate/render once answers exist.
