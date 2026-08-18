import { describe, it, expect } from "vitest";
import {
  generateCliCommand,
  generateYamlConfig,
  configToCopierArgs,
  shellEscapeString,
  resolveExportProjectName,
  tryGenerateCliCommand,
  tryGenerateYamlConfig,
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

  it("exports rbac, ui framework, and admin dashboard when saas infra is enabled", () => {
    const args = configToCopierArgs({
      project_name: "saas-rbac-ui",
      saas_infra_module: "enabled",
      saas_rbac_system: "custom-permissions",
      saas_ui_framework: "headless-ui",
      saas_admin_dashboard: true,
    });
    expect(args.saas_rbac_system).toBe("custom-permissions");
    expect(args.saas_ui_framework).toBe("headless-ui");
    expect(args.saas_admin_dashboard).toBe(true);
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
      saas_rbac_system: "custom-permissions",
      saas_ui_framework: "headless-ui",
      saas_admin_dashboard: true,
    });
    expect(args).not.toHaveProperty("saas_multi_tenancy_level");
    expect(args).not.toHaveProperty("saas_tenancy_model");
    expect(args).not.toHaveProperty("saas_search_provider");
    expect(args).not.toHaveProperty("saas_compliance_level");
    expect(args).not.toHaveProperty("saas_ai_features");
    expect(args).not.toHaveProperty("vector_db_provider");
    expect(args).not.toHaveProperty("embedding_provider");
    expect(args).not.toHaveProperty("saas_rbac_system");
    expect(args).not.toHaveProperty("saas_ui_framework");
    expect(args).not.toHaveProperty("saas_admin_dashboard");
  });

  it("exports mcp_transport and mcp_example_tools when mcp_module is enabled", () => {
    const args = configToCopierArgs({
      project_name: "mcp-export",
      mcp_module: "enabled",
      mcp_languages: ["python"],
      mcp_transport: "http",
      mcp_example_tools: false,
    });
    expect(args.mcp_transport).toBe("http");
    expect(args.mcp_example_tools).toBe(false);
  });

  it("exports desktop_framework when desktop_module is enabled", () => {
    const args = configToCopierArgs({
      project_name: "desktop-export",
      desktop_module: "enabled",
      desktop_framework: "tauri",
    });
    expect(args.desktop_module).toBe("enabled");
    expect(args.desktop_framework).toBe("tauri");
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

  it("soft-fails CLI/YAML generate on invalid project_name instead of throwing from try helpers", () => {
    expect(() =>
      generateCliCommand({ project_name: "bad name" }),
    ).toThrow();
    const cli = tryGenerateCliCommand({ project_name: "bad name" });
    expect(cli.ok).toBe(false);
    if (!cli.ok) {
      expect(cli.error.length).toBeGreaterThan(0);
    }
    const yaml = tryGenerateYamlConfig({
      project_name: "ok-project",
      saas_auth: "firebase",
    } as Record<string, unknown>);
    expect(yaml.ok).toBe(false);
  });

  it("aligns Copier when: storage/AI/obs/fixtures on infra; jobs/email/analytics on app; auth on infra", () => {
    const infra = configToCopierArgs({
      project_name: "infra-when",
      saas_infra_module: "enabled",
      saas_storage: "r2",
      saas_ai: "openai",
      saas_observability_sentry: true,
      saas_include_fixtures: true,
      saas_auth_module: "enabled",
      saas_jobs: "triggerdev",
      saas_email: "resend",
      saas_analytics: "posthog",
    });
    expect(infra.saas_storage).toBe("r2");
    expect(infra.saas_ai).toBe("openai");
    expect(infra.saas_observability_sentry).toBe(true);
    expect(infra.saas_include_fixtures).toBe(true);
    expect(infra.saas_auth_module).toBe("enabled");
    expect(infra).not.toHaveProperty("saas_jobs");
    expect(infra).not.toHaveProperty("saas_email");
    expect(infra).not.toHaveProperty("saas_analytics");

    const appOnly = configToCopierArgs({
      project_name: "app-when",
      saas_infra_module: "disabled",
      saas_app_module: "enabled",
      saas_storage: "r2",
      saas_auth_module: "enabled",
      saas_jobs: "triggerdev",
      saas_email: "resend",
      saas_analytics: "posthog",
    });
    expect(appOnly).not.toHaveProperty("saas_storage");
    expect(appOnly).not.toHaveProperty("saas_auth_module");
    expect(appOnly.saas_jobs).toBe("triggerdev");
    expect(appOnly.saas_email).toBe("resend");
    expect(appOnly.saas_analytics).toBe("posthog");
  });

  it("exports desktop/go/mcp/python_versions/include_databases when Copier when matches", () => {
    const args = configToCopierArgs({
      project_name: "extra-modules",
      api_module: "enabled",
      api_languages: ["go"],
      mcp_module: "enabled",
      mcp_languages: ["go"],
      desktop_module: "enabled",
      desktop_framework: "electron-vite",
      desktop_features: "auto_updater",
      desktop_platforms: "mac,windows,linux",
      go_version: "1.24",
      go_framework: "gin",
      mcp_transport: "http",
      mcp_example_tools: true,
      include_databases: "yes",
      ci_platform: "github-actions",
      python_versions: ["3.11", "3.12"],
    });
    expect(args.desktop_module).toBe("enabled");
    expect(args.desktop_framework).toBe("electron-vite");
    expect(args.go_version).toBe("1.24");
    expect(args.go_framework).toBe("gin");
    expect(args.mcp_transport).toBe("http");
    expect(args.mcp_example_tools).toBe(true);
    expect(args.include_databases).toBe("yes");
    expect(args.python_versions).toEqual(["3.11", "3.12"]);
  });

  it("never reintroduces the 8 removed live keys", () => {
    const args = configToCopierArgs({
      project_name: "no-removed",
      saas_infra_module: "enabled",
      saas_auth_module: "enabled",
      saas_billing_module: "enabled",
      saas_app_module: "enabled",
    });
    for (const key of Object.keys(REMOVED_ANSWER_KEYS)) {
      expect(args).not.toHaveProperty(key);
    }
    expect(args).not.toHaveProperty("saas_auth");
    expect(args).not.toHaveProperty("saas_billing");
    expect(args).not.toHaveProperty("include_admin");
  });
});
