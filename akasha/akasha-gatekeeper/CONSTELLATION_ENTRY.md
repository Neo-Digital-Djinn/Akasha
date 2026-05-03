# CONSTELLATION ENTRY — akasha-gatekeeper

**Status:** Canonical  
**Layer:** Security Intelligence  
**Admitted:** 2026-05-02  
**Steward:** Akasha Forge  
**Source Lineage:** Gatekeeper v2.0 (Termux/Android)

---

## Role

`akasha-gatekeeper` is the Akasha Constellation's **security intelligence organ**.

It watches the system (via osquery, Falco, Suricata, or basic procfs), detects
threat patterns, and emits scoped, expiring, HMAC-signed ActionIR records into
the shared `action_ir.log` — which `akasha-bridge/executor` consumes.

**Gatekeeper does not enforce. Bridge executes.**

---

## Why This Split Satisfies Axiom 9

The original Gatekeeper v2.0 had an embedded Enforcer that autonomously
killed processes, blocked IPs, and quarantined files — all without a human
approval gate. That violated Axiom 9 (Stewardship).

The Bridge executor README stated: *"Power is constrained by math, not trust."*

The reconciliation:

| What | Who | How constrained |
|---|---|---|
| Observe | Gatekeeper Sentinel | read-only, no side effects |
| Analyze → ActionIR | Gatekeeper Arbiter | HMAC-signed, scoped, 5-min expiry |
| Execute effects | Bridge Executor | validates CapabilityToken before acting |
| Audit | Bridge Executor | append-only audit log |
| Reversal | Bridge Executor | ReversalPlan in every ActionIR |

The human steward controls: (1) the signing key, (2) whether the Bridge
executor is deployed, (3) the Bridge executor's policy (verify.go).

---

## Constellation Position

```
[akasha-axioms]
      │
      ▼
[akasha-gatekeeper]  ← security intelligence layer
  │   Sentinel: observe → observations.log
  │   Arbiter:  analyze → action_ir.log
      │
      ▼
[akasha-bridge/executor]  ← hardened execution surface
      │
      ├── effects: kill_process, block_ip, quarantine_file
      └── audit:  append-only log + reversal plans
```

---

## Porting Notes (Termux → Debian 13)

| Change | Detail |
|---|---|
| Enforcer removed | No enforcement code in this repo — Bridge owns execution |
| Action output | Arbiter writes `action_ir.log` (not judgments.log) to match Bridge schema |
| CapabilityToken | Replaces Gatekeeper's AuthorityToken — same HMAC pattern, Bridge-compatible |
| Signing key | Via `GATEKEEPER_KEY` env var (must match `AKASHA_BRIDGE_KEY` in executor) |
| journald | Observer uses `journalctl --user` (Debian systemd) instead of Android logcat |
| procfs | `/proc/<pid>/comm` read directly — works identically on Debian |
| libelfmaster | Removed from Go code — ELF forensics optionally delegated to akasha-cipher-lab |

---

## Build (Debian 13)

```bash
sudo apt install golang-go

# Gatekeeper (sentinel + arbiter)
cd akasha-gatekeeper
go build -o gatekeeper ./cmd/gatekeeper

# Bridge executor (runs separately, needs same signing key)
cd ../akasha-bridge/executor
go build -o akasha-bridge-executor ./cmd/executor
```

## Run

```bash
export AKASHA_BRIDGE_DIR=/var/lib/akasha/bridge
export GATEKEEPER_KEY="your-secret-key-here"

# Terminal 1 — Sentinel
sudo gatekeeper sentinel --osquery --falco --suricata

# Terminal 2 — Arbiter
gatekeeper arbiter

# Terminal 3 — Bridge Executor (consumes ActionIR, enforces)
sudo AKASHA_BRIDGE_KEY="your-secret-key-here" akasha-bridge-executor
```
