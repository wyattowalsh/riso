// Mermaid diagram initialization for Sphinx docs
// Converts highlight-mermaid code blocks to rendered diagrams

import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

// Custom Riso theme for Mermaid
const risoTheme = {
  theme: 'base',
  themeVariables: {
    // General
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontSize: '14px',

    // Primary colors (teal)
    primaryColor: '#ccfbf1',
    primaryBorderColor: '#14b8a6',
    primaryTextColor: '#0f172a',

    // Secondary colors
    secondaryColor: '#f1f5f9',
    secondaryBorderColor: '#94a3b8',
    secondaryTextColor: '#475569',

    // Tertiary colors
    tertiaryColor: '#fef3c7',
    tertiaryBorderColor: '#f59e0b',
    tertiaryTextColor: '#78350f',

    // Lines and edges
    lineColor: '#14b8a6',

    // Text
    textColor: '#1e293b',

    // Notes
    noteBkgColor: '#fef9c3',
    noteTextColor: '#713f12',
    noteBorderColor: '#facc15',

    // Actors (sequence diagrams)
    actorBkg: '#f8fafc',
    actorBorder: '#14b8a6',
    actorTextColor: '#1e293b',
    actorLineColor: '#cbd5e1',

    // Signals
    signalColor: '#14b8a6',
    signalTextColor: '#1e293b',

    // Labels
    labelBoxBkgColor: '#f8fafc',
    labelBoxBorderColor: '#14b8a6',
    labelTextColor: '#1e293b',

    // Loops
    loopTextColor: '#1e293b',

    // Activation
    activationBkgColor: '#ccfbf1',
    activationBorderColor: '#14b8a6',

    // Sequence numbers
    sequenceNumberColor: '#ffffff',

    // Flowchart
    nodeBkg: '#f8fafc',
    nodeBorder: '#14b8a6',
    clusterBkg: '#f1f5f9',
    clusterBorder: '#e2e8f0',
    defaultLinkColor: '#14b8a6',

    // State diagram
    labelColor: '#1e293b',

    // Class diagram
    classText: '#1e293b',

    // Git graph
    git0: '#14b8a6',
    git1: '#f59e0b',
    git2: '#8b5cf6',
    git3: '#ef4444',
    git4: '#3b82f6',
    git5: '#ec4899',
    git6: '#10b981',
    git7: '#f97316',
    gitBranchLabel0: '#ffffff',
    gitBranchLabel1: '#ffffff',
    gitBranchLabel2: '#ffffff',
    gitBranchLabel3: '#ffffff',
    commitLabelColor: '#64748b',
    commitLabelFontSize: '12px',

    // Pie chart
    pie1: '#14b8a6',
    pie2: '#f59e0b',
    pie3: '#8b5cf6',
    pie4: '#ef4444',
    pie5: '#3b82f6',
    pie6: '#ec4899',
    pie7: '#10b981',
    pie8: '#f97316',
    pie9: '#6366f1',
    pie10: '#84cc16',
    pie11: '#06b6d4',
    pie12: '#a855f7',
    pieTitleTextSize: '16px',
    pieTitleTextColor: '#1e293b',
    pieSectionTextSize: '14px',
    pieSectionTextColor: '#ffffff',
    pieLegendTextSize: '14px',
    pieLegendTextColor: '#1e293b',
    pieStrokeColor: '#ffffff',
    pieStrokeWidth: '2px',
  }
};

// Check for dark mode
function isDarkMode() {
  return document.documentElement.getAttribute('data-theme') === 'dark' ||
         (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches &&
          document.documentElement.getAttribute('data-theme') !== 'light');
}

// Dark mode theme overrides
const darkThemeOverrides = {
  primaryColor: '#134e4a',
  primaryBorderColor: '#14b8a6',
  primaryTextColor: '#f1f5f9',
  secondaryColor: '#334155',
  secondaryTextColor: '#cbd5e1',
  tertiaryColor: '#422006',
  tertiaryTextColor: '#fef3c7',
  textColor: '#f1f5f9',
  nodeBkg: '#1e293b',
  clusterBkg: '#334155',
  actorBkg: '#1e293b',
  noteBkgColor: '#422006',
  noteTextColor: '#fef9c3',
  labelBoxBkgColor: '#1e293b',
};

// Initialize mermaid with config
function initMermaid() {
  const config = {
    startOnLoad: false,
    ...risoTheme,
    securityLevel: 'loose',
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: 'basis',
      padding: 15,
    },
    sequence: {
      useMaxWidth: true,
      diagramMarginX: 20,
      diagramMarginY: 20,
      actorMargin: 50,
      boxMargin: 10,
      boxTextMargin: 5,
      noteMargin: 10,
      messageMargin: 35,
      mirrorActors: true,
    },
    gantt: {
      useMaxWidth: true,
      barHeight: 20,
      barGap: 4,
      topPadding: 50,
      leftPadding: 75,
      gridLineStartPadding: 35,
      fontSize: 12,
      numberSectionStyles: 4,
    },
    pie: {
      useMaxWidth: true,
      textPosition: 0.75,
    },
    gitGraph: {
      useMaxWidth: true,
      showCommitLabel: true,
      showBranches: true,
      rotateCommitLabel: true,
    },
  };

  // Apply dark mode overrides if needed
  if (isDarkMode()) {
    Object.assign(config.themeVariables, darkThemeOverrides);
  }

  mermaid.initialize(config);
}

// Convert code blocks to mermaid diagrams
async function renderMermaidDiagrams() {
  const codeBlocks = document.querySelectorAll('.highlight-mermaid');

  for (let i = 0; i < codeBlocks.length; i++) {
    const block = codeBlocks[i];
    const pre = block.querySelector('pre');

    if (!pre) continue;

    // Extract the mermaid code (remove span tags and get text content)
    const code = pre.textContent.trim();

    if (!code) continue;

    // Create container for the diagram
    const container = document.createElement('div');
    container.className = 'mermaid';
    container.id = `mermaid-diagram-${i}`;

    try {
      // Render the diagram
      const { svg } = await mermaid.render(container.id, code);
      container.innerHTML = svg;

      // Replace the code block with the rendered diagram
      block.replaceWith(container);
    } catch (error) {
      console.warn(`Failed to render mermaid diagram ${i}:`, error);
      // Keep the code block visible on error
      block.classList.add('mermaid-error');
    }
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  initMermaid();
  renderMermaidDiagrams();
});

// Re-render on theme change
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.attributeName === 'data-theme') {
      initMermaid();
      // Re-render all diagrams
      document.querySelectorAll('.mermaid').forEach((el, i) => {
        const code = el.getAttribute('data-mermaid-code');
        if (code) {
          mermaid.render(`mermaid-rerender-${i}`, code).then(({ svg }) => {
            el.innerHTML = svg;
          });
        }
      });
    }
  }
});

observer.observe(document.documentElement, { attributes: true });
