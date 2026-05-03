
package policy

import (
    "errors"
    "time"
    "akasha-executor/internal/ir"
)

func Verify(a ir.ActionIR) error {
    if time.Now().After(a.ExpiresAt) {
        return errors.New("action expired")
    }

    allowed := false
    for _, e := range a.Capability.Allows {
        if e == a.Effect {
            allowed = true
            break
        }
    }
    if !allowed {
        return errors.New("capability does not allow effect")
    }

    return nil
}
