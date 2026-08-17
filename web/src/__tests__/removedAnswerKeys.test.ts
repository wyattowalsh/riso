import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it, expect } from "vitest";
import { parse as parseYAML } from "yaml";
import {
  ANSWER_KEY_REMAPS,
  REMOVED_ANSWER_KEYS,
  RemovedAnswerKeyError,
  applyRemovedKeyRemaps,
  applyThenRejectRemovedKeys,
  formatRemapPreview,
  remapRemovedAnswerKeys,
} from "../lib/removedAnswerKeys";

const PYTHON_REMOVED_KEYS = [
  "api_tracks",
  "api_language",
  "docs_site",
  "mcp_language",
  "saas_starter_module",
  "saas_auth",
  "saas_billing",
  "include_admin",
] as const;

const FIXTURE_DIR = join(
  dirname(fileURLToPath(import.meta.url)),
  "fixtures/remap",
);

function loadFixture(name: string): Record<string, unknown> {
  const raw = parseYAML(readFileSync(join(FIXTURE_DIR, name), "utf8"));
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    throw new Error(`invalid fixture ${name}`);
  }
  return raw as Record<string, unknown>;
}

describe("removedAnswerKeys parity with Python SSOT", () => {
  it("exposes exactly eight removed keys", () => {
    expect(Object.keys(REMOVED_ANSWER_KEYS)).toHaveLength(8);
  });

  it("matches Python removed_answer_keys key set", () => {
    expect(Object.keys(REMOVED_ANSWER_KEYS).sort()).toEqual(
      [...PYTHON_REMOVED_KEYS].sort(),
    );
  });

  it("remap table covers removed keys and operator names", () => {
    expect(Object.keys(ANSWER_KEY_REMAPS).sort()).toEqual(
      Object.keys(REMOVED_ANSWER_KEYS).sort(),
    );
    expect(ANSWER_KEY_REMAPS.api_language.action).toBe("wrap-list");
    expect(ANSWER_KEY_REMAPS.mcp_language.action).toBe("wrap-list");
    expect(ANSWER_KEY_REMAPS.api_tracks.action).toBe("derive");
    expect(ANSWER_KEY_REMAPS.docs_site.action).toBe("derive");
    expect(ANSWER_KEY_REMAPS.saas_starter_module.action).toBe("rename");
    expect(ANSWER_KEY_REMAPS.saas_auth.action).toBe("split");
    expect(ANSWER_KEY_REMAPS.saas_billing.action).toBe("split");
    expect(ANSWER_KEY_REMAPS.include_admin.action).toBe("rename-bool");
    expect(ANSWER_KEY_REMAPS.api_language.new_keys).toEqual(["api_languages"]);
    expect(ANSWER_KEY_REMAPS.mcp_language.new_keys).toEqual(["mcp_languages"]);
    expect(ANSWER_KEY_REMAPS.api_tracks.new_keys).toEqual([
      "api_module",
      "api_languages",
    ]);
    expect(ANSWER_KEY_REMAPS.docs_site.new_keys).toEqual([
      "docs_module",
      "docs_framework",
    ]);
    expect(ANSWER_KEY_REMAPS.saas_starter_module.new_keys).toEqual([
      "saas_infra_module",
    ]);
    expect(ANSWER_KEY_REMAPS.saas_auth.new_keys).toEqual([
      "saas_auth_module",
      "saas_auth_provider",
    ]);
    expect(ANSWER_KEY_REMAPS.saas_billing.new_keys).toEqual([
      "saas_billing_module",
      "saas_billing_provider",
    ]);
    expect(ANSWER_KEY_REMAPS.include_admin.new_keys).toEqual([
      "saas_admin_dashboard",
    ]);
  });
});

