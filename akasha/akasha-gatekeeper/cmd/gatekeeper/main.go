// cmd/gatekeeper/main.go — Akasha Gatekeeper
// Security intelligence organ. Observes, analyzes, emits ActionIR.
// Does NOT enforce. Enforcement is akasha-bridge/executor's domain.
//
// Usage:
//   gatekeeper sentinel [--osquery] [--falco] [--suricata]
//   gatekeeper arbiter

package main

import (
	"fmt"
	"log"
	"os"

	"akasha-gatekeeper/internal/arbiter"
	"akasha-gatekeeper/internal/sentinel"
)

const version = "2.1.0"

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Akasha Gatekeeper v%s\n", version)
		fmt.Println()
		fmt.Println("Security intelligence organ — observes and analyzes.")
		fmt.Println("Enforcement is handled by: akasha-bridge/executor")
		fmt.Println()
		fmt.Println("Components:")
		fmt.Println("  sentinel   Multi-source observer (osquery / Falco / Suricata / procfs)")
		fmt.Println("  arbiter    Threat analysis — emits ActionIR → akasha-bridge")
		fmt.Println()
		fmt.Println("Usage:")
		fmt.Println("  gatekeeper sentinel [--osquery] [--falco] [--suricata]")
		fmt.Println("  gatekeeper arbiter")
		fmt.Println()
		fmt.Println("Environment:")
		fmt.Println("  AKASHA_BRIDGE_DIR   base directory for shared logs (default: /var/lib/akasha/bridge)")
		fmt.Println("  GATEKEEPER_KEY      HMAC signing key for capability tokens")
		os.Exit(1)
	}

	baseDir := os.Getenv("AKASHA_BRIDGE_DIR")
	if baseDir == "" {
		baseDir = "/var/lib/akasha/bridge"
	}
	os.MkdirAll(baseDir, 0700)

	observationLog := baseDir + "/observations.log"
	actionLog := baseDir + "/action_ir.log" // read by akasha-bridge executor

	signingKey := []byte(os.Getenv("GATEKEEPER_KEY"))
	if len(signingKey) == 0 {
		log.Println("⚠ GATEKEEPER_KEY not set — using default key. Set this in production!")
		signingKey = []byte("akasha-gatekeeper-change-this-key")
	}

	// akasha-bridge executor must use the same key.
	// Set AKASHA_BRIDGE_KEY in the executor environment to match.

	component := os.Args[1]

	var err error
	switch component {
	case "sentinel":
		osquery, falco, suricata := false, false, false
		for _, arg := range os.Args[2:] {
			switch arg {
			case "--osquery":
				osquery = true
			case "--falco":
				falco = true
			case "--suricata":
				suricata = true
			}
		}
		s := sentinel.New(observationLog, osquery, falco, suricata)
		err = s.Run()

	case "arbiter":
		a := arbiter.New(observationLog, actionLog, signingKey)
		err = a.Run()

	default:
		fmt.Fprintf(os.Stderr, "Unknown component: %s\n", component)
		os.Exit(1)
	}

	if err != nil {
		log.Fatal(err)
	}
}
