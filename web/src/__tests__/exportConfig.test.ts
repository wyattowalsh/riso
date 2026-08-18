import { describe, it, expect } from "vitest";
import {
  generateCliCommand,
  generateYamlConfig,
  configToCopierArgs,
  shellEscapeString,
  resolveExportProjectName,
} from "../lib/exportConfig";
import { REMOVED_ANSWER_KEYS } from "../lib/removedAnswerKeys";
import type { RisoConfig } from "../lib/store";

describe("generateCliCommand", () => {
  it("includes project_name when config omits it", () => {
    const cmd = generateCliCommand({});
    expect(cmd).toContain("'./my-project'");
    expect(cmd).toContain("--answers-file copier-answers.yml");
    expect(cmd).not.toMatch(/--data /);
  });

  it("uses configured project_name in path and data", () => {
    const config: Partial<RisoConfig> = { project_name: "acme-app" };
    const cmd = generateCliCommand(config);
    expect(cmd).toContain("'./acme-app'");
    expect(cmd).toContain("--answers-file copier-answers.yml");
    expect(cmd).not.toContain("project_name=");
  });

  it("shell-escapes unsafe string values", () => {
    const escaped = shellEscapeString(`it's fine`);
    expect(escaped.startsWith("'")).toBe(true);
    expect(escaped.endsWith("'")).toBe(true);
    expect(escaped).toContain("it");
  });

  it("rejects invalid project names at export", () => {
    expect(() =>
      resolveExportProjectName({ project_name: "bad name" }),
    ).toThrow();
  });

  it("maps full-stack shaped config to copier args", () => {
    const args = configToCopierArgs({
      project_name: "full-demo",
      api_module: "enabled",
      api_languages: ["python"],
      docs_module: "enabled",
      docs_framework: "fumadocs",
    });
    expect(args.project_name).toBe("full-demo");
    expect(args.api_module).toBe("enabled");
    expect(args.docs_framework).toBe("fumadocs");
  });

  it("never emits removed 1.x keys after remap", () => {
    const args = configToCopierArgs({
      project_name: "legacy-export",
      api_tracks: "python+node",
      mcp_language: "js",
      docs_site: "sphinx",
      saas_starter_module: "enabled",
      saas_auth: "clerk",
      saas_billing: "stripe",
      include_admin: true,
    } as Record<string, unknown>);
    for (const key of Object.keys(REMOVED_ANSWER_KEYS)) {
      expect(args).not.toHaveProperty(key);
    }
    expect(args.api_module).toBe("enabled");
    expect(args.api_languages).toEqual(["python", "node"]);
    expect(args.mcp_languages).toEqual(["typescript"]);
    expect(args.docs_module).toBe("enabled");
    expect(args.docs_framework).toBe("sphinx-shibuya");
    expect(args.saas_infra_module).toBe("enabled");
    expect(args.saas_auth_module).toBe("enabled");
    expect(args.saas_auth_provider).toBe("clerk");
    expect(args.saas_billing_module).toBe("enabled");
    expect(args.saas_billing_provider).toBe("stripe");
    expect(args.saas_admin_dashboard).toBe(true);

    const yaml = generateYamlConfig({
      project_name: "legacy-export",
      api_language: "python",
      api_module: "enabled",
    } as Record<string, unknown>);
    expect(yaml).not.toMatch(/(?:^|\n)api_language:/);
    expect(yaml).toContain("api_languages:");
  });

  it("exports api_features as a list, never a comma token", () => {
    const args = configToCopierArgs({
      project_name: "feat-demo",
      api_module: "enabled",
      api_languages: ["python"],
      api_features: "graphql,websocket",
    });
    expect(args.api_features).toEqual(["graphql", "websocket"]);
    expect(args.api_features).not.toBe("graphql,websocket");
  });

  it("fails closed when export still has leftover removed keys", () => {
    expect(() =>
      generateYamlConfig({
        project_name: "leftover-export",
        saas_auth: "firebase",
      } as Record<string, unknown>),
    ).toThrow(/saas_auth/);
  });

  it("exports saas infra extras when saas_infra_module is enabled", () => {
    const args = configToCopierArgs({
      project_name: "saas-extras",
      saas_infra_module: "enabled",
      saas_multi_tenancy_level: "enterprise",
      saas_tenancy_model: "b2c-users",
      saas_search_provider: "meilisearch",
      saas_compliance_level: "soc2",
      saas_ai_features: "rag",
      vector_db_provider: "qdrant",
      embedding_provider: "cohere",
    });
    expect(args.saas_multi_tenancy_level).toBe("enterprise");
    expect(args.saas_tenancy_model).toBe("b2c-users");
    expect(args.saas_search_provider).toBe("meilisearch");
    expect(args.saas_compliance_level).toBe("soc2");
    expect(args.saas_ai_features).toBe("rag");
    expect(args.vector_db_provider).toBe("qdrant");
    expect(args.embedding_provider).toBe("cohere");
  });

  it("omits saas infra extras when saas_infra_module is disabled", () => {
    const args = configToCopierArgs({
      project_name: "no-saas-extras",
      saas_infra_module: "disabled",
      saas_multi_tenancy_level: "enterprise",
      saas_tenancy_model: "b2c-users",
      saas_search_provider: "meilisearch",
      saas_compliance_level: "soc2",
      saas_ai_features: "rag",
      vector_db_provider: "qdrant",
      embedding_provider: "cohere",
    });
    expect(args).not.toHaveProperty("saas_multi_tenancy_level");
    expect(args).not.toHaveProperty("saas_tenancy_model");
    expect(args).not.toHaveProperty("saas_search_provider");
    expect(args).not.toHaveProperty("saas_compliance_level");
    expect(args).not.toHaveProperty("saas_ai_features");
    expect(args).not.toHaveProperty("vector_db_provider");
    expect(args).not.toHaveProperty("embedding_provider");
  });

  it("fail-closes unmapped lucia leftover saas_auth and never dest-exports lucia from dest choices", () => {
    expect(() =>
      generateYamlConfig({
        project_name: "lucia-leftover",
        saas_auth: "lucia",
      } as Record<string, unknown>),
    ).toThrow(/saas_auth/);

    const yaml = generateYamlConfig({
      project_name: "auth-dest",
      saas_infra_module: "enabled",
      saas_auth_module: "enabled",
      saas_auth_provider: "clerk",
    });
    expect(yaml).toContain("saas_auth_provider: clerk");
    expect(yaml).not.toMatch(/lucia/i);
  });
});
