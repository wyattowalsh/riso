import { describe, it, expect } from "vitest";
import {
  getPrompt,
  getPromptChoices,
  getPromptDefault,
} from "../lib/matrixData";
import { defaultRisoConfig } from "../lib/store";

describe("matrix dest lockstep (WIZ-P1-lucia-dest)", () => {
  it("saas_auth_provider dest choices are clerk|authjs only", () => {
    const prompt = getPrompt("saas_auth_provider");
    expect(prompt).toBeDefined();
    expect(prompt?.choices).toEqual(["clerk", "authjs"]);
    expect(getPromptChoices("saas_auth_provider", ["clerk", "authjs"])).toEqual(
      ["clerk", "authjs"],
    );
    expect(prompt?.choices).not.toContain("lucia");
    expect(prompt?.help ?? "").not.toMatch(/Lucia/i);
  });

  it("defaults stay clerk dest, just runner, OpenSpec off", () => {
    expect(getPromptDefault("saas_auth_provider", "clerk")).toBe("clerk");
    expect(getPromptDefault("task_runner", "just")).toBe("just");
    expect(getPromptDefault("openspec_extra", "disabled")).toBe("disabled");
    expect(defaultRisoConfig.saas_auth_provider).toBe("clerk");
    expect(defaultRisoConfig.task_runner).toBe("just");
    expect(defaultRisoConfig.openspec_extra).toBe("disabled");
  });
});
