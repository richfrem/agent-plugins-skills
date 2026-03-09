# Namespace Standards

## Overview

This document outlines the namespace conventions for the JAM Oracle Forms conversion project. Consistent namespaces improve code readability, maintainability, and organization across the monorepo.

## 1. Namespace Conventions

### 1.1 Common Package Namespaces

All code in the common package should use the `Common.*` namespace pattern:

```csharp
namespace Common.Services
namespace Common.Controllers
namespace Common.Models
namespace Common.Utilities
namespace Common.ProgramUnits
namespace Common.Data
```

### 1.2 Application-Specific Namespaces
For code that is specific to one application and not shared:

```csharp
namespace RCC.Services  // Only for RCC-specific services
namespace JCS.Models    // Only for JCS-specific models
```

## 2. Assembly names
While namespaces are consistently Common.*, assembly names may include an application prefix if needed:

```csharp
<PropertyGroup>
  <AssemblyName>Justin.Common.Services</AssemblyName>
</PropertyGroup>
```

## 3. migration from legacy namespaces
Some files currently use Justin.* namespaces. When working with these files:

If making substantial changes, update the namespace to Common.*
Update any references to maintain consistency
Document the namespace change in the commit message

## Service Registration
When registering services with dependency injection, use the full namespace:

```csharp
// CORRECT
builder.Services.AddScoped<Common.Services.JUSE0005Service>();

// INCORRECT
builder.Services.AddScoped<Justin.Services.JUSE0005Service>();
builder.Services.AddScoped<JUSE0005Service>();  // Missing namespace
```

## 5. Best Practices

- Always use full namespaces when registering services in DI
- Maintain consistency with Common.* namespaces for all shared code
- Follow C# namespace conventions (PascalCase for namespace segments)
- Include appropriate subnamespaces for logical grouping (e.g., Common.- Services.Authentication)

### Namespace Structure

The standard namespace structure should be:

- `Justin.Controllers` - For all API controllers
- `Justin.Services` - For all business logic services
- `Justin.Models.[FormName]` - For form-specific models and DTOs
- `Justin.Data` - For database contexts
- `Justin.Data.Entities` - For all entity definitions
- `Justin.Data.Configurations` - For entity configurations
- `Justin.ProgramUnits` - For business logic units
- `Justin.Utilities` - For helper classes and utilities

### Files to Update

The following files currently using `Common` namespace need to be updated to use the `Justin` namespace:

1. `/outputs/common/dotnet/Services/JUSE0005Service.cs` → `namespace Justin.Services`
2. `/outputs/common/dotnet/Controllers/JUSE0005Controller.cs` → `namespace Justin.Controllers`
3. `/outputs/common/dotnet/Models/JUSE0005/*.cs` → `namespace Justin.Models.JUSE0005`
4. `/outputs/common/dotnet/Utilities/ValidationHelper.cs` → `namespace Justin.Utilities`

### Migration Plan

1. Update all namespaces to use the standard `Justin.*` pattern
2. Update all references to the changed namespaces
3. Add appropriate using statements as needed
4. Test all affected components to ensure they still work correctly
5. Update documentation to reflect the standardized namespace approach

This standardization will improve code consistency, reduce confusion, and make the codebase more maintainable in the long run.

## Frontend Considerations

For the React components, the current approach of using relative imports from the common package should be maintained. No changes are needed for the frontend code regarding namespaces.
