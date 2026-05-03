// internal/sentinel/sentinel.go — Gatekeeper Sentinel
// Multi-source system observer: osquery, Falco, Suricata, basic procfs fallback.
// Emits Observations to observations.log (append-only JSONL).
// NO enforcement. NO side effects. Read-only surface.
//
// Axiom 2 (Discoverability): gaps in tool coverage are surfaced as named warnings.
// Axiom 7 (Transparency): every observation is attributed to its source.

package sentinel

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"

	"akasha-gatekeeper/internal/ir"
)

type Sentinel struct {
	observationLog  string
	hostname        string
	osqueryEnabled  bool
	falcoEnabled    bool
	suricataEnabled bool
}

func New(logPath string, osquery, falco, suricata bool) *Sentinel {
	hostname, _ := os.Hostname()
	return &Sentinel{
		observationLog:  logPath,
		hostname:        hostname,
		osqueryEnabled:  osquery,
		falcoEnabled:    falco,
		suricataEnabled: suricata,
	}
}

func (s *Sentinel) Run() error {
	log.Println("Gatekeeper Sentinel started")

	errChan := make(chan error, 4)

	if s.osqueryEnabled {
		if toolAvailable("osqueryi") {
			go func() { errChan <- s.monitorOsquery() }()
		} else {
			log.Println("⚠ osquery not found — skipping osquery monitoring")
		}
	}

	if s.falcoEnabled {
		if toolAvailable("falco") {
			go func() { errChan <- s.monitorFalco() }()
		} else {
			log.Println("⚠ Falco not found — skipping Falco monitoring")
		}
	}

	if s.suricataEnabled {
		if _, err := os.Stat("/var/log/suricata/eve.json"); err == nil {
			go func() { errChan <- s.monitorSuricata() }()
		} else {
			log.Println("⚠ Suricata EVE log not found — skipping Suricata monitoring")
		}
	}

	// Always run basic procfs monitor as fallback
	go func() { errChan <- s.monitorBasic() }()

	return <-errChan
}

// ── osquery ──────────────────────────────────────────────────────────────────

type osqueryProcess struct {
	PID     string `json:"pid"`
	Name    string `json:"name"`
	Path    string `json:"path"`
	Cmdline string `json:"cmdline"`
	UID     string `json:"uid"`
}

func (s *Sentinel) monitorOsquery() error {
	log.Println("📊 Sentinel: osquery monitoring active")
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	seen := make(map[string]bool)

	for range ticker.C {
		cmd := exec.Command("osqueryi", "--json",
			"SELECT pid, name, path, cmdline, uid FROM processes WHERE start_time > (strftime('%s', 'now') - 600)")
		out, err := cmd.Output()
		if err != nil {
			log.Printf("osquery error: %v", err)
			continue
		}

		var procs []osqueryProcess
		if err := json.Unmarshal(out, &procs); err != nil {
			continue
		}
		for _, p := range procs {
			if !seen[p.PID] {
				seen[p.PID] = true
				s.emit(ir.Observation{
					Timestamp: time.Now().UTC(),
					Actor:     p.PID,
					Resource:  "process",
					Action:    "exec",
					Target:    p.Path,
					Scope:     "local",
					Source:    "osquery",
					Metadata:  map[string]string{"name": p.Name, "cmdline": p.Cmdline, "uid": p.UID},
				})
			}
		}

		s.osqueryFiles()
		s.osqueryNetwork()
	}
	return nil
}

func (s *Sentinel) osqueryFiles() {
	cmd := exec.Command("osqueryi", "--json",
		"SELECT path, size, uid, ctime FROM file WHERE directory IN ('/tmp', '/var/tmp', '/dev/shm') AND ctime > (strftime('%s', 'now') - 600)")
	out, err := cmd.Output()
	if err != nil {
		return
	}
	var files []map[string]interface{}
	if err := json.Unmarshal(out, &files); err != nil {
		return
	}
	for _, f := range files {
		s.emit(ir.Observation{
			Timestamp: time.Now().UTC(),
			Actor:     fmt.Sprintf("%v", f["uid"]),
			Resource:  "file",
			Action:    "created",
			Target:    fmt.Sprintf("%v", f["path"]),
			Scope:     "local",
			Source:    "osquery",
			Metadata:  map[string]string{"size": fmt.Sprintf("%v", f["size"]), "ctime": fmt.Sprintf("%v", f["ctime"])},
		})
	}
}

