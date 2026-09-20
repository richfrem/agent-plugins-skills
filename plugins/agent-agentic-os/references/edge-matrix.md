# Edge matrix: who runs each transition

Legend:
- **AGENT**: You (the agent) run this once the human has said go in chat. Put their words in --human-confirmed. There is no question to ask.
- **SOFT**: Ask the human in chat, then you run this. Do not hand the command to the human.
- **HARD**: Only the human can run this. Give them the complete command; you cannot run it.

| Transition | From | To | Who | Basis | Why |
|---|---|---|---|---|---|
| intake_to_interview | INTAKE | INTERVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| force_retrospective_from_interview | INTERVIEW | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| intake_to_draft_plan | INTAKE | DRAFT_PLAN | AGENT | none | Deterministic checks only; no human decision is needed. |
| intake_to_plan_review | INTAKE | PLAN_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| intake_to_escalated | INTAKE | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| interview_to_draft_plan | INTERVIEW | DRAFT_PLAN | AGENT | none | Deterministic checks only; no human decision is needed. |
| interview_to_plan_review | INTERVIEW | PLAN_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| interview_to_escalated | INTERVIEW | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| draft_plan_to_plan_review | DRAFT_PLAN | PLAN_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| draft_plan_to_interview | DRAFT_PLAN | INTERVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| draft_plan_to_escalated | DRAFT_PLAN | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| multi_agent_review_to_draft_plan | MULTI_AGENT_REVIEW | DRAFT_PLAN | AGENT | none | Deterministic checks only; no human decision is needed. |
| multi_agent_review_to_plan_review | MULTI_AGENT_REVIEW | PLAN_REVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| multi_agent_review_to_escalated | MULTI_AGENT_REVIEW | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| plan_review_to_multi_agent_review | PLAN_REVIEW | MULTI_AGENT_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| plan_review_to_awaiting_approval | PLAN_REVIEW | AWAITING_APPROVAL | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| plan_review_to_draft_plan | PLAN_REVIEW | DRAFT_PLAN | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| plan_review_to_interview | PLAN_REVIEW | INTERVIEW | AGENT | none | Deterministic checks only; no human decision is needed. |
| plan_review_to_escalated | PLAN_REVIEW | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| awaiting_approval_to_approved | AWAITING_APPROVAL | APPROVED | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| awaiting_approval_to_plan_review | AWAITING_APPROVAL | PLAN_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| awaiting_approval_to_draft_plan | AWAITING_APPROVAL | DRAFT_PLAN | AGENT | none | Deterministic checks only; no human decision is needed. |
| awaiting_approval_to_escalated | AWAITING_APPROVAL | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| approved_to_in_worktree | APPROVED | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| approved_to_retrospective_planning_only | APPROVED | RETROSPECTIVE | AGENT | none | Deterministic checks only; no human decision is needed. |
| approved_to_escalated | APPROVED | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| in_worktree_to_worktree_review | IN_WORKTREE | WORKTREE_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| in_worktree_to_rolled_back | IN_WORKTREE | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| in_worktree_to_escalated | IN_WORKTREE | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| worktree_review_to_multi_agent_code_review | WORKTREE_REVIEW | MULTI_AGENT_CODE_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| worktree_review_to_verify_exit | WORKTREE_REVIEW | VERIFY_EXIT | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| worktree_review_to_in_worktree | WORKTREE_REVIEW | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| worktree_review_to_rolled_back | WORKTREE_REVIEW | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| worktree_review_to_escalated | WORKTREE_REVIEW | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| multi_agent_code_review_to_worktree_review | MULTI_AGENT_CODE_REVIEW | WORKTREE_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| multi_agent_code_review_to_verify_exit | MULTI_AGENT_CODE_REVIEW | VERIFY_EXIT | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| multi_agent_code_review_to_in_worktree | MULTI_AGENT_CODE_REVIEW | IN_WORKTREE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| multi_agent_code_review_to_rolled_back | MULTI_AGENT_CODE_REVIEW | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| multi_agent_code_review_to_escalated | MULTI_AGENT_CODE_REVIEW | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_retrospective | VERIFY_EXIT | RETROSPECTIVE | AGENT | none | Deterministic checks only; no human decision is needed. |
| retrospective_to_done | RETROSPECTIVE | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| retrospective_to_escalated | RETROSPECTIVE | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_in_worktree | VERIFY_EXIT | IN_WORKTREE | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_worktree_review | VERIFY_EXIT | WORKTREE_REVIEW | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| verify_exit_to_rolled_back | VERIFY_EXIT | ROLLED_BACK | AGENT | none | Deterministic checks only; no human decision is needed. |
| verify_exit_to_escalated | VERIFY_EXIT | ESCALATED | AGENT | none | Deterministic checks only; no human decision is needed. |
| rolled_back_to_escalated | ROLLED_BACK | ESCALATED | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| rolled_back_to_plan_review | ROLLED_BACK | PLAN_REVIEW | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| escalated_to_intake | ESCALATED | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| escalated_to_plan_review | ESCALATED | PLAN_REVIEW | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| human_force_done__from_INTAKE | INTAKE | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_INTERVIEW | INTERVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_DRAFT_PLAN | DRAFT_PLAN | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_MULTI_AGENT_REVIEW | MULTI_AGENT_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_PLAN_REVIEW | PLAN_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_AWAITING_APPROVAL | AWAITING_APPROVAL | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_APPROVED | APPROVED | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_IN_WORKTREE | IN_WORKTREE | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_WORKTREE_REVIEW | WORKTREE_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_MULTI_AGENT_CODE_REVIEW | MULTI_AGENT_CODE_REVIEW | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_VERIFY_EXIT | VERIFY_EXIT | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_ROLLED_BACK | ROLLED_BACK | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| human_force_done__from_ESCALATED | ESCALATED | DONE | HARD | crypto | Needs the human's SSH signature (passphrase prompt); no typed word or flag can replace it. |
| reset_to_intake__from_INTERVIEW | INTERVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_DRAFT_PLAN | DRAFT_PLAN | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_MULTI_AGENT_REVIEW | MULTI_AGENT_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_PLAN_REVIEW | PLAN_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_AWAITING_APPROVAL | AWAITING_APPROVAL | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_APPROVED | APPROVED | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_IN_WORKTREE | IN_WORKTREE | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_WORKTREE_REVIEW | WORKTREE_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_MULTI_AGENT_CODE_REVIEW | MULTI_AGENT_CODE_REVIEW | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_VERIFY_EXIT | VERIFY_EXIT | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_RETROSPECTIVE | RETROSPECTIVE | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_DONE | DONE | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| reset_to_intake__from_ROLLED_BACK | ROLLED_BACK | INTAKE | HARD | policy | Repo policy reserves this human-typed decision to the human. |
| force_retrospective_from_intake | INTAKE | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_draft_plan | DRAFT_PLAN | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_multi_agent_review | MULTI_AGENT_REVIEW | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_plan_review | PLAN_REVIEW | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_awaiting_approval | AWAITING_APPROVAL | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_rolled_back | ROLLED_BACK | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_escalated | ESCALATED | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_done | DONE | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_in_worktree | IN_WORKTREE | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_worktree_review | WORKTREE_REVIEW | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
| force_retrospective_from_multi_agent_code_review | MULTI_AGENT_CODE_REVIEW | RETROSPECTIVE | SOFT | none | Has a human question: the human answers in chat, then the agent runs the edge. |
