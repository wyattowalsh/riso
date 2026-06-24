# Warnings Module

Focused, modular components for displaying dependency validation warnings and cost estimates.

## Structure

```
warnings/
├── index.tsx                  # Main exports
├── DependencyWarnings.tsx     # Container/orchestrator (142 LOC)
├── WarningItem.tsx            # Single warning display (162 LOC)
├── CostEstimateCard.tsx       # Cost summary display (85 LOC)
└── QuickFixButton.tsx         # One-click fix action (54 LOC)
```

**Related:**
- `/web/src/lib/useValidation.ts` - Validation logic hook (238 LOC)
- `/web/src/components/DependencyWarnings.tsx` - Main module entry (160 LOC, re-exports + utilities)

## Components

### DependencyWarnings (Main Orchestrator)

Slim orchestrator that coordinates validation warnings display.

**Props:**
- `showEmpty?: boolean` - Show success message when no warnings
- `className?: string` - Additional CSS classes
- `onNavigateToStep?: (step: number) => void` - Callback for navigation

**Usage:**
```tsx
import { DependencyWarnings } from '../components/DependencyWarnings'

<DependencyWarnings showEmpty onNavigateToStep={handleNavigate} />
```

### WarningItem

Displays a single validation warning with interactive actions.

**Features:**
- Severity-based styling (error, warning, info)
- Collapsible details
- Quick-fix buttons
- Navigation to related fields
- Dismissal for info-level warnings

**Props:**
- `warning: Warning` - Warning data
- `onNavigate: (field: string) => void` - Navigation handler
- `onDismiss: (id: string) => void` - Dismiss handler

### CostEstimateCard

Displays estimated monthly costs for third-party services.

**Features:**
- Expandable service breakdown
- Monthly cost summary
- Free tier indicators

**Props:**
- `estimate: ReturnType<typeof getCostEstimate>` - Cost data
- `className?: string` - Additional CSS classes

### QuickFixButton

One-click action button for applying configuration fixes.

**Features:**
- Severity-appropriate styling
- Lightning bolt icon
- Hover effects

**Props:**
- `label: string` - Button text
- `onClick: () => void` - Click handler
- `severity: 'error' | 'warning' | 'info'` - Styling level
- `className?: string` - Additional CSS classes

## Validation Hook

### useValidation

Custom hook that extracts all validation logic.

**Usage:**
```tsx
import { useValidation } from '../../lib/useValidation'

const { warnings, errors, warningList, infos, costEstimate, hasIssues } =
  useValidation(config, updateConfig, dismissedIds)
```

**Returns:**
- `warnings: Warning[]` - All warnings
- `errors: Warning[]` - Error-level warnings
- `warningList: Warning[]` - Warning-level items
- `infos: Warning[]` - Info-level recommendations
- `costEstimate` - Cost estimate data
- `hasIssues: boolean` - Whether any issues exist

## Utility Components

These remain in `/web/src/components/DependencyWarnings.tsx`:

### InlineDependencyWarning

Compact inline warning for form fields.

**Props:**
- `field: string` - Field name to check
- `className?: string` - Additional CSS classes

### DependencyBadge

Summary badge showing validation status.

**Props:**
- `className?: string` - Additional CSS classes

**Display:**
- Valid (green) - No issues
- N issues (red) - Error count
- N recommendations (amber) - Warning/info count

## Design Patterns

### Severity Color Mapping

```tsx
error:   red-50/red-900   (border: red-200/red-800)
warning: amber-50/amber-900 (border: amber-200/amber-800)
info:    blue-50/blue-900  (border: blue-200/blue-800)
```

### Warning Categorization

1. **Errors** - Must be fixed (e.g., missing required dependencies)
2. **Warnings** - Should be addressed (e.g., experimental features)
3. **Info** - Recommendations (e.g., best practices)

### Quick-Fix Actions

Quick fixes apply configuration updates via:
```tsx
fix: {
  label: 'Use Clerk',
  action: () => updateConfig({ saas_auth_provider: 'clerk' })
}
```

### Field Navigation

Navigation maps fields to wizard steps:
- `saas_*` → Step 3 (SaaS Config)
- `fumadocs_*`, `docusaurus_*` → Step 2 (Docs Config)
- `ai_tools_*` → Step 4 (AI Tools)
- `*_module`, `*_languages` → Step 1 (Modules)

## Animation Styles

Warnings appear with smooth transitions:
- `transition-colors` on hover
- `hover:opacity-70` for dismiss buttons
- `hover:underline` for navigation links

## Backward Compatibility

The original `/web/src/components/DependencyWarnings.tsx` now:
1. Re-exports all components from `./warnings/`
2. Maintains utility components (InlineDependencyWarning, DependencyBadge)
3. Preserves all existing imports

Existing code importing from `../components/DependencyWarnings` continues to work unchanged.

## Refactoring Benefits

1. **Focused Responsibility** - Each component has a single purpose
2. **Reusability** - Components can be imported individually
3. **Maintainability** - Easier to locate and update specific functionality
4. **Testability** - Smaller components are easier to test
5. **Performance** - Potential for better code splitting
6. **Readability** - Reduced cognitive load per file (< 150 LOC each)

## Migration Guide

No migration needed! The refactoring maintains full backward compatibility.

To use new direct imports:
```tsx
// Old (still works)
import { DependencyWarnings, WarningItem } from '../components/DependencyWarnings'

// New (more explicit)
import { DependencyWarnings } from '../components/warnings/DependencyWarnings'
import { WarningItem } from '../components/warnings/WarningItem'

// Or from index
import { DependencyWarnings, WarningItem } from '../components/warnings'
```
