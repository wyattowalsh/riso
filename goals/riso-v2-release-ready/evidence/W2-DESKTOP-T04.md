# W2 DESK-T04 — no clang/lld in Tauri cargo config

- Task: `DESK-T04`
- Wave: W2 / lane DESKTOP
- Deps: `DESK-T01`
- Exclusive write: `template/files/tauri/**`
- Verify: `rg lld` empty under `.cargo`
- Status: **green**
- `samples/*/render/**` writes: **0**

## Contract

`template/files/tauri/src-tauri/.cargo/config.toml.jinja` does **not** pin `linker = "clang"` or `link-arg=-fuse-ld=lld`. Local file is incremental + Windows `/DEBUG:NONE` only (dirty KEEP vs HEAD, which still has clang/lld).

```toml
[build]
incremental = true
# Use the platform default linker.

[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "link-arg=/DEBUG:NONE"]
```

## Verify

```text
rg -n -i 'clang|lld|fuse-ld' template/files/tauri/src-tauri/.cargo
(no matches)
```

Jinja render of the cargo template contains neither `clang` nor `lld`.

`template/files/tauri/.vscode/launch.json.jinja` still has `"type": "lldb"` — that is the **debugger**, not the linker. Left unchanged.
