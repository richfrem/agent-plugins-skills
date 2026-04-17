---
concept: file-namespace-and-class-naming-conventions
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/file-namespace-and-class-naming-conventions.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.748337+00:00
cluster: pascalcase
content_hash: 5f4741412a8ac0cf
---

# File, Namespace, and Class Naming Conventions

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# File, Namespace, and Class Naming Conventions

> **Note:** For guidance on where to place shared React and .NET code, see [Project Directory Structure Requirements](./project-folder-structure-guidance.md). All shared React code must be in `outputs/common/react/` and all shared .NET code in `outputs/common/dotnet/`.

Consistent naming conventions in .NET and React projects improve readability and maintainability. This guide summarizes best practices for naming files, classes, and namespaces, with recommendations for mixed-language projects.

---

## 1. File Naming Conventions

### .NET (C#)
- **General Rule:** Use **PascalCase** for file names (e.g., `MyClass.cs`, `UserService.cs`) to match the public class they contain, following Microsoft's C# coding conventions.
- **Exceptions:** Configuration, script, or non-class files (e.g., `appsettings.json`, `Startup.cs`) may use `camelCase` or `kebab-case` (e.g., `my-config.json`) as per team/project standards.
- **Rationale:** PascalCase aligns with class naming and makes it easy to locate files by class name.

### React (JavaScript/TypeScript)
- **General Rule:** Use **camelCase** (e.g., `myComponent.js`, `userProfile.tsx`) or **kebab-case** (e.g., `my-component.js`) for file names. **camelCase** is more common in modern React/TypeScript projects.
- **Component Files:** File names often match the component name, which is typically **PascalCase** (e.g., `MyComponent.tsx`). However, some projects use `camelCase` for the file (e.g., `myComponent.tsx`) for consistency with other JS files.
- **Rationale:** camelCase/kebab-case aligns with JavaScript ecosystem norms and avoids issues on case-sensitive file systems.

**Recommendation for Mixed Projects:**
- Use **PascalCase** for C# files.
- Use **PascalCase** for React component files (e.g., `MyComponent.tsx`) to match component names, and **camelCase** for non-component files (e.g., `useAuthHook.ts`, `apiClient.js`).
- Choose one style for React files and document it for consistency.

---

## 2. Class Naming Conventions

### .NET (C#)
- **Rule:** Use **PascalCase** for all class names (e.g., `UserService`, `OrderController`).
- **Rationale:** PascalCase distinguishes types from variables/methods (which use camelCase).

### React (TypeScript/JavaScript)
- **Rule:** Use **PascalCase** for all classes and React components (e.g., `MyComponent`, `UserModel`).
- **Rationale:** PascalCase is standard for constructor functions and classes, including functional React components.

**Recommendation:** Use **PascalCase** for all classes in both .NET and React/TypeScript.

---

## 3. Namespace and Directory Naming

### .NET (C#)
- **Rule:** Use **PascalCase** for namespaces (e.g., `MyApp.Services`, `MyApp.Models`).
- **Rationale:** Namespaces are treated like types; PascalCase ensures clarity and consistency.
- **Example:**
  ```csharp
  namespace MyCompany.MyApp.Services;
  ```

### React (JavaScript/TypeScript)
- **Rule:** Use **camelCase** or **kebab-case** for directory names (e.g., `components/userProfile`, `components/user-profile`).
- **Note:** JavaScript/TypeScript does not use namespaces like C#; modules (files) and directories serve as organizational units.
- **If using TypeScript namespaces (rare):** Use **PascalCase** (e.g., `namespace MyApp.Utils`).

**Recommendation:**
- Use **PascalCase** for C# namespaces.
- Use **camelCase** or **kebab-case** for React directories. Avoid TypeScript namespaces in favor of ES module imports.

---

## 4. Best Practices for Mixed .NET and React Projects

- **Consistency:** Agree on conventions upfront and document them (e.g., in `CONTRIBUTING.md` or a style guide).
- **Tooling:**
  - .NET: Use EditorConfig or Roslyn analyzers (e.g., `Microsoft.CodeAnalysis.CSharp`).
  - React: Use ESLint/Prettier with rules like `naming-convention` or `filenames/match-exported`.
- **Cross-Language Alignment:**
  - Use **PascalCase** for C# files/classes and React component files.
  - Use **camelCase** for non-component

*(content truncated)*

## See Also

- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[recent-updates-and-conventions]]
- [[recent-updates-and-conventions]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/file-namespace-and-class-naming-conventions.md`
- **Indexed:** 2026-04-17T06:42:09.748337+00:00
