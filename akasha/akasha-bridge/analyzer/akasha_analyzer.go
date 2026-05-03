package main

import (
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// ============================================================================
// BEHAVIOR IR (from Observer)
// ============================================================================

type BehaviorIR struct {
	Timestamp   time.Time `json:"timestamp"`
	Actor       string    `json:"actor"`
	Resource    string    `json:"resource"`
	Action      string    `json:"action"`
	Target      string    `json:"target"`
	Scope       string    `json:"scope"`
	Persistence bool      `json:"persistence"`
	Source      string    `json:"source"`
}

// ============================================================================
// ACTION IR (to Executor)
// ============================================================================

type ActionIR struct {
	ID         string                 `json:"id"`
	Effect     string                 `json:"effect"`
	Target     string                 `json:"target"`
	Params     map[string]string      `json:"params"`
	IssuedAt   time.Time              `json:"issued_at"`
	ExpiresAt  time.Time              `json:"expires_at"`
	Capability CapabilityToken        `json:"capability"`
	Reversal   *ReversalPlan          `json:"reversal"`
	Evidence   []string               `json:"evidence"`
	Confidence float64                `json:"confidence"`
	Reasoning  string                 `json:"reasoning"`
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

// ============================================================================
// THREAT PATTERNS
// ============================================================================

type ThreatPattern struct {
	Name        string
	Severity    string
	Confidence  float64
	Detector    func([]BehaviorIR) []Detection
	Effect      string
	ReversalTTL time.Duration
}

type Detection struct {
	Target     string
	Evidence   []string
	Confidence float64
	Reasoning  string
	Params     map[string]string
}

var ThreatPatterns = []ThreatPattern{
	{
		Name:        "suspicious_cryptominer",
		Severity:    "high",
		Effect:      "kill_process",
		ReversalTTL: 1 * time.Hour,
		Detector: func(behaviors []BehaviorIR) []Detection {
			var detections []Detection
			
			// Look for processes with crypto-mining indicators
			procMap := make(map[string]int)
			var suspiciousProcs []string
			
			for _, b := range behaviors {
				if b.Resource == "process" && b.Action == "exists" {
					procMap[b.Actor]++
					
					name := strings.ToLower(b.Actor)
					if strings.Contains(name, "xmrig") ||
						strings.Contains(name, "minerd") ||
						strings.Contains(name, "cpuminer") ||
						strings.Contains(name, "ethminer") {
						suspiciousProcs = append(suspiciousProcs, b.Actor)
					}
				}
			}
			
			for _, proc := range suspiciousProcs {
				detections = append(detections, Detection{
					Target:     proc,
					Evidence:   []string{fmt.Sprintf("Process name matches mining pattern: %s", proc)},
					Confidence: 0.85,
					Reasoning:  "Process name contains known cryptocurrency mining software identifiers",
					Params:     map[string]string{"process_name": proc},
				})
			}
			
			return detections
		},
	},
	{
		Name:        "port_scan_source",
		Severity:    "medium",
		Effect:      "block_ip",
		ReversalTTL: 24 * time.Hour,
		Detector: func(behaviors []BehaviorIR) []Detection {
			var detections []Detection
			
			// Look for log entries indicating port scanning
			for _, b := range behaviors {
				if b.Resource == "log" && b.Action == "emit" {
					msg := strings.ToLower(b.Target)
					
					if strings.Contains(msg, "port scan") ||
						strings.Contains(msg, "portscan") ||
						(strings.Contains(msg, "connection") && strings.Contains(msg, "refused")) {
						
						// Try to extract IP from log message
						parts := strings.Fields(b.Target)
						for _, part := range parts {
							if strings.Count(part, ".") == 3 {
								detections = append(detections, Detection{
									Target:     part,
									Evidence:   []string{fmt.Sprintf("Log entry: %s", b.Target)},
									Confidence: 0.70,
									Reasoning:  "System logs indicate potential port scanning activity from this source",
									Params:     map[string]string{"ip": part, "log_source": b.Source},
								})
								break
							}
						}
					}
				}
			}
			
			return detections
		},
	},
	{
		Name:        "suspicious_shell_process",
		Severity:    "high",
		Effect:      "kill_process",
		ReversalTTL: 30 * time.Minute,
		Detector: func(behaviors []BehaviorIR) []Detection {
			var detections []Detection
			
			for _, b := range behaviors {
				if b.Resource == "process" && b.Action == "exists" {
					name := strings.ToLower(b.Actor)
					
					// Look for reverse shells or suspicious shell spawns
					if strings.Contains(name, "nc") && (strings.Contains(name, "-e") || strings.Contains(name, "-c")) ||
						strings.Contains(name, "/dev/tcp") ||
						strings.Contains(name, "bash -i") ||
						strings.Contains(name, "sh -i") {
						
						detections = append(detections, Detection{
							Target:     b.Actor,
							Evidence:   []string{fmt.Sprintf("Suspicious shell command pattern: %s", b.Actor)},
							Confidence: 0.80,
							Reasoning:  "Process exhibits characteristics of reverse shell or interactive backdoor",
							Params:     map[string]string{"process_name": b.Actor},
						})
					}
				}
			}
			
			return detections
		},
	},
	{
		Name:        "malicious_file_detected",
		Severity:    "critical",
		Effect:      "quarantine_file",
		ReversalTTL: 7 * 24 * time.Hour,
		Detector: func(behaviors []BehaviorIR) []Detection {
			var detections []Detection
			
			for _, b := range behaviors {
				if b.Resource == "log" && b.Action == "emit" {
					msg := strings.ToLower(b.Target)
					
					if strings.Contains(msg, "malware") ||
						strings.Contains(msg, "virus") ||
						strings.Contains(msg, "trojan") {
						
						// Try to extract file path
						parts := strings.Fields(b.Target)
						for _, part := range parts {
							if strings.HasPrefix(part, "/") && strings.Contains(part, ".") {
								detections = append(detections, Detection{
									Target:     part,
									Evidence:   []string{fmt.Sprintf("Security alert: %s", b.Target)},
									Confidence: 0.90,
									Reasoning:  "File flagged by system security monitoring as potential malware",
									Params:     map[string]string{"file_path": part},
								})
								break
							}
						}
					}
				}
			}
			
			return detections
		},
	},
}

// ============================================================================
// CAPABILITY TOKEN GENERATION
// ============================================================================

var signingKey = []byte("akasha-analyzer-v1-secret-key-change-in-production")

func generateCapabilityToken(effect string, scope string) CapabilityToken {
	nonce := make([]byte, 16)
	rand.Read(nonce)
	nonceHex := hex.EncodeToString(nonce)
	
	token := CapabilityToken{
		Allows: []string{effect},
		Scope:  scope,
		Issuer: "akasha-analyzer",
		Nonce:  nonceHex,
	}
	
	// Create signature
	data := fmt.Sprintf("%s:%s:%s:%s", 
		strings.Join(token.Allows, ","),
		token.Scope,
		token.Issuer,
		token.Nonce,
	)
	
	h := hmac.New(sha256.New, signingKey)
	h.Write([]byte(data))
	token.Signature = hex.EncodeToString(h.Sum(nil))
	
	return token
}

// ============================================================================
// ANALYSIS ENGINE
// ============================================================================

type AnalysisResult struct {
	Actions  []ActionIR
	Summary  string
	Analyzed int
	Detected int
}

func analyzeWindow(behaviors []BehaviorIR) AnalysisResult {
	var actions []ActionIR
	detectedCount := 0
	
	for _, pattern := range ThreatPatterns {
		detections := pattern.Detector(behaviors)
		
		for _, detection := range detections {
			detectedCount++
			
			actionID := fmt.Sprintf("action-%s-%d", pattern.Name, time.Now().Unix())
			
			action := ActionIR{
				ID:         actionID,
				Effect:     pattern.Effect,
				Target:     detection.Target,
				Params:     detection.Params,
				IssuedAt:   time.Now().UTC(),
				ExpiresAt:  time.Now().UTC().Add(5 * time.Minute),
				Evidence:   detection.Evidence,
				Confidence: detection.Confidence,
				Reasoning:  detection.Reasoning,
				Capability: generateCapabilityToken(pattern.Effect, "local"),
			}
			
			// Add reversal plan
			action.Reversal = &ReversalPlan{
				UndoEffect: reverseEffect(pattern.Effect),
				Target:     detection.Target,
				Deadline:   time.Now().UTC().Add(pattern.ReversalTTL),
				Params:     detection.Params,
			}
			
			actions = append(actions, action)
		}
	}
	
	summary := fmt.Sprintf("Analyzed %d behaviors, detected %d threats, generated %d actions",
		len(behaviors), detectedCount, len(actions))
	
	return AnalysisResult{
		Actions:  actions,
		Summary:  summary,
		Analyzed: len(behaviors),
		Detected: detectedCount,
	}
}

func reverseEffect(effect string) string {
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

// ============================================================================
// FILE I/O
// ============================================================================

func readBehaviorLog(path string) ([]BehaviorIR, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	
	lines := strings.Split(string(data), "\n")
	var behaviors []BehaviorIR
	
	for _, line := range lines {
		if strings.TrimSpace(line) == "" {
			continue
		}
		
		var b BehaviorIR
		if err := json.Unmarshal([]byte(line), &b); err != nil {
			continue
		}
		behaviors = append(behaviors, b)
	}
	
	return behaviors, nil
}

func writeActionLog(path string, actions []ActionIR) error {
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		return err
	}
	
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
	if err != nil {
		return err
	}
	defer f.Close()
	
	enc := json.NewEncoder(f)
	for _, action := range actions {
		if err := enc.Encode(action); err != nil {
			return err
		}
	}
	
	return nil
}

func writeAnalysisLog(path string, result AnalysisResult) error {
	if err := os.MkdirAll(filepath.Dir(path), 0700); err != nil {
		return err
	}
	
	f, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
	if err != nil {
		return err
	}
	defer f.Close()
	
	entry := map[string]interface{}{
		"timestamp": time.Now().UTC(),
		"summary":   result.Summary,
		"analyzed":  result.Analyzed,
		"detected":  result.Detected,
		"actions":   len(result.Actions),
	}
	
	enc := json.NewEncoder(f)
	return enc.Encode(entry)
}

// ============================================================================
// MAIN
// ============================================================================

func main() {
	home, err := os.UserHomeDir()
	if err != nil {
		log.Fatal(err)
	}
	
	baseDir := filepath.Join(home, ".local", "share", "akasha")
	behaviorLog := filepath.Join(baseDir, "behavior_ir.log")
	actionLog := filepath.Join(baseDir, "action_ir.log")
	analysisLog := filepath.Join(baseDir, "analysis.log")
	
	log.Println("Akasha Analyzer v1.0 started")
	log.Printf("Reading behaviors from: %s", behaviorLog)
	log.Printf("Writing actions to: %s", actionLog)
	log.Printf("Analysis log: %s", analysisLog)
	log.Printf("Loaded %d threat patterns", len(ThreatPatterns))
	
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()
	
	for {
		<-ticker.C
		
		// Read all behaviors from the last analysis window
		behaviors, err := readBehaviorLog(behaviorLog)
		if err != nil {
			log.Printf("Error reading behavior log: %v", err)
			continue
		}
		
		if len(behaviors) == 0 {
			log.Println("No behaviors to analyze")
			continue
		}
		
		// Filter to recent behaviors (last 5 minutes)
		cutoff := time.Now().UTC().Add(-5 * time.Minute)
		var recentBehaviors []BehaviorIR
		for _, b := range behaviors {
			if b.Timestamp.After(cutoff) {
				recentBehaviors = append(recentBehaviors, b)
			}
		}
		
		log.Printf("Analyzing %d recent behaviors (last 5 min)", len(recentBehaviors))
		
		// Run analysis
		result := analyzeWindow(recentBehaviors)
		
		log.Println(result.Summary)
		
		// Write actions
		if len(result.Actions) > 0 {
			if err := writeActionLog(actionLog, result.Actions); err != nil {
				log.Printf("Error writing actions: %v", err)
			} else {
				log.Printf("Generated %d actions", len(result.Actions))
				for _, action := range result.Actions {
					log.Printf("  → %s: %s on %s (confidence: %.2f)",
						action.ID, action.Effect, action.Target, action.Confidence)
				}
			}
		}
		
		// Write analysis summary
		if err := writeAnalysisLog(analysisLog, result); err != nil {
			log.Printf("Error writing analysis log: %v", err)
		}
	}
}