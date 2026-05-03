package proc

import (
    "os"
    "strconv"
)

type ProcEntry struct {
    PID  int
    Comm string
}

func Snapshot() ([]ProcEntry, error) {
    entries, err := os.ReadDir("/proc")
    if err != nil {
        return nil, err
    }

    var procs []ProcEntry

    for _, e := range entries {
        if !e.IsDir() {
            continue
        }

        pid, err := strconv.Atoi(e.Name())
        if err != nil {
            continue
        }

        comm, err := os.ReadFile("/proc/" + e.Name() + "/comm")
        if err != nil {
            continue
        }

        procs = append(procs, ProcEntry{
            PID:  pid,
            Comm: string(comm[:len(comm)-1]),
        })
    }

    return procs, nil
}