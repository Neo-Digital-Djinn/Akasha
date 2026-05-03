package journal

import (
    "bufio"
    "os/exec"
    "strings"
)

type JournalEvent struct {
    Comm string
    Msg  string
}

func ReadOnce() ([]JournalEvent, error) {
    cmd := exec.Command("journalctl", "--user", "-n", "50", "--no-pager")
    out, err := cmd.Output()
    if err != nil {
        return nil, err
    }

    var events []JournalEvent
    scanner := bufio.NewScanner(strings.NewReader(string(out)))

    for scanner.Scan() {
        events = append(events, JournalEvent{
            Comm: "unknown",
            Msg:  scanner.Text(),
        })
    }

    return events, nil
}