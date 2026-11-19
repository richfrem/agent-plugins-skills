# Deterministic Code or Generative AI in a Cowork Skill

Where to put the work in a skill: in a script that runs the same way every time, or in the
agent's own reasoning. Cowork usage is metered, so the choice affects cost and speed as well
as reliability.

## Contents

- [The rule](#the-rule)
- [Evidence and what is not measured](#evidence-and-what-is-not-measured)
- [The hybrid pattern we used](#the-hybrid-pattern-we-used)
- [When the sandbox forces the AI route](#when-the-sandbox-forces-the-ai-route)
- [A test to measure cost](#a-test-to-measure-cost)

## The rule

1. **Script anything you can check.** Parsing, splitting, linking, counting, formatting and
   validation belong in a script using tools the sandbox already has (Python with
   pdfplumber or pypdf, pandoc, LibreOffice). The same input gives the same output, and the
   result can be compared with expected values.
2. **Use the agent only for judgment** a script cannot make, such as proposing topic
   boundaries for a document with no headings, or naming things.
3. **Never let the agent rewrite content.** In the converter skills the page text is copied
   from the source unchanged. The agent proposes boundaries and titles only.
4. **Put a human gate on every AI proposal.** Write the proposal to an editable file (a topics
   spreadsheet) and ask the user to confirm before anything is built.
5. **Validate after the build** with numbers (character or word coverage, empty topics,
   warnings), not with a model's opinion.

## Evidence and what is not measured

- **Reported:** when Cowork's built-in `/pdf` skill did the same conversion by agent, the
  user saw it as likely slower and more expensive than running deterministic code.
- **Observed:** on the same manual the body text came out essentially the same from both. The
  built-in route was better in formatting details (list nesting, image labels, a Contents
  list, a richer report), and those were then added to the script.
- **Not measured:** no credit or time figures were recorded. Do not quote a saving. Use the
  [test below](#a-test-to-measure-cost) to get one.

## The hybrid pattern we used

| Step | Done by | Why |
|---|---|---|
| Detect structure (bookmarks, heading sizes, Word heading styles) | Script | Deterministic and free of model cost |
| Propose topics when structure is weak | Agent, from a digest the script wrote | Needs judgment |
| Review and edit topics | The user, in an Excel or CSV file | Human gate |
| Build pages, index, links, media | Script | Repeatable |
| Check coverage and report | Script | Numbers, not opinion |
| Explain results and deliver files | Agent | Natural-language work |

## When the sandbox forces the AI route

Skill scripts may not be on disk in the sandbox (see
[the sandbox findings](cowork-sandbox-findings.md)). If a script cannot run:

- First try reading it with the file viewer and writing it to `/tmp` (not yet tested for a
  large script).
- Otherwise ask the user to attach it. Do not silently fall back to doing the whole job by
  agent, because quality and cost both change. Say so and let the user choose.

## A test to measure cost

Run one document both ways in fresh tasks and record, for each: elapsed time, the credit or
usage figure Cowork shows, whether the output passed the same validation, and how many
manual corrections it needed.

1. Task A: the skill with its script path.
2. Task B: the same request with the built-in agent skill (for a PDF, `/pdf`).

Add the figures to this file with the date and the document size, labelled Measured, and leave
the earlier Reported observation as it is.
