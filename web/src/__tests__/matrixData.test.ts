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

  it("desktop_framework dest choices are electron-vite|tauri only", () => {
    const prompt = getPrompt("desktop_framework");
    expect(prompt).toBeDefined();
    expect(prompt?.choices).toEqual(["electron-vite", "tauri"]);
    expect(prompt?.choices).not.toContain("electron-forge");
    expect(prompt?.help ?? "").not.toMatch(/electron-forge/);
    expect(defaultRisoConfig.desktop_framework).toBe("electron-vite");
  });

  it("api_features dest help is Python FastAPI only", () => {
    const prompt = getPrompt("api_features");
    expect(prompt).toBeDefined();
    expect(prompt?.when).toBe(
      "{{ api_module == 'enabled' and 'python' in api_languages }}",
    );
    expect(prompt?.help ?? "").toMatch(/Python-only/);
    expect(prompt?.help ?? "").not.toMatch(
      /GraphQL endpoint \(Strawberry\/Apollo\/async-graphql\)/,
    );
  });
});