describe("wrap-list api_language", () => {
  it.each([
    ["python", ["python"]],
    ["node", ["node"]],
    ["rust", ["rust"]],
    ["go", ["go"]],
    [["python"], ["python"]],
    [
      ["node", "go"],
      ["node", "go"],
    ],
  ] as const)("maps %j → %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ api_language: before });
    expect(result.answers.api_languages).toEqual([...expected]);
    expect(result.answers).not.toHaveProperty("api_language");
    expect(result.ops[0]?.action).toBe("wrap-list");
    expect(result.ops[0]?.old).toBe("api_language");
    expect(result.ops[0]?.new_keys).toEqual(["api_languages"]);
  });
});

describe("wrap-list mcp_language", () => {
  it.each([
    ["python", ["python"]],
    ["typescript", ["typescript"]],
    ["rust", ["rust"]],
    ["go", ["go"]],
    ["node", ["typescript"]],
    ["js", ["typescript"]],
    [["python"], ["python"]],
    [
      ["node", "go"],
      ["typescript", "go"],
    ],
  ] as const)("maps %j → %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ mcp_language: before });
    expect(result.answers.mcp_languages).toEqual([...expected]);
    expect(result.answers).not.toHaveProperty("mcp_language");
    expect(result.ops[0]?.action).toBe("wrap-list");
  });
});

describe("derive api_tracks", () => {
  it.each([
    ["", { api_module: "disabled" }],
    ["none", { api_module: "disabled" }],
    ["disabled", { api_module: "disabled" }],
    [[], { api_module: "disabled" }],
    ["python", { api_module: "enabled", api_languages: ["python"] }],
    [
      "python+node",
      { api_module: "enabled", api_languages: ["python", "node"] },
    ],
    ["fastapi", { api_module: "enabled", api_languages: ["python"] }],
    ["fastify", { api_module: "enabled", api_languages: ["node"] }],
    ["actix", { api_module: "enabled", api_languages: ["rust"] }],
    [
      ["python", "go"],
      { api_module: "enabled", api_languages: ["python", "go"] },
    ],
  ] as const)("maps %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ api_tracks: before });
    expect(result.answers).toMatchObject(expected);
    expect(result.answers).not.toHaveProperty("api_tracks");
    expect(result.ops[0]?.action).toBe("derive");
  });
});

describe("derive docs_site", () => {
  it.each([
    ["none", { docs_module: "disabled" }],
    ["false", { docs_module: "disabled" }],
    ["disabled", { docs_module: "disabled" }],
    ["off", { docs_module: "disabled" }],
    ["sphinx", { docs_module: "enabled", docs_framework: "sphinx-shibuya" }],
    [
      "sphinx-shibuya",
      { docs_module: "enabled", docs_framework: "sphinx-shibuya" },
    ],
    ["docusaurus", { docs_module: "enabled", docs_framework: "docusaurus" }],
    ["fumadocs", { docs_module: "enabled", docs_framework: "fumadocs" }],
  ] as const)("maps %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ docs_site: before });
    expect(result.answers).toMatchObject(expected);
    expect(result.answers).not.toHaveProperty("docs_site");
    expect(result.ops[0]?.action).toBe("derive");
  });
});

