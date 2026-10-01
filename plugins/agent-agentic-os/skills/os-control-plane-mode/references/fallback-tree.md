# Fallback Tree - os-control-plane-mode

Start from the symptom. Every command here is safe to repeat.

| Symptom | Meaning | Do this |
|---|---|---|
| `status` exit 1, "still installed while disabled" | A resync or manual install brought a member back | Run `disable --yes` again; it reconciles |
| `status` exit 1, "not wired" / "script missing" while enabled | Hooks were reset or reinstalled by an older installer | Run `enable --yes`; it reinstalls and rewires the guards |
| `status` warns "still wired (inert)" while disabled | A guard is wired but exits 0 because of the mode | Harmless; `disable --yes` unwires it |
| `status` warns "stale" | The guard in `.git/hooks` differs from the plugin's copy | Run `enable --yes` (refreshes it) |
| Exit 2: ownership file not found | The plugin was never installed with the syncer here | Run the plugin-syncer first, then retry |
| Exit 2: "in the manifest but not in the ownership file" | A member was renamed or the install is older than the manifest | Run the plugin-syncer to refresh the ownership file, then retry. Nothing was changed |
| Exit 3: the plugin sync failed | Earlier steps were applied; the sync did not finish | Fix the sync error, then re-run the same toggle |
| "unrecognized" for a dispatcher hook | A hand-edited hook mentions the guard in a different shape | Left untouched on purpose. The guard still exits 0 while disabled. Edit the hook by hand if you want it gone |
| "mode file must contain 'enabled' or 'disabled'" | `context/control-plane-mode` is corrupt | Delete the file (missing means enabled) or write a valid word, then run `status` |
| Gates still blocking after `disable` | You are in a different clone, or hooks were reinstalled afterwards | Run `status` in that clone; mode and hooks are per clone |

## Undo

Each toggle backs up the ownership file, mode file and dispatcher hooks to
`context/control-plane-backup/<timestamp>/`. Re-running the opposite toggle is the normal undo;
the backup is the manual one.
