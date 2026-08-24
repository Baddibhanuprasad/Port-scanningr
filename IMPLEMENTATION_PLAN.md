# Guardian AV implementation roadmap

## Phase 1 — Service skeleton
- Create the service package structure and entry point.
- Add policy loading, logging, and a placeholder IPC surface.
- Add install and dashboard stubs.

## Phase 2 — Ingestion watchers
- Implement USB device notifications and filesystem watchers.
- Add app-launch integration for messaging and browser download paths.

## Phase 3 — Classification and static scanning
- Add policy-driven tier routing.
- Add hash-based and signature-based static scanning primitives.

## Phase 4 — Sandbox and behavioral monitoring
- Integrate Sandboxie/Windows Sandbox orchestration.
- Add rule-based behavioral scoring and canary handling.

## Phase 5 — Dashboard and installer
- Build the dashboard client around the IPC endpoint.
- Add installer packaging and service management scripts.
