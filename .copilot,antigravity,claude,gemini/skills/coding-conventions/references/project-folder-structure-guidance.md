# Project Directory Structure Requirements

## Base Directory

When generating modernization code to convert Oracle Forms XML to React + .NET, follow this structure:

**All shared React code must be placed in `modernization/apps/common/react/` and all shared .NET code in `modernization/apps/common/dotnet/`.**

```
modernization/apps/common/react/   # For reusable React components, hooks, forms, utils, config, styles, types
modernization/apps/common/dotnet/  # For reusable .NET controllers, services, DTOs, models, utilities
modernization/apps/{APP_NAME}/     # For application-specific code (APP_NAME = RCC, JAS, JCS, JRS, LEA)
```

## Current Structure Overview

```
modernization/apps/
├── common/
│   ├── config/                    # Shared configuration
│   ├── react/                     # Shared React library (@justin/common npm package)
│   │   ├── components/            # Reusable React components
│   │   ├── forms/                 # Form components (199 forms)
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── api/                   # API client utilities
│   │   ├── config/                # Configuration files
│   │   ├── styles/                # Shared CSS/styling
│   │   ├── types/                 # TypeScript type definitions
│   │   ├── utils/                 # Utility functions
│   │   ├── package.json           # npm package config
│   │   └── index.ts               # Package exports
│   └── dotnet/                    # Shared .NET libraries
│       ├── Controllers/           # Common.Controllers
│       ├── Services/              # Common.Services
│       ├── Models/                # Common.Models
│       ├── Data/                  # Common.Data
│       ├── DTOs/                  # Common.DTOs
│       ├── Utilities/             # Common.Utilities
│       └── ProgramUnits/          # Common.ProgramUnits
│
├── RCC/                           # Records and Court Case
│   ├── next-js/                   # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/               # App router pages
│   │   │   └── components/        # RCC-specific components
│   │   ├── public/                # Static assets
│   │   ├── package.json
│   │   └── next.config.mjs
│   ├── dotnet/                    # .NET API backend
│   │   ├── RCC.Api.csproj
│   │   ├── Program.cs
│   │   └── appsettings.json
│   └── docs/                      # App-specific documentation
│
├── JAS/                           # Justice Administration Services
│   ├── next-js/
│   └── dotnet/
│
├── JCS/                           # Justice Court Services
│   ├── next-js/
│   └── dotnet/
│
├── JRS/                           # Justice Report Services
│   ├── next-js/
│   └── dotnet/
│
└── LEA/                           # Law Enforcement Access
    ├── next-js/
    └── dotnet/
```

## Guidelines

1. **Do NOT duplicate code between apps** - Move shared logic to `common/react/` or `common/dotnet/`
2. **App folders contain only**:
   - Entry points (`Program.cs`, `page.tsx`)
   - Configuration (`appsettings.json`, `.env.local`)
   - App-specific logic unique to that application
3. **Frontends use Next.js** (not plain React) in the `next-js/` folder
4. **Backends are .NET APIs** in the `dotnet/` folder
5. **JSON files must have no comments** (`package.json`, `appsettings.json`, etc.)

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| `package.json` | `apps/{APP}/next-js/` | Frontend dependencies |
| `{APP}.Api.csproj` | `apps/{APP}/dotnet/` | Backend project file |
| `Program.cs` | `apps/{APP}/dotnet/` | .NET entry point |
| `appsettings.json` | `apps/{APP}/dotnet/` | API configuration |
| `next.config.mjs` | `apps/{APP}/next-js/` | Next.js configuration |

## Port Configuration

| App | API Port | UI Port |
|-----|----------|---------|
| LEA | 7009 | 3009 |
| RCC | 7010 | 3010 |
| JAS | 7006 | 3006 |
| JCS | 7007 | 3007 |
| JRS | 7008 | 3008 |

## Enforcement

Any code or documentation not placed in the correct output directory will be considered out of scope and must be moved. All contributors must follow these requirements.