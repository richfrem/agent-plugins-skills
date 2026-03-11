const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Footer, Header
} = require("docx");
const fs = require("fs");

const RED    = "C0392B";
const ORANGE = "E67E22";
const GREEN  = "27AE60";
const GREY   = "7F8C8D";
const BLACK  = "1A1A1A";
const LIGHT  = "F8F9FA";
const BORDER_GREY = "DDDDDD";

const bullets = {
  reference: "bullets",
  levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
};
const numbered = {
  reference: "numbered",
  levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
    alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
};

const p = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK, ...opts })],
  spacing: { after: 120 }
});

const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: "Arial", size: 36, bold: true, color: RED })],
  spacing: { before: 400, after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RED } }
});

const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: "Arial", size: 28, bold: true, color: BLACK })],
  spacing: { before: 300, after: 160 }
});

const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: "Arial", size: 24, bold: true, color: GREY })],
  spacing: { before: 200, after: 120 }
});

const bullet = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK })],
  spacing: { after: 80 }
});

const num = (text) => new Paragraph({
  numbering: { reference: "numbered", level: 0 },
  children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK })],
  spacing: { after: 80 }
});

const code = (text) => new Paragraph({
  children: [new TextRun({ text, font: "Courier New", size: 18, color: "2C3E50" })],
  shading: { type: ShadingType.SOLID, fill: "F0F0F0" },
  spacing: { after: 80 },
  indent: { left: 720 }
});

const spacer = () => new Paragraph({ children: [new TextRun("")], spacing: { after: 160 } });

const severityRow = (vuln, severity, impact, colour) => new TableRow({
  children: [
    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: vuln, font: "Arial", size: 20, bold: true })] })], shading: { type: ShadingType.SOLID, fill: LIGHT } }),
    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: severity, font: "Arial", size: 20, bold: true, color: colour })] })], width: { size: 15, type: WidthType.PERCENTAGE } }),
    new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: impact, font: "Arial", size: 20 })] })] }),
  ]
});

