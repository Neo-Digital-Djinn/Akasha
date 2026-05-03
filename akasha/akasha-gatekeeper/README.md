# akasha-gatekeeper

**Security Intelligence Organ**  
Akasha Constellation · Layer: Security Intelligence · Status: Canonical

Gatekeeper observes your system and analyzes threats.  
It does not enforce. `akasha-bridge/executor` enforces.

```
Sentinel (observe) → observations.log
Arbiter  (analyze) → action_ir.log → akasha-bridge/executor → effects + audit
```

---

## Build (Debian 13)

```bash
sudo apt install golang-go
go build -o gatekeeper ./cmd/gatekeeper
```

## Run

```bash
export AKASHA_BRIDGE_DIR=/var/lib/akasha/bridge
export GATEKEEPER_KEY="your-secret-key"   # must match AKASHA_BRIDGE_KEY

# Sentinel (needs root for osquery/Falco/Suricata)
sudo gatekeeper sentinel --osquery --falco --suricata

# Arbiter (unprivileged)
gatekeeper arbiter
```

## Sentinel sources

| Flag | Tool | What it watches |
|---|---|---|
| `--osquery` | osquery | processes, files in /tmp, network sockets |
| `--falco` | Falco | runtime syscall events |
| `--suricata` | Suricata | network IDS alerts |
| _(none)_ | procfs | basic process list fallback |

## Threat patterns (Arbiter)

| Pattern | Effect emitted | Confidence |
|---|---|---|
| Cryptominer process name | kill_process | 0.95 |
| Falco critical/alert | kill_process | 0.95 |
| Falco warning/error | kill_process | 0.75 |
| Suricata scan/brute/exploit | block_ip | 0.85 |
| File created in /tmp,/var/tmp,/dev/shm | quarantine_file | 0.70 |

## Akasha Constellation

- **Layer:** security-intelligence
- **Feeds into:** `akasha-bridge` (execution), `akasha-events`, `akasha-anomaly`
- **Peers:** `akasha-observer`, `akasha-esce`
- **Axiom alignment:** see `repo-manifest.yaml` and `CONSTELLATION_ENTRY.md`
