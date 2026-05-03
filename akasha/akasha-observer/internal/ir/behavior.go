package ir

import "time"

type Behavior struct {
    Timestamp   time.Time `json:"timestamp"`
    Actor       string    `json:"actor"`
    Resource    string    `json:"resource"`
    Action      string    `json:"action"`
    Target      string    `json:"target"`
    Scope       string    `json:"scope"`
    Persistence bool      `json:"persistence"`
    Source      string    `json:"source"`
}