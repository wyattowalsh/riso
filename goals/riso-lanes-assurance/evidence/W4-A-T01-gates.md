# W4 A-T01 — Gate recheck (fail-closed)

| Gate                | Boolean | Source                                  | Recheck                                                                                                         |
| ------------------- | ------- | --------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| validate_green      | true    | W3-PL-T05-validate-summary.json (37/37) | Spot 4 samples ok:true → W4-A-T01-validate-spot.json                                                            |
| quality_green       | false   | W3-PL-T09-just-quality.log              | 839 passed / 1 failed / 3 errors — not re-run full suite (matrix contention; residual owned)                    |
| render_matrix_green | false   | W3-PL-T06-render_matrix.log             | Process still running (pid 28326 at recheck); api-monorepo smoke failed; no samples/metadata/render_matrix.json |
| riso_mcp_clean      | true    | rg src/riso template                    | W4-A-T04-riso-mcp.txt                                                                                           |

Fail-closed: quality_green and render_matrix_green are false because evidence does not prove exit 0 / complete matrix metadata.