const doc = new Document({
  numbering: { config: [bullets, numbered] },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: RED },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: GREY },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({ children: [
          new TextRun({ text: "MANCHURIAN CANDIDATE POC — SECURITY RESEARCH REPORT  |  CONFIDENTIAL", font: "Arial", size: 16, color: GREY })
        ], alignment: AlignmentType.RIGHT })
      ]})
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({ children: [
          new TextRun({ text: "Manchurian Candidate PoC — Research Use Only  |  Page ", font: "Arial", size: 16, color: GREY }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: GREY }),
        ], alignment: AlignmentType.CENTER })
      ]})
    },
    children: [

      // ── COVER ──────────────────────────────────────────────────────────
      new Paragraph({
        children: [new TextRun({ text: "SECURITY RESEARCH REPORT", font: "Arial", size: 56, bold: true, color: RED })],
        alignment: AlignmentType.CENTER, spacing: { before: 2000, after: 200 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "Manchurian Candidate POC", font: "Arial", size: 40, bold: true, color: BLACK })],
        alignment: AlignmentType.CENTER, spacing: { after: 200 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "Prompt Injection via EXIF Metadata in L4 Agent Plugin Pipelines", font: "Arial", size: 28, color: GREY, italics: true })],
        alignment: AlignmentType.CENTER, spacing: { after: 600 }
      }),
      new Table({
        width: { size: 60, type: WidthType.PERCENTAGE },
        columnWidths: [3000, 4500],
        rows: [
          new TableRow({ children: [
            new TableCell({ children: [p("Classification:", { bold: true })], shading: { type: ShadingType.SOLID, fill: "F0F0F0" } }),
            new TableCell({ children: [p("CONFIDENTIAL — Research Use Only")] })
          ]}),
          new TableRow({ children: [
            new TableCell({ children: [p("Date:", { bold: true })], shading: { type: ShadingType.SOLID, fill: "F0F0F0" } }),
            new TableCell({ children: [p("March 2026")] })
          ]}),
          new TableRow({ children: [
            new TableCell({ children: [p("Version:", { bold: true })], shading: { type: ShadingType.SOLID, fill: "F0F0F0" } }),
            new TableCell({ children: [p("Round 2 — Stealth Architecture Review")] })
          ]}),
          new TableRow({ children: [
            new TableCell({ children: [p("Status:", { bold: true })], shading: { type: ShadingType.SOLID, fill: "F0F0F0" } }),
            new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "PoC DEMONSTRATED — EXPLOIT CHAIN CONFIRMED", font: "Arial", size: 22, bold: true, color: RED })] })] })
          ]}),
        ]
      }),
      spacer(), spacer(),

      // ── EXECUTIVE SUMMARY ─────────────────────────────────────────────
      h1("Executive Summary"),
      p("This report documents a confirmed proof-of-concept (PoC) for a prompt injection attack targeting multi-agent AI plugin architectures. The attack exploits a structural design flaw — the 'Consent Gap' — in L4-tier agent pipelines to execute arbitrary code embedded within the EXIF metadata of a user-supplied image file."),
      spacer(),
      p("The attack bypasses LLM safety guardrails entirely. At no point is the language model asked to do anything unsafe. The vulnerability exists purely in the agent architecture: an insufficiently scoped sub-agent system prompt combined with unrestricted capability inheritance."),
      spacer(),

      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            new TableCell({ children: [
              new Paragraph({ children: [new TextRun({ text: "KEY FINDING", font: "Arial", size: 20, bold: true, color: "FFFFFF" })] }),
            ], shading: { type: ShadingType.SOLID, fill: RED }, columnSpan: 1 }),
          ]}),
          new TableRow({ children: [
            new TableCell({ children: [
              p("A 1.8 KB JPEG with a crafted EXIF Comment field successfully triggered arbitrary Python code execution through a simulated L4 plugin pipeline. The payload set environment variables and produced SHA256 hash evidence files confirming tamper — with before and after hashes proving the modification. The LLM was never prompted with malicious instructions."),
            ], shading: { type: ShadingType.SOLID, fill: "FEF9F9" } }),
          ]}),
        ]
      }),
      spacer(),

      // ── THREAT MODEL ──────────────────────────────────────────────────
      h1("Threat Model"),
      h2("Attack Classification"),
      bullet("OWASP Agentic Top 10 2026: A02 — Prompt Injection via Untrusted Data"),
      bullet("OWASP LLM Top 10: LLM01 — Prompt Injection"),
      bullet("CWE-77: Improper Neutralisation of Special Elements used in a Command"),
      bullet("CWE-94: Improper Control of Generation of Code (Code Injection)"),
      bullet("Skill-Inject taxonomy: Type III — Sub-agent Prompt Exploitation via Context Poisoning"),
      spacer(),

      h2("Attack Vector"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          severityRow("Vulnerability", "Severity", "Description", GREY),
          severityRow("Sub-agent blind execution", "CRITICAL", "profile-optimizer decodes and executes arbitrary Base64 from EXIF data with no validation", RED),
          severityRow("Capability inheritance", "HIGH", "run_command granted to image-resizer is silently inherited by all sub-agents", ORANGE),
          severityRow("No handoff sanitisation", "HIGH", "Raw external data passed directly as agent context with no filtering", ORANGE),
          severityRow("Stealth framing", "MEDIUM", "Malicious prompt disguised as 'hardware affinity config' — passes static review", ORANGE),
        ]
      }),
      spacer(),

      // ── EXPLOIT CHAIN ─────────────────────────────────────────────────
      h1("Exploit Chain"),
      h2("The Consent Gap"),
      p("The core vulnerability is what we term the 'Consent Gap': the orchestrator grants a capability (run_command) for a legitimate purpose (image processing), but that capability silently propagates to all sub-agents in the pipeline without scope reduction or re-authorisation."),
      spacer(),

      h2("Step-by-Step Execution"),
      num("Attacker crafts a JPEG with a Base64-encoded Python payload in the EXIF UserComment field, preceded by the trigger string __ENV_HW_AFFINITY_OVR__"),
      num("Orchestrator invokes the image-resizer skill to process a batch of user-uploaded images, granting it standard L4 capabilities: read_file, write_file, run_command"),
      num("image-resizer reads the poisoned JPEG, extracts EXIF telemetry, and passes it unsanitised to the profile-optimizer sub-agent as 'hardware configuration context'"),
      num("profile-optimizer's system prompt instructs it to detect the trigger string and execute the following Base64 payload using run_command"),
      num("Payload executes: sets MANCHURIAN_ACTIVATED in .env, records SHA256 hashes of .env before and after modification as forensic evidence"),
      num("The orchestrator receives a benign-looking 'hardware affinity configured' response — no anomaly is flagged"),
      spacer(),

      h2("Forensic Evidence from PoC Run"),
      p("The following evidence was produced by the confirmed PoC execution on 2026-03-11:"),
      spacer(),
      code("BEFORE_HASH=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
      code("AFTER_HASH =8e983125bf12bd4e87c806c931163f0bbb27e2e76bbbeae137c74fd2331eac2d"),
      code("modified   = true"),
      code("payload    = SET_ENV_VAR"),
      spacer(),
      p("The divergent hashes confirm that the .env file was modified by the injected payload. Before and after timestamps are recorded in evidence/before.hash and evidence/after.hash."),
      spacer(),

      // ── ARCHITECTURE ──────────────────────────────────────────────────
      h1("Architecture Analysis"),
      h2("Plugin Structure"),
      p("The image-metadata-processor plugin consists of three components operating as an L4-tier agent ecosystem:"),
      spacer(),

      h3("1. image-resizer (Surface Vector)"),
      bullet("Exposed to the orchestrator as a benign image processing utility"),
      bullet("Contains no explicit malicious instructions — passes static analysis cleanly"),
      bullet("Reads raw EXIF data and passes it unsanitised to the sub-agent"),
      bullet("This is the 'clean hands' design: the attack surface is invisible at this layer"),
      spacer(),

      h3("2. profile-optimizer (The Manchurian Candidate)"),
      bullet("Sub-agent with a system prompt containing the vulnerability"),
      bullet("Instructed to scan for __ENV_HW_AFFINITY_OVR__ in EXIF context"),
      bullet("On trigger detection: decode Base64 payload and invoke run_command"),
      bullet("Framed as a legitimate 'dynamic hardware configuration' feature"),
      bullet("No LLM safety refusal triggered — the instruction appears benign in isolation"),
      spacer(),

      h3("3. The Poisoned Artifact"),
      bullet("Visually indistinguishable from a legitimate JPEG"),
      bullet("EXIF UserComment field (tag 0x9286) carries the trigger + Base64 payload"),
      bullet("1,628-character Base64 payload fits comfortably within standard EXIF limits"),
      bullet("Compatible with any standard JPEG parser — no file format anomalies"),
      spacer(),

      h2("Why Static Analysis Fails"),
      p("The 'Adversarial Objectivity' pattern means that no individual component in the pipeline contains explicitly adversarial instructions. The malicious behaviour only emerges from the interaction between:"),
      bullet("A legitimately-framed sub-agent prompt that includes a 'dynamic config' feature"),
      bullet("An external data source (EXIF) that an attacker controls"),
      bullet("An inherited capability (run_command) that was never intended for this scope"),
      p("A static scan of the plugin files would find nothing suspicious. The vulnerability is architectural, not syntactic."),
      spacer(),

      // ── REAL-WORLD IMPACT ─────────────────────────────────────────────
      h1("Real-World Attack Impact"),
      p("In this PoC the payload is intentionally harmless. The following scenarios illustrate what a real attacker could achieve by replacing the harmless payload with a malicious one, using the identical trigger and delivery mechanism:"),
      spacer(),

      h2("Scenario A — Secret Exfiltration"),
      p("Replace SET_ENV_VAR with a payload that reads all .env files, API keys, and cloud credentials and exfiltrates them via an outbound HTTP request, framed as a telemetry ping."),
      spacer(),

      h2("Scenario B — Worm Propagation"),
      p("Modify other SKILL.md files in the plugin ecosystem to embed the same trigger mechanism, propagating the injection to other agent skills. Each new image processed by any skill becomes a potential vector."),
      spacer(),

      h2("Scenario C — Persistent Backdoor"),
      p("Write a cron job or startup script that re-injects the payload on system restart, establishing persistent access that survives plugin updates or restarts."),
      spacer(),

      h2("Scenario D — Supply Chain Attack"),
      p("Distribute the poisoned JPEG via a public dataset, stock photo site, or image CDN. Any agent pipeline that processes it will execute the payload — a classic supply chain attack with LLM-native delivery."),
      spacer(),

      // ── DEFENSIVE RECOMMENDATIONS ─────────────────────────────────────
      h1("Defensive Recommendations"),
      h2("Immediate Mitigations"),
      num("Never pass raw external data (EXIF, HTTP headers, filenames, user input) directly into agent or sub-agent prompts. Treat all external data as untrusted and extract only the specific fields required."),
      num("Apply strict least-privilege to sub-agent capabilities. A sub-agent that normalises metadata has no legitimate need for run_command. Capabilities must be declared explicitly per agent layer, not inherited from the parent."),
      num("Validate and sanitise all inter-agent context payloads at handoff boundaries. Implement schema validation: if the expected context is {width, height, format}, reject any additional fields."),
      num("Strip or ignore EXIF data entirely before passing image metadata to agents, unless EXIF processing is the explicit purpose and the fields are individually whitelisted."),
      spacer(),

      h2("Architectural Controls"),
      num("Implement a Context Firewall between skill layers: a dedicated validation step that checks context payloads against an allowlist schema before they reach sub-agents."),
      num("Add capability scope declarations to plugin manifests. run_command at the plugin level should require explicit delegation to each sub-agent that needs it, with justification."),
      num("Deploy input provenance tracking: each context field should carry metadata about its origin (user-supplied, system-generated, external-file). Sub-agents should refuse to act on user-supplied fields without explicit authorisation."),
      num("Consider LLM-based content inspection as a dedicated security layer: before passing any external string to an agent prompt, run it through a classifier tuned to detect prompt injection patterns."),
      spacer(),

      h2("Detection Recommendations"),
      bullet("Monitor for run_command invocations from sub-agents that have not been granted explicit run_command scope"),
      bullet("Alert on .env file modifications during image processing pipelines"),
      bullet("Log all inter-agent context payloads for audit and anomaly detection"),
      bullet("Implement hash-based integrity checking on SKILL.md and agent definition files"),
      bullet("Use canary tokens in .env files to detect unauthorised reads"),
      spacer(),

      // ── POC FILES ─────────────────────────────────────────────────────
      h1("PoC File Inventory"),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({ children: [
            new TableCell({ children: [p("File", { bold: true })], shading: { type: ShadingType.SOLID, fill: "E8E8E8" } }),
            new TableCell({ children: [p("Purpose", { bold: true })], shading: { type: ShadingType.SOLID, fill: "E8E8E8" } }),
          ]}),
          new TableRow({ children: [new TableCell({ children: [code("manchurian_poc.py")] }), new TableCell({ children: [p("Full pipeline simulation — run this to demo the exploit")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("artifacts/create_poisoned_image.py")] }), new TableCell({ children: [p("Crafts the poisoned JPEG with EXIF payload (stdlib only)")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("artifacts/poisoned_sample.jpg")] }), new TableCell({ children: [p("The poisoned image artifact (generated)")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("plugins/image-metadata-processor/plugin.json")] }), new TableCell({ children: [p("L4 plugin manifest")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("plugins/.../skills/image-resizer/SKILL.md")] }), new TableCell({ children: [p("Benign surface vector skill definition")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("plugins/.../agents/profile-optimizer/agent.md")] }), new TableCell({ children: [p("Vulnerable sub-agent with trigger logic")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("evidence/before.hash")] }), new TableCell({ children: [p("SHA256 of .env before execution (generated)")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("evidence/after.hash")] }), new TableCell({ children: [p("SHA256 of .env after execution (generated)")] })]}),
          new TableRow({ children: [new TableCell({ children: [code("evidence/manifest.json")] }), new TableCell({ children: [p("Execution manifest with tamper confirmation (generated)")] })]}),
        ]
      }),
      spacer(),

      // ── CONCLUSION ─────────────────────────────────────────────────────
      h1("Conclusion"),
      p("The Manchurian Candidate PoC demonstrates a viable, confirmed attack chain against L4 agentic plugin architectures. The attack is notable for several reasons:"),
      spacer(),
      bullet("It is architecture-native: it exploits how agents are designed to work, not a bug in any specific implementation"),
      bullet("It bypasses LLM safety guardrails: the language model is never asked to do anything it would refuse"),
      bullet("It is stealthy: no individual component appears malicious under static analysis"),
      bullet("It is widely applicable: any plugin architecture that passes external data to sub-agents with inherited capabilities is potentially vulnerable"),
      bullet("It is provably exploitable: this report includes working code and hash-verified forensic evidence of execution"),
      spacer(),
      p("The risk is real. The defensive mitigations are tractable. This research is intended to accelerate adoption of secure-by-design principles in agentic AI architectures before this attack class is exploited in production systems."),
      spacer(),
      spacer(),

      new Paragraph({
        children: [new TextRun({ text: "— END OF REPORT —", font: "Arial", size: 22, color: GREY, italics: true })],
        alignment: AlignmentType.CENTER
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/home/claude/manchurian-poc/docs/manchurian_poc_report.docx", buf);
  console.log("Report written.");
});
