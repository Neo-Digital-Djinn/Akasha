
package ir

import "time"

type ActionIR struct {
	ID         string            `json:"id"`
	Effect     EffectType        `json:"effect"`
	Target     string            `json:"target"`
	Params     map[string]string `json:"params"`

	IssuedAt   time.Time `json:"issued_at"`
	ExpiresAt  time.Time `json:"expires_at"`

	Capability CapabilityToken `json:"capability"`
	Reversal   *ReversalPlan   `json:"reversal"`

	// From analyzer
	Evidence   []string `json:"evidence"`
	Confidence float64  `json:"confidence"`
	Reasoning  string   `json:"reasoning"`
}

type EffectType string

const (
    KillProcess EffectType = "kill_process"
    BlockIP     EffectType = "block_ip"
    Quarantine  EffectType = "quarantine_file"
)

type CapabilityToken struct {
    Allows     []EffectType
    Scope      string
    Issuer     string
    Nonce      string
    Signature  string
}

type ReversalPlan struct {
    UndoEffect EffectType
    Target     string
    Deadline   time.Time
}
