
package audit

import (
    "encoding/json"
    "os"
    "sync"
    "time"
)

type Entry struct {
    Time   time.Time
    Action string
    Target string
    Result string
}

var mu sync.Mutex

func Append(path string, e Entry) error {
    mu.Lock()
    defer mu.Unlock()

    f, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
    if err != nil {
        return err
    }
    defer f.Close()

    enc := json.NewEncoder(f)
    return enc.Encode(e)
}
