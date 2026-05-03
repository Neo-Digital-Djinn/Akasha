// internal/arbiter/arbiter.go — Gatekeeper Arbiter
// Reads Observations from Sentinel, applies threat patterns,
// emits ActionIR to action_ir.log for akasha-bridge Executor to consume.
//
// KEY DESIGN: Arbiter does NOT enforce. It produces ActionIR.
// Enforcement is the exclusive domain of akasha-bridge/executor.
//
// Axiom 1 (Coherence): every threat becomes a named, scoped, expiring ActionIR.
// Axiom 5 (Traceability): evidence + reasoning logged with every action.
// Axiom 9 (Stewardship): CapabilityToken scopes and expires every action.

package arbiter

import (
	"bufio"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"akasha-gatekeeper/internal/ir"
)

type Arbiter struct {
	observationLog string
	actionLog      string // feeds akasha-bridge executor
	windowSize     time.Duration
	signingKey     []byte
}

func New(observationLog, actionLog string, signingKey []byte) *Arbiter {
	return &Arbiter{
		observationLog: observationLog,
		actionLog:      actionLog,
		windowSize:     5 * time.Minute,
		signingKey:     signingKey,
	}
}

func (a *Arbiter) Run() error {
	log.Println("Gatekeeper Arbiter started")
	log.Printf("Observations: %s", a.observationLog)
	log.Printf("Actions → Bridge: %s", a.actionLog)

	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		obs, err := a.readRecent()
		if err != nil {
			log.Printf("observation read error: %v", err)
			continue
		}
		if len(obs) == 0 {
			continue
		}

		log.Printf("🔍 Arbiter analyzing %d observations...", len(obs))
		actions := a.detect(obs)

		if len(actions) > 0 {
			log.Printf("⚖ Arbiter emitting %d ActionIR records → Bridge", len(actions))
			for _, action := range actions {
				if err := a.emitAction(action); err != nil {
					log.Printf("emit error: %v", err)
				} else {
					log.Printf("  → %s: %s on %s (confidence %.0f%%)",
						action.ID, action.Effect, action.Target, action.Confidence*100)
				}
			}
		}
	}
	return nil
}

// ── Detection ────────────────────────────────────────────────────────────────

func (a *Arbiter) detect(obs []ir.Observation) []ir.ActionIR {
	var actions []ir.ActionIR
	actions = append(actions, a.detectCryptominers(obs)...)
	actions = append(actions, a.detectFalcoThreats(obs)...)
	actions = append(actions, a.detectNetworkThreats(obs)...)
	actions = append(actions, a.detectSuspiciousFiles(obs)...)
	return actions
}

func (a *Arbiter) detectCryptominers(obs []ir.Observation) []ir.ActionIR {
	miners := []string{"xmrig", "minerd", "cryptominer", "cpuminer", "ethminer", "ccminer", "claymore", "t-rex"}
	var actions []ir.ActionIR
	for _, o := range obs {
		if o.Resource != "process" {
			continue
		}
		target := strings.ToLower(o.Target)
		cmdline := strings.ToLower(o.Metadata["cmdline"])
		for _, name := range miners {
			if strings.Contains(target, name) || strings.Contains(cmdline, name) {
				actions = append(actions, a.makeAction("kill_process", o.Actor,
					map[string]string{"pid": o.Actor},
					[]string{fmt.Sprintf("process matches cryptominer pattern: %s (source: %s)", name, o.Source)},
					0.95,
					fmt.Sprintf("known cryptomining software detected: %s", name),
					1*time.Hour,
				))
				break
			}
		}
	}
	return actions
}

func (a *Arbiter) detectFalcoThreats(obs []ir.Observation) []ir.ActionIR {
	var actions []ir.ActionIR
	for _, o := range obs {
		if o.Source != "falco" {
			continue
		}
		priority := strings.ToLower(o.Metadata["priority"])
		var confidence float64
		switch priority {
		case "emergency", "alert", "critical":
			confidence = 0.95
		case "error", "warning":
			confidence = 0.75
		default:
			continue
		}
		actions = append(actions, a.makeAction("kill_process", o.Actor,
			map[string]string{"process": o.Actor},
			[]string{fmt.Sprintf("Falco alert: %s (priority: %s)", o.Action, priority)},
			confidence,
			fmt.Sprintf("Falco runtime threat: %s", o.Action),
			30*time.Minute,
		))
	}
	return actions
}

