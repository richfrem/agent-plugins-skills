# Recent Updates and Conventions

## Module and Build System Updates

- **ES6 Module Syntax:**
  - All processor, utility, and test scripts now use ES6 module syntax (`import`/`export`) for compatibility and maintainability.
- **NPM Build of Common Components:**
  - The `common` package is now built as its own local NPM package (`@modernization/apps/common`).
  - Manual versioning is used for the common package to avoid accidental mismatches.
  - Peer dependencies for React, MUI, and type definitions ensure version alignment with consuming apps.
- **Build Automation:**
  - The `rebuild-all.ps1` PowerShell script automates cleaning, building, and installing the common package and the RCC React app.
  - All shell commands use full absolute paths to avoid path resolution issues.
- **ESM Output:**
  - All code is output as ESM (ECMAScript Module) instead of CommonJS.
  - `tsconfig.json` in both `common` and `RCC/react` uses `"module": "ESNext"` and `"moduleResolution": "NodeNext"`.
  - All `package.json` files set `"type": "module"`.
  - All import/export statements use ESM syntax (no `require`).

## Input and Test Data Handling

- **Application-Specific Input Directories:**
  - Automated scripts create and manage app-specific input directories for both XML and MD files.
  - XML files for each app (JAS, JCS, JRS, LEA, RCC) are copied to `/{YOUR_PROJECT_DIRECTORY}/inputs/XML/{APP}/` using dependency lists and object tags.
  - MD files (e.g., `OBJECTID-FormModule.md`) are copied to `/{YOUR_PROJECT_DIRECTORY}/inputs/MDs/{APP}/` using the same logic.
  - Destination folders are cleared before copying to ensure clean, reproducible input sets for each application.
- **Test Script Improvements:**
  - Test scripts for processors (e.g., `LovReactProcessor`, `LovColumnMappingProcessor`) use real XML test data from `/test-data/` and output results to `/test-outputs/`.
  - Shared XML/test utility scripts (`xmlUtils.js`, `codeUtils.js`, `testUtils.js`) are used for consistent XML parsing and test data handling.
  - Test scripts process all XML files in their relevant test-data folders, improving coverage and automation.

## React Application Patterns

- **Config-Driven Menu/Layout:**
  - Implemented config-driven `AppMenu` and `AppTitle` using `menuConfig.ts` and `FormAndReportList.ts` (per-app). These configuration files should be generated for each application.
  - All imports in the RCC React app use `@modernization/apps/common` instead of relative paths to the shared folder.
  - Import path and casing issues have been fixed for cross-platform compatibility.
- **Component and Prop Fixes:**
  - Added missing props and types to custom components (e.g., `onLovTrigger`, `showAlert`, buttons).
  - Fixed all import path and casing issues for form and custom components.
  - Removed or commented out all imports from non-existent .NET model files.
- **API and State Management Refactors:**
  - Refactored `baseApi.ts` to export a generic `baseApiFetch<T>()` function for type safety and ESM compatibility.
  - Updated all usages of `baseApiFetch` to use the new generic signature.
  - Refactored all state update patterns to use partial state objects (not updater functions) to match the new `useFormState` signature.

## UI/UX and Design System Alignment

- **Alerts/Dialogs Alignment:**
  - Explicit requirement for BC Gov Design System alignment for generated React Alert/Dialogs, with a validation process involving a test harness (`test-harness/react/`).
- **General Conventions:**
  - Modular, config-driven, LLM/developer-friendly generation.
  - All final outputs are under `outputs/{APP_NAME}/`.
  - Ongoing documentation updates.

## Dependency and Version Alignment

- Ensured both `common` and `RCC/react` use the same versions for React, MUI, and type definitions to avoid peer dependency conflicts.

## Clean Build Verification

- Cleaned and rebuilt both `common` and `RCC/react` multiple times to verify that all TypeScript, Vite, and runtime errors were resolved.
- Confirmed that the RCC React app now builds and runs successfully using the shared `@modernization/apps/common` package.