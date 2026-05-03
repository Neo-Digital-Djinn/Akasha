package main

import (
    "log"
    "os"
    "path/filepath"
    "time"

    "akasha-observer/internal/ir"
    "akasha-observer/internal/journal"
    "akasha-observer/internal/proc"
    "akasha-observer/internal/storage"
)

func main() {
    home, err := os.UserHomeDir()
    if err != nil {
        log.Fatal(err)
    }

    base := filepath.Join(home, ".local", "share", "akasha")
    writer, err := storage.NewWriter(filepath.Join(base, "behavior_ir.log"))
    if err != nil {
        log.Fatal(err)
    }
    defer writer.Close()

    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for {
        procs, _ := proc.Snapshot()
        for _, p := range procs {
            b := ir.Behavior{
                Timestamp: time.Now().UTC(),
                Actor:     p.Comm,
                Resource:  "process",
                Action:    "exists",
                Scope:     "local",
                Source:    "procfs",
            }
            _ = writer.Write(b)
        }

        events, _ := journal.ReadOnce()
        for _, e := range events {
            b := ir.Behavior{
                Timestamp: time.Now().UTC(),
                Actor:     e.Comm,
                Resource:  "log",
                Action:    "emit",
                Target:    e.Msg,
                Scope:     "local",
                Source:    "journald",
            }
            _ = writer.Write(b)
        }

        <-ticker.C
    }
}