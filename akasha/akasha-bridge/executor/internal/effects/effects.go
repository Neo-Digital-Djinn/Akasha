
// effects.go — Effect backends for the Akasha Bridge Executor
// Ported from Bridge/executor to Debian 13 Linux.
// Axiom 6 (Modularity): each effect is independently replaceable.
// Axiom 7 (Transparency): every effect does exactly what it says, no hidden state.

package effects

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

const quarantineBase = "/var/lib/akasha/bridge/quarantine"

// KillProcess sends SIGKILL to the named process by PID string.
func KillProcess(pid string) error {
	return exec.Command("kill", "-9", pid).Run()
}

// BlockIP adds an iptables INPUT DROP rule for the given IP.
// Requires root / CAP_NET_ADMIN.
func BlockIP(ip string) error {
	return exec.Command("iptables", "-A", "INPUT", "-s", ip, "-j", "DROP").Run()
}

// QuarantineFile moves a file into the Akasha quarantine directory.
// Destination: /var/lib/akasha/bridge/quarantine/<timestamp>-<basename>
// The original path is vacated atomically via os.Rename.
func QuarantineFile(path string) error {
	if err := os.MkdirAll(quarantineBase, 0700); err != nil {
		return fmt.Errorf("quarantine: cannot create quarantine dir: %w", err)
	}

	timestamp := time.Now().UTC().Format("20060102-150405")
	dest := filepath.Join(quarantineBase, fmt.Sprintf("%s-%s", timestamp, filepath.Base(path)))

	if err := os.Rename(path, dest); err != nil {
		return fmt.Errorf("quarantine: rename failed (%s → %s): %w", path, dest, err)
	}

	return nil
}
