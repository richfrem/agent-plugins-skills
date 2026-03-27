# Secrets & Environment Configuration Guide

**Scope:** Windows (PowerShell), macOS/Linux
**Purpose:** Securely manage Database credentials and API keys without committing them to git.

---

## Overview

The JUSTIN Modernization environment (5 .NET APIs + 5 Next.js Frontends) relies on environment variables for sensitive connections, particularly the **Oracle Database**.

**⚠️ SECURITY RULE:** NEVER store passwords or keys in `.env` files or commit them to the repository.

---

## 📋 Required Variables

You must configure the following variables in your **Operating System**.

### 🔐 Database Credentials (Oracle)
These allow the .NET APIs to connect to the external Oracle Database.

| Variable | Description | Example |
| :--- | :--- | :--- |
| `Oracle__User` | Database Username | `my_user` |
| `Oracle__Password` | Database Password | `secure_password_123` |
| `Oracle__DataSource` | TNS Connection String | `devdb.bcgov:1521/JUSTINDEV` |

### ☁️ Azure / Authentication (Optional)
Required only if integration with Azure AD or storage is enabled.

| Variable | Description |
| :--- | :--- |
| `Azure__ClientId` | App Registration Client ID |
| `Azure__ClientSecret` | App Secret |
| `Azure__TenantId` | Tenant ID |

---

## 🪟 Windows Setup (Primary)

Since we are using **Windows Direct** (native), you should set these as **User Environment Variables**.

### Method A: Use GUI (Recommended)
1.  Press `Win + S` and search for **"Edit environment variables for your account"**.
2.  Click the result to open.
3.  Under **User variables for <YourUser>**, click **New...**.
4.  Add each variable:
    *   **Name:** `Oracle__User`
    *   **Value:** `your_username`
5.  Repeat for Password and DataSource.
6.  Click **OK**.
7.  **Restart PowerShell/Terminal** for changes to take effect.

### Method B: PowerShell (Persistence)
You can set them permanently via PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("Oracle__User", "your_username", "User")
[Environment]::SetEnvironmentVariable("Oracle__Password", "your_password", "User")
[Environment]::SetEnvironmentVariable("Oracle__DataSource", "your_data_source", "User")
```

---

## 🍎 macOS / Linux Setup

Export these in your shell profile (`~/.zshrc` or `~/.bashrc`).

```bash
export Oracle__User="your_username"
export Oracle__Password="your_password"
export Oracle__DataSource="your_data_source"
```

Then run `source ~/.zshrc` to apply.

---

## 🔍 Verification

To verify your variables are set correctly before running the apps:

**PowerShell:**
```powershell
$env:Oracle__User
```

**Bash:**
```bash
echo $Oracle__User
```

If these commands return your values, the Docker containers (via `podman-compose`) will automatically pick them up and pass them to the .NET APIs.