func (s *Sentinel) osqueryNetwork() {
	cmd := exec.Command("osqueryi", "--json",
		"SELECT pid, remote_address, remote_port, state FROM process_open_sockets WHERE remote_address != '' AND remote_address NOT LIKE '127.%'")
	out, err := cmd.Output()
	if err != nil {
		return
	}
	var conns []map[string]interface{}
	if err := json.Unmarshal(out, &conns); err != nil {
		return
	}
	for _, c := range conns {
		s.emit(ir.Observation{
			Timestamp: time.Now().UTC(),
			Actor:     fmt.Sprintf("%v", c["pid"]),
			Resource:  "network",
			Action:    "connect",
			Target:    fmt.Sprintf("%v:%v", c["remote_address"], c["remote_port"]),
			Scope:     "local",
			Source:    "osquery",
			Metadata:  map[string]string{"state": fmt.Sprintf("%v", c["state"])},
		})
	}
}

// ── Falco ────────────────────────────────────────────────────────────────────

type falcoAlert struct {
	Time     time.Time         `json:"time"`
	Rule     string            `json:"rule"`
	Output   string            `json:"output"`
	Priority string            `json:"priority"`
	Fields   map[string]string `json:"output_fields"`
}

func (s *Sentinel) monitorFalco() error {
	log.Println("🛡 Sentinel: Falco monitoring active")
	cmd := exec.Command("tail", "-f", "-n", "0", "/var/log/falco/events.json")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	if err := cmd.Start(); err != nil {
		return err
	}
	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		var a falcoAlert
		if err := json.Unmarshal(scanner.Bytes(), &a); err != nil {
			continue
		}
		s.emit(ir.Observation{
			Timestamp: a.Time,
			Actor:     a.Fields["proc.name"],
			Resource:  "syscall",
			Action:    a.Rule,
			Target:    a.Output,
			Scope:     "local",
			Source:    "falco",
			Metadata:  map[string]string{"priority": a.Priority, "container": a.Fields["container.id"], "user": a.Fields["user.name"]},
		})
	}
	return cmd.Wait()
}

// ── Suricata ─────────────────────────────────────────────────────────────────

func (s *Sentinel) monitorSuricata() error {
	log.Println("🌐 Sentinel: Suricata monitoring active")
	cmd := exec.Command("tail", "-f", "-n", "0", "/var/log/suricata/eve.json")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	if err := cmd.Start(); err != nil {
		return err
	}
	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		var event map[string]interface{}
		if err := json.Unmarshal(scanner.Bytes(), &event); err != nil {
			continue
		}
		if event["event_type"] != "alert" {
			continue
		}
		alert := event["alert"].(map[string]interface{})
		s.emit(ir.Observation{
			Timestamp: time.Now().UTC(),
			Actor:     fmt.Sprintf("%v", event["src_ip"]),
			Resource:  "network",
			Action:    "alert",
			Target:    fmt.Sprintf("%v:%v", event["dest_ip"], event["dest_port"]),
			Scope:     "local",
			Source:    "suricata",
			Metadata: map[string]string{
				"signature": fmt.Sprintf("%v", alert["signature"]),
				"category":  fmt.Sprintf("%v", alert["category"]),
				"proto":     fmt.Sprintf("%v", event["proto"]),
			},
		})
	}
	return cmd.Wait()
}

// ── Basic procfs fallback ─────────────────────────────────────────────────────

func (s *Sentinel) monitorBasic() error {
	log.Println("👁 Sentinel: basic procfs monitoring active (fallback)")
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()
	seen := make(map[string]bool)

	for range ticker.C {
		out, err := exec.Command("ps", "aux").Output()
		if err != nil {
			continue
		}
		for _, line := range strings.Split(string(out), "\n")[1:] {
			fields := strings.Fields(line)
			if len(fields) < 11 {
				continue
			}
			pid := fields[1]
			if !seen[pid] {
				seen[pid] = true
				s.emit(ir.Observation{
					Timestamp: time.Now().UTC(),
					Actor:     pid,
					Resource:  "process",
					Action:    "exists",
					Target:    strings.Join(fields[10:], " "),
					Scope:     "local",
					Source:    "procfs",
				})
			}
		}
	}
	return nil
}

// ── Emit ─────────────────────────────────────────────────────────────────────

func (s *Sentinel) emit(obs ir.Observation) {
	f, err := os.OpenFile(s.observationLog, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		log.Printf("emit error: %v", err)
		return
	}
	defer f.Close()
	json.NewEncoder(f).Encode(obs)
}

func toolAvailable(name string) bool {
	_, err := exec.LookPath(name)
	return err == nil
}
