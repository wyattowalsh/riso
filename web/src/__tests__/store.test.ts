import { describe, it, expect, beforeEach } from "vitest";
import {
  defaultRisoConfig,
  mergePersistedWizardState,
  useRisoStore,
  type RisoStore,
} from "../lib/store";

describe("Riso Store", () => {
  beforeEach(() => {
    // Reset store state before each test
    useRisoStore.setState({
      config: {
        project_name: "",
        project_layout: "single-package",
        quality_profile: "standard",
        cli_module: "disabled",
        api_module: "disabled",
        api_languages: ["python"],
        docs_module: "enabled",
        docs_framework: "fumadocs",
        ai_tools_module: "enabled",
        saas_infra_module: "disabled",
      },
      history: [],
      currentStep: 0,
    });
  });

  describe("defaults (WEB-T05)", () => {
    it("defaults task_runner to just, OpenSpec off, and no mypy", () => {
      useRisoStore.getState().resetConfig();
      const { config } = useRisoStore.getState();
      expect(config.task_runner).toBe("just");
      expect(config.openspec_extra).toBe("disabled");
      expect(config.saas_auth_provider).toBe("clerk");
      expect(config).not.toHaveProperty("mypy");
      expect(JSON.stringify(config)).not.toMatch(/mypy/);
      expect(JSON.stringify(config)).not.toMatch(/lucia/);
      expect(defaultRisoConfig.task_runner).toBe("just");
      expect(defaultRisoConfig.openspec_extra).toBe("disabled");
      expect(defaultRisoConfig.saas_auth_provider).toBe("clerk");
      expect(defaultRisoConfig).not.toHaveProperty("mypy");
    });

    it("remaps 1.x keys on updateConfig and rejects leftovers", () => {
      const { updateConfig } = useRisoStore.getState();
      updateConfig({
        api_tracks: "python+node",
      } as Partial<import("../lib/store").RisoConfig>);
      const { config } = useRisoStore.getState();
      expect(config.api_module).toBe("enabled");
      expect(config.api_languages).toEqual(["python", "node"]);
      expect(config).not.toHaveProperty("api_tracks");
      expect(() =>
        updateConfig({
          saas_auth: "firebase",
        } as Partial<import("../lib/store").RisoConfig>),
      ).toThrow(/saas_auth/);
    });

    it("defaults saas_admin_dashboard from matrix (true)", () => {
      useRisoStore.getState().resetConfig();
      expect(useRisoStore.getState().config.saas_admin_dashboard).toBe(true);
    });

    it("defaults saas infra extras from copier.yml / matrix", () => {
      useRisoStore.getState().resetConfig();
      const { config } = useRisoStore.getState();
      expect(config.saas_multi_tenancy_level).toBe("teams");
      expect(config.saas_tenancy_model).toBe("b2b-teams");
      expect(config.saas_search_provider).toBe("none");
      expect(config.saas_compliance_level).toBe("basic");
      expect(config.saas_ai_features).toBe("none");
      expect(config.vector_db_provider).toBe("none");
      expect(config.embedding_provider).toBe("openai");
      expect(defaultRisoConfig.saas_multi_tenancy_level).toBe("teams");
      expect(defaultRisoConfig.saas_tenancy_model).toBe("b2b-teams");
      expect(defaultRisoConfig).toHaveProperty("saas_rbac_system");
      expect(defaultRisoConfig).toHaveProperty("saas_ui_framework");
      expect(defaultRisoConfig).toHaveProperty("mcp_example_tools");
      expect(defaultRisoConfig).toHaveProperty("desktop_module");
      expect(defaultRisoConfig).toHaveProperty("go_version");
      expect(defaultRisoConfig.saas_rbac_system).toBe("basic-roles");
      expect(defaultRisoConfig.saas_ui_framework).toBe("shadcn-ui");
      expect(defaultRisoConfig.mcp_example_tools).toBe(true);
      expect(defaultRisoConfig.desktop_module).toBe("disabled");
      expect(defaultRisoConfig.go_version).toBe("1.24");
      expect(config.saas_rbac_system).toBe("basic-roles");
      expect(config.saas_ui_framework).toBe("shadcn-ui");
      expect(config.mcp_example_tools).toBe(true);
      expect(config.desktop_module).toBe("disabled");
      expect(config.go_version).toBe("1.24");
    });
  });

  describe("mergePersistedWizardState", () => {
    const persistedHistory = [
      {
        id: "hist-1",
        name: "Saved",
        config: { project_name: "historic-app" },
        timestamp: new Date("2026-01-01T00:00:00.000Z"),
      },
    ];

    function currentWizardState(): RisoStore {
      return {
        config: { project_name: "live-app", saas_infra_module: "disabled" },
        history: [],
        currentStep: 0,
        highlightedField: null,
        isDrawerOpen: false,
      } as RisoStore;
    }

    it("merges persisted config when href has no share preset", () => {
      const merged = mergePersistedWizardState(
        {
          config: {
            project_name: "persisted-app",
            saas_rbac_system: "custom-permissions",
          },
          history: persistedHistory,
          currentStep: 2,
          highlightedField: "api_module",
        },
        currentWizardState(),
        { href: "https://example.com/wizard" },
      );
      expect(merged.config.project_name).toBe("persisted-app");
      expect(merged.config.saas_rbac_system).toBe("custom-permissions");
      expect(merged.config.saas_infra_module).toBe("disabled");
      expect(merged.history).toHaveLength(1);
      expect(merged.history[0].id).toBe("hist-1");
      expect(merged.currentStep).toBe(2);
      expect(merged.highlightedField).toBe("api_module");
    });

    it("ignores persisted config when href has a share preset", () => {
      const current = currentWizardState();
      const merged = mergePersistedWizardState(
        {
          config: {
            project_name: "persisted-app",
            saas_rbac_system: "custom-permissions",
          },
          history: persistedHistory,
          currentStep: 4,
          highlightedField: "api_module",
        },
        current,
        { href: "https://example.com/wizard?preset=" },
      );
      expect(merged.config).toEqual(current.config);
      expect(merged.config.project_name).toBe("live-app");
      expect(merged.config).not.toHaveProperty("saas_rbac_system");
      expect(merged.history).toHaveLength(1);
      expect(merged.history[0].id).toBe("hist-1");
      expect(merged.history[0].config.project_name).toBe("historic-app");
      expect(merged.currentStep).toBe(current.currentStep);
      expect(merged.highlightedField).toBe("api_module");
    });

    it("clamps persisted Review step when project_name is invalid", () => {
      const merged = mergePersistedWizardState(
        {
          config: { project_name: "bad name" },
          history: [],
          currentStep: 5,
        },
        currentWizardState(),
      );
      expect(merged.currentStep).toBe(0);
      expect(merged.config.project_name).toBe("bad name");
    });
  });

  describe("replaceConfig", () => {
    it("replaces dirty local state instead of merging onto it", () => {
      const { updateConfig, replaceConfig } = useRisoStore.getState();
      updateConfig({ project_name: "dirty-app", api_module: "enabled" });
      expect(useRisoStore.getState().config.api_module).toBe("enabled");

      replaceConfig({ project_name: "preset-app" });
      const { config } = useRisoStore.getState();
      expect(config.project_name).toBe("preset-app");
      expect(config.api_module).toBe(defaultRisoConfig.api_module);
    });
  });

  describe("updateConfig", () => {
    it("updates config with new values", () => {
      const { updateConfig } = useRisoStore.getState();

      updateConfig({ project_name: "test-project" });

      expect(useRisoStore.getState().config.project_name).toBe("test-project");
    });

    it("merges with existing config", () => {
      const { updateConfig } = useRisoStore.getState();

      updateConfig({ project_name: "my-app" });
      updateConfig({ api_module: "enabled", api_languages: ["python"] });

      const { config } = useRisoStore.getState();
      expect(config.project_name).toBe("my-app");
      expect(config.api_module).toBe("enabled");
      expect(config.api_languages).toEqual(["python"]);
    });
  });

  describe("resetConfig", () => {
    it("resets config to defaults", () => {
      const { updateConfig, resetConfig } = useRisoStore.getState();

      updateConfig({
        project_name: "my-app",
        api_module: "enabled",
        api_languages: ["node"],
      });
      resetConfig();

      const { config } = useRisoStore.getState();
      expect(config.project_name).toBe("");
      expect(config.api_module).toBe("disabled");
    });

    it("resets step to 0", () => {
      const { setStep, resetConfig } = useRisoStore.getState();

      setStep(3);
      resetConfig();

      expect(useRisoStore.getState().currentStep).toBe(0);
    });
  });

  describe("setStep", () => {
    it("updates current step when gate allows", () => {
      const { updateConfig, setStep } = useRisoStore.getState();

      updateConfig({ project_name: "step-test" });
      setStep(2);

      expect(useRisoStore.getState().currentStep).toBe(2);
    });

    it("blocks forward jumps without a valid project name", () => {
      const { setStep } = useRisoStore.getState();

      setStep(4);

      expect(useRisoStore.getState().currentStep).toBe(0);
    });

    it("allows review step when project name is valid", () => {
      const { updateConfig, setStep } = useRisoStore.getState();

      updateConfig({ project_name: "gated-app" });
      setStep(5);

      expect(useRisoStore.getState().currentStep).toBe(5);
    });
  });

  describe("setCurrentStep", () => {
    it("is an alias for setStep", () => {
      const { setCurrentStep, updateConfig } = useRisoStore.getState();

      updateConfig({ project_name: "gated-app" });
      setCurrentStep(4);

      expect(useRisoStore.getState().currentStep).toBe(4);
    });
  });

  describe("history", () => {
    it("saves configuration to history", () => {
      const { updateConfig, saveToHistory } = useRisoStore.getState();

      updateConfig({ project_name: "saved-project" });
      saveToHistory("My Saved Config");

      const { history } = useRisoStore.getState();
      expect(history).toHaveLength(1);
      expect(history[0].name).toBe("My Saved Config");
      expect(history[0].config.project_name).toBe("saved-project");
    });

    it("loads configuration from history", () => {
      const { updateConfig, saveToHistory, loadFromHistory, resetConfig } =
        useRisoStore.getState();

      updateConfig({
        project_name: "historic-project",
        api_module: "enabled",
        api_languages: ["python"],
      });
      saveToHistory("Historic Config");

      const historyId = useRisoStore.getState().history[0].id;

      resetConfig();
      expect(useRisoStore.getState().config.project_name).toBe("");

      loadFromHistory(historyId);
      expect(useRisoStore.getState().config.project_name).toBe(
        "historic-project",
      );
      expect(useRisoStore.getState().config.api_module).toBe("enabled");
    });

    it("deletes configuration from history", () => {
      const { saveToHistory, deleteFromHistory } = useRisoStore.getState();

      saveToHistory("Config 1");
      saveToHistory("Config 2");

      expect(useRisoStore.getState().history).toHaveLength(2);

      const idToDelete = useRisoStore.getState().history[0].id;
      deleteFromHistory(idToDelete);

      expect(useRisoStore.getState().history).toHaveLength(1);
    });

    it("limits history to 10 items", () => {
      const { saveToHistory } = useRisoStore.getState();

      for (let i = 0; i < 12; i++) {
        saveToHistory(`Config ${i}`);
      }

      expect(useRisoStore.getState().history).toHaveLength(10);
    });
  });
});
