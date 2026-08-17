import { describe, it, expect, beforeEach } from "vitest";
import { defaultRisoConfig, useRisoStore } from "../lib/store";

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