func (a *Arbiter) detectNetworkThreats(obs []ir.Observation) []ir.ActionIR {
	var actions []ir.ActionIR
	for _, o := range obs {
		if o.Source != "suricata" {
			continue
		}
		cat := strings.ToLower(o.Metadata["category"])
		if !strings.Contains(cat, "scan") && !strings.Contains(cat, "brute") && !strings.Contains(cat, "exploit") {
			continue
		}
		actions = append(actions, a.makeAction("block_ip", o.Actor,
			map[string]string{"ip": o.Actor},
			[]string{fmt.Sprintf("Suricata: %s (category: %s)", o.Metadata["signature"], o.Metadata["category"])},
			0.85,
			fmt.Sprintf("network threat: %s", o.Metadata["signature"]),
			24*time.Hour,
		))
	}
	return actions
}

func (a *Arbiter) detectSuspiciousFiles(obs []ir.Observation) []ir.ActionIR {
	suspiciousDirs := []string{"/tmp", "/var/tmp", "/dev/shm"}
	var actions []ir.ActionIR
	for _, o := range obs {
		if o.Resource != "file" || o.Action != "created" {
			continue
		}
		for _, dir := range suspiciousDirs {
			if strings.HasPrefix(o.Target, dir) {
				actions = append(actions, a.makeAction("quarantine_file", o.Target,
					map[string]string{"path": o.Target},
					[]string{fmt.Sprintf("suspicious file created in %s (source: %s)", dir, o.Source)},
					0.70,
					"executable-like file created in world-writable temp directory",
					7*24*time.Hour,
				))
				break
			}
		}
	}
	return actions
}

// ── ActionIR construction ─────────────────────────────────────────────────────

func (a *Arbiter) makeAction(
	effect, target string,
	params map[string]string,
	evidence []string,
	confidence float64,
	reasoning string,
	reversalTTL time.Duration,
) ir.ActionIR {
	nonce := make([]byte, 8)
	rand.Read(nonce)
	nonceStr := hex.EncodeToString(nonce)

	cap := ir.CapabilityToken{
		Allows:  []string{effect},
		Scope:   "local",
		Issuer:  "akasha-gatekeeper-arbiter",
		Nonce:   nonceStr,
	}
	data := fmt.Sprintf("%s:%s:%s:%s", effect, cap.Scope, cap.Issuer, nonceStr)
	h := hmac.New(sha256.New, a.signingKey)
	h.Write([]byte(data))
	cap.Signature = hex.EncodeToString(h.Sum(nil))

	return ir.ActionIR{
		ID:         fmt.Sprintf("gk-%s-%d", effect, time.Now().UnixNano()),
		Effect:     effect,
		Target:     target,
		Params:     params,
		IssuedAt:   time.Now().UTC(),
		ExpiresAt:  time.Now().UTC().Add(5 * time.Minute),
		Capability: cap,
		Reversal: &ir.ReversalPlan{
			UndoEffect: reverseOf(effect),
			Target:     target,
			Deadline:   time.Now().UTC().Add(reversalTTL),
		},
		Evidence:   evidence,
		Confidence: confidence,
		Reasoning:  reasoning,
	}
}

func reverseOf(effect string) string {
	switch effect {
	case "kill_process":
		return "restart_process"
	case "block_ip":
		return "unblock_ip"
	case "quarantine_file":
		return "restore_file"
	default:
		return "manual_review"
	}
}

// ── I/O ──────────────────────────────────────────────────────────────────────

func (a *Arbiter) readRecent() ([]ir.Observation, error) {
	f, err := os.Open(a.observationLog)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	cutoff := time.Now().UTC().Add(-a.windowSize)
	var obs []ir.Observation
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		var o ir.Observation
		if err := json.Unmarshal(scanner.Bytes(), &o); err != nil {
			continue
		}
		if o.Timestamp.After(cutoff) {
			obs = append(obs, o)
		}
	}
	return obs, nil
}

func (a *Arbiter) emitAction(action ir.ActionIR) error {
	f, err := os.OpenFile(a.actionLog, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		return err
	}
	defer f.Close()
	return json.NewEncoder(f).Encode(action)
}
