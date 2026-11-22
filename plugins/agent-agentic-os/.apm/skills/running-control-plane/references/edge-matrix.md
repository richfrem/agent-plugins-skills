# Edge matrix: who runs each transition

Legend:
- **AGENT**: You (the agent) run this once the human has said go in chat. Put their words in --human-confirmed. There is no question to ask.
- **SOFT**: Ask the human in chat, then you run this. Do not hand the command to the human.
- **HARD**: Only the human can run this. Give them the complete command; you cannot run it.

| Transition | From | To | Who | Basis | Why |
|---|---|---|---|---|---|
| intake_to_draft_plan | INTAKE | DRAFT_PLAN | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| intake_to_escalated | INTAKE | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| draft_plan_to_plan_review | DRAFT_PLAN | PLAN_REVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| plan_review_to_approved | PLAN_REVIEW | APPROVED | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| plan_review_to_draft_plan | PLAN_REVIEW | DRAFT_PLAN | AGENT | none | Deterministic checks only; no human decision is needed. |
| approved_to_in_worktree | APPROVED | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| in_worktree_to_worktree_review | IN_WORKTREE | WORKTREE_REVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| in_worktree_to_rolled_back | IN_WORKTREE | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| worktree_review_to_verify_exit | WORKTREE_REVIEW | VERIFY_EXIT | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| worktree_review_to_in_worktree | WORKTREE_REVIEW | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| worktree_review_to_rolled_back | WORKTREE_REVIEW | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_done | VERIFY_EXIT | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| verify_exit_to_in_worktree | VERIFY_EXIT | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_worktree_review | VERIFY_EXIT | WORKTREE_REVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_rolled_back | VERIFY_EXIT | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| rolled_back_to_plan_review | ROLLED_BACK | PLAN_REVIEW | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| rolled_back_to_escalated | ROLLED_BACK | ESCALATED | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| escalated_to_plan_review | ESCALATED | PLAN_REVIEW | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_DRAFT_PLAN | DRAFT_PLAN | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_PLAN_REVIEW | PLAN_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_APPROVED | APPROVED | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_IN_WORKTREE | IN_WORKTREE | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_WORKTREE_REVIEW | WORKTREE_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_VERIFY_EXIT | VERIFY_EXIT | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_ROLLED_BACK | ROLLED_BACK | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_ESCALATED | ESCALATED | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| human_force_done__from_INTAKE | INTAKE | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_DRAFT_PLAN | DRAFT_PLAN | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_PLAN_REVIEW | PLAN_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_APPROVED | APPROVED | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_IN_WORKTREE | IN_WORKTREE | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_WORKTREE_REVIEW | WORKTREE_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_ROLLED_BACK | ROLLED_BACK | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_ESCALATED | ESCALATED | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
