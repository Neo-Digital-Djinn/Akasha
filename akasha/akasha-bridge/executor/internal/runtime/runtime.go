
// runtime.go — Akasha Bridge Executor runtime loop
// Polls action_ir.log, validates CapabilityTokens, executes effects, audits.
// Axiom 1 (Coherence): every action either executes cleanly or fails with a named error.
// Axiom 9 (Stewardship): CapabilityToken + expiry ensures no unbounded authority.

package runtime

import (
	"bufio"
	"encoding/json"
	"log"
	"os"
	"path/filepath"
	"time"

	"akasha-executor/internal/executor"
	"akasha-executor/internal/ir"
)

const (
	defaultBase   = "/var/lib/akasha/bridge"
	actionLogName = "action_ir.log"
	auditLogName  = "akasha-audit.log"
	pollInterval  = 30 * time.Second
)

func Run() error {
	base := defaultBase
	if b := os.Getenv("AKASHA_BRIDGE_DIR"); b != "" {
		base = b
	}

	actionLog := filepath.Join(base, actionLogName)
	auditLog := filepath.Join(base, auditLogName)

	if err := os.MkdirAll(base, 0700); err != nil {
		return err
	}

	log.Printf("Akasha Bridge Executor started")
	log.Printf("Action log:  %s", actionLog)
	log.Printf("Audit log:   %s", auditLog)

	executed := make(map[string]bool)
	ticker := time.NewTicker(pollInterval)
	defer ticker.Stop()

	for range ticker.C {
		actions, err := readActionLog(actionLog)
		if err != nil {
			log.Printf("action log read error: %v", err)
			continue
		}

		for _, action := range actions {
			if executed[action.ID] {
				continue
			}

			log.Printf("→ executing %s: %s on %s (confidence %.0f%%)",
				action.ID, action.Effect, action.Target, action.Confidence*100)

			if err := executor.Execute(action, auditLog); err != nil {
				log.Printf("  ✗ %v", err)
			} else {
				log.Printf("  ✓ success")
				executed[action.ID] = true
			}
		}
	}

	return nil
}

func readActionLog(path string) ([]ir.ActionIR, error) {
	f, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, err
	}
	defer f.Close()

	var actions []ir.ActionIR
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		var a ir.ActionIR
		if err := json.Unmarshal(scanner.Bytes(), &a); err != nil {
			continue
		}
		if time.Now().Before(a.ExpiresAt) {
			actions = append(actions, a)
		}
	}
	return actions, nil
}
