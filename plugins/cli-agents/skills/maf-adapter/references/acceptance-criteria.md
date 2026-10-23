# Acceptance Criteria: Microsoft Agent Framework Adapter (`maf-adapter`)

Verification criteria for Microsoft Agent Framework (MAF) manifest compatibility and execution adapter.

## 1. Manifest Schema Compliance
- [ ] Plugin manifests and skill metadata conform to MAF agent definition specifications.
- [ ] `test_harness.py --validate --plugin <plugin>` completes with exit code 0.

## 2. Tool & Capability Exposition
- [ ] Declared agent capabilities map cleanly to MAF function-calling signatures.
- [ ] No unhandled exceptions during capability simulation or manifest translation.

## 3. Local Test Harness Execution
- [ ] Test harness operates locally without requiring live Azure AI Foundry or remote cloud credentials.
- [ ] Dry-run executions output structured compatibility validation results.
