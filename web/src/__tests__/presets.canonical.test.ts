import { describe, it, expect } from "vitest";
import { PRESETS } from "../components/presets/presets";
import {
  findRemovedAnswerKeys,
  REMOVED_ANSWER_KEYS,
} from "../lib/removedAnswerKeys";

describe("built-in presets (WEB-T04)", () => {
  it("use canonical Copier keys only", () => {
    expect(PRESETS.length).toBeGreaterThan(0);
    for (const preset of PRESETS) {
      const hits = findRemovedAnswerKeys(
        preset.config as Record<string, unknown>,
      );
      expect(hits, `${preset.id} still has ${hits.join(", ")}`).toEqual([]);
    }
  });

  it("does not mention old keys in preset config objects", () => {
    const dumped = JSON.stringify(PRESETS.map((preset) => preset.config));
    for (const key of Object.keys(REMOVED_ANSWER_KEYS)) {
      expect(dumped).not.toMatch(new RegExp(`"${key}"`));
    }
  });

  it("does not publish dest saas_auth_provider=lucia", () => {
    const dumped = JSON.stringify(PRESETS.map((preset) => preset.config));
    expect(dumped).not.toMatch(/"lucia"/);
  });
});