describe("rename / split / rename-bool", () => {
  it.each([
    ["enabled", "enabled"],
    ["disabled", "disabled"],
    [true, "enabled"],
    [false, "disabled"],
  ] as const)("saas_starter_module %j → %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ saas_starter_module: before });
    expect(result.answers.saas_infra_module).toBe(expected);
    expect(result.answers).not.toHaveProperty("saas_starter_module");
    expect(result.ops[0]?.action).toBe("rename");
  });

  it.each([
    ["none", { saas_auth_module: "disabled" }],
    ["disabled", { saas_auth_module: "disabled" }],
    ["false", { saas_auth_module: "disabled" }],
    ["off", { saas_auth_module: "disabled" }],
    ["clerk", { saas_auth_module: "enabled", saas_auth_provider: "clerk" }],
    ["authjs", { saas_auth_module: "enabled", saas_auth_provider: "authjs" }],
  ] as const)("saas_auth %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ saas_auth: before });
    expect(result.answers).toMatchObject(expected);
    expect(result.answers).not.toHaveProperty("saas_auth");
    expect(result.ops[0]?.action).toBe("split");
  });

  it.each([
    ["none", { saas_billing_module: "disabled" }],
    [
      "stripe",
      { saas_billing_module: "enabled", saas_billing_provider: "stripe" },
    ],
    [
      "paddle",
      { saas_billing_module: "enabled", saas_billing_provider: "paddle" },
    ],
    [
      "lemonsqueezy",
      { saas_billing_module: "enabled", saas_billing_provider: "lemonsqueezy" },
    ],
  ] as const)("saas_billing %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ saas_billing: before });
    expect(result.answers).toMatchObject(expected);
    expect(result.answers).not.toHaveProperty("saas_billing");
    expect(result.ops[0]?.action).toBe("split");
  });

  it.each([
    [true, true],
    [false, false],
    ["true", true],
    ["yes", true],
    ["false", false],
    ["off", false],
    [1, true],
    [0, false],
  ] as const)("include_admin %j → %j", (before, expected) => {
    const result = applyRemovedKeyRemaps({ include_admin: before });
    expect(result.answers.saas_admin_dashboard).toBe(expected);
    expect(result.answers).not.toHaveProperty("include_admin");
    expect(result.ops[0]?.action).toBe("rename-bool");
  });
});

describe("apply contract", () => {
  it("does not mutate input", () => {
    const original = { api_language: "python" };
    applyRemovedKeyRemaps(original);
    expect(original).toEqual({ api_language: "python" });
  });

  it("second apply is a no-op", () => {
    const first = applyRemovedKeyRemaps({
      api_language: "python",
      mcp_language: "node",
    });
    const second = applyRemovedKeyRemaps(first.answers);
    expect(second.answers).toEqual(first.answers);
    expect(second.ops).toEqual([]);
  });

  it("does not overwrite dest wrap-list", () => {
    const result = applyRemovedKeyRemaps({
      api_language: "python",
      api_languages: ["go"],
    });
    expect(result.answers.api_languages).toEqual(["go"]);
    expect(result.answers).not.toHaveProperty("api_language");
  });

  it("fail-closes lucia saas_auth (no payload)", () => {
    expect(() => applyThenRejectRemovedKeys({ saas_auth: "lucia" })).toThrow(
      RemovedAnswerKeyError,
    );
    const leftover = applyRemovedKeyRemaps({ saas_auth: "lucia" });
    expect(leftover.answers).toHaveProperty("saas_auth", "lucia");
    expect(leftover.answers).not.toHaveProperty("saas_auth_provider");
  });

  it("does not overwrite dest split", () => {
    const result = applyRemovedKeyRemaps({
      saas_auth: "authjs",
      saas_auth_module: "disabled",
      saas_auth_provider: "clerk",
    });
    expect(result.answers.saas_auth_module).toBe("disabled");
    expect(result.answers.saas_auth_provider).toBe("clerk");
    expect(result.answers).not.toHaveProperty("saas_auth");
  });

  it("does not overwrite dest derive", () => {
    const result = applyRemovedKeyRemaps({
      api_tracks: "node",
      api_module: "disabled",
      api_languages: ["rust"],
    });
    expect(result.answers.api_module).toBe("disabled");
    expect(result.answers.api_languages).toEqual(["rust"]);
    expect(result.answers).not.toHaveProperty("api_tracks");
  });

  it("leaves unmapped values for reject", () => {
    const result = applyRemovedKeyRemaps({ saas_auth: "firebase" });
    expect(result.answers.saas_auth).toBe("firebase");
    expect(result.ops).toEqual([]);
    expect(() => applyThenRejectRemovedKeys(result.answers)).toThrow(
      RemovedAnswerKeyError,
    );
    try {
      applyThenRejectRemovedKeys(result.answers);
    } catch (error) {
      expect(error).toBeInstanceOf(RemovedAnswerKeyError);
      const message = (error as Error).message;
      expect(message).toContain("saas_auth");
      expect(message).toContain("saas_auth_module");
    }
  });

  it("remapRemovedAnswerKeys is an apply alias", () => {
    const a = applyRemovedKeyRemaps({ api_language: "python" });
    const b = remapRemovedAnswerKeys({ api_language: "python" });
    expect(b).toEqual(a);
  });

  it("formats preview strings from ops", () => {
    const result = applyRemovedKeyRemaps({ api_language: "python" });
    const preview = formatRemapPreview(result.ops);
    expect(preview).toHaveLength(1);
    expect(preview[0]).toContain("api_language");
    expect(preview[0]).toContain("api_languages");
    expect(preview[0]).toContain("wrap-list");
  });
});

