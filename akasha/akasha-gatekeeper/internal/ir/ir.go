// internal/ir/ir.go — Shared IR types for Gatekeeper
// These mirror akasha-bridge's ActionIR so observations and actions
// can be deserialized by the Bridge executor without conversion.

package ir

import "time"

// Observation is what Sentinel emits — read-only, no side effects.
type Observation struct {
	Timestamp   time.Time         `json:"timestamp"`
	Actor       string            `json:"actor"`
	Resource    string            `json:"resource"`
	Action      string            `json:"action"`
	Target      string            `json:"target"`
	Scope       string            `json:"scope"`
	Persistence bool              `json:"persistence"`
	Source      string            `json:"source"`
	Metadata    map[string]string `json:"metadata,omitempty"`
}

// ActionIR is what Arbiter emits — consumed by akasha-bridge Executor.
// Must be kept in sync with akasha-bridge/executor/internal/ir/ir.go.
type ActionIR struct {
	ID         string            `json:"id"`
	Effect     string            `json:"effect"`
	Target     string            `json:"target"`
	Params     map[string]string `json:"params"`
	IssuedAt   time.Time         `json:"issued_at"`
	ExpiresAt  time.Time         `json:"expires_at"`
	Capability CapabilityToken   `json:"capability"`
	Reversal   *ReversalPlan     `json:"reversal"`
	Evidence   []string          `json:"evidence"`
	Confidence float64           `json:"confidence"`
	Reasoning  string            `json:"reasoning"`
	// Gatekeeper-specific forensic annotation (optional)
	ELFForensics *ELFForensicResult `json:"elf_forensics,omitempty"`
}

type CapabilityToken struct {
	Allows    []string `json:"allows"`
	Scope     string   `json:"scope"`
	Issuer    string   `json:"issuer"`
	Nonce     string   `json:"nonce"`
	Signature string   `json:"signature"`
}

type ReversalPlan struct {
	UndoEffect string            `json:"undo_effect"`
	Target     string            `json:"target"`
	Deadline   time.Time         `json:"deadline"`
	Params     map[string]string `json:"params"`
}

type ELFForensicResult struct {
	Path            string  `json:"path"`
	Reconstructed   bool    `json:"reconstructed"`
	Stripped        bool    `json:"stripped"`
	Packed          bool    `json:"packed"`
	SuspiciousPerms bool    `json:"suspicious_perms"`
	SectionCount    int     `json:"section_count"`
	ThreatScore     float64 `json:"threat_score"`
	Reasoning       string  `json:"reasoning"`
}