describe("YAML fixtures", () => {
  it("api_language.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("api_language.yml"));
    expect(result.answers.api_languages).toEqual(["python"]);
    expect(result.answers).not.toHaveProperty("api_language");
  });

  it("mcp_language.yml maps node → typescript", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("mcp_language.yml"));
    expect(result.answers.mcp_languages).toEqual(["typescript"]);
    expect(result.answers).not.toHaveProperty("mcp_language");
  });

  it("api_tracks.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("api_tracks.yml"));
    expect(result.answers.api_module).toBe("enabled");
    expect(result.answers.api_languages).toEqual(["python", "node"]);
    expect(result.answers).not.toHaveProperty("api_tracks");
  });

  it("docs_site.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("docs_site.yml"));
    expect(result.answers.docs_module).toBe("enabled");
    expect(result.answers.docs_framework).toBe("sphinx-shibuya");
    expect(result.answers).not.toHaveProperty("docs_site");
  });

  it("saas_starter_module.yml", () => {
    const result = applyThenRejectRemovedKeys(
      loadFixture("saas_starter_module.yml"),
    );
    expect(result.answers.saas_infra_module).toBe("enabled");
    expect(result.answers).not.toHaveProperty("saas_starter_module");
  });

  it("saas_auth.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("saas_auth.yml"));
    expect(result.answers.saas_auth_module).toBe("enabled");
    expect(result.answers.saas_auth_provider).toBe("clerk");
    expect(result.answers).not.toHaveProperty("saas_auth");
  });

  it("saas_billing.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("saas_billing.yml"));
    expect(result.answers.saas_billing_module).toBe("enabled");
    expect(result.answers.saas_billing_provider).toBe("stripe");
    expect(result.answers).not.toHaveProperty("saas_billing");
  });

  it("include_admin.yml", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("include_admin.yml"));
    expect(result.answers.saas_admin_dashboard).toBe(true);
    expect(result.answers).not.toHaveProperty("include_admin");
  });

  it("mixed.yml remaps all eight keys", () => {
    const result = applyThenRejectRemovedKeys(loadFixture("mixed.yml"));
    expect(result.answers.api_module).toBe("enabled");
    expect(result.answers.api_languages).toEqual(["python", "go"]);
    expect(result.answers.mcp_languages).toEqual(["typescript"]);
    expect(result.answers.docs_module).toBe("enabled");
    expect(result.answers.docs_framework).toBe("docusaurus");
    expect(result.answers.saas_infra_module).toBe("enabled");
    expect(result.answers.saas_auth_module).toBe("enabled");
    expect(result.answers.saas_auth_provider).toBe("authjs");
    expect(result.answers.saas_billing_module).toBe("enabled");
    expect(result.answers.saas_billing_provider).toBe("lemonsqueezy");
    expect(result.answers.saas_admin_dashboard).toBe(false);
    expect(
      Object.keys(result.answers).some((key) => key in REMOVED_ANSWER_KEYS),
    ).toBe(false);
  });

  it("already_canonical.yml is a no-op", () => {
    const original = loadFixture("already_canonical.yml");
    const result = applyThenRejectRemovedKeys(original);
    expect(result.answers).toEqual(original);
    expect(result.ops).toEqual([]);
  });

  it("leftover.yml fails closed", () => {
    expect(() =>
      applyThenRejectRemovedKeys(loadFixture("leftover.yml")),
    ).toThrow(/saas_auth/);
  });
});
