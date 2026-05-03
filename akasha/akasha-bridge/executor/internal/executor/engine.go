
package executor

import (
    "akasha-executor/internal/audit"
    "akasha-executor/internal/effects"
    "akasha-executor/internal/ir"
    "akasha-executor/internal/policy"
    "time"
)

func Execute(a ir.ActionIR, auditPath string) error {
    if err := policy.Verify(a); err != nil {
        return err
    }

    var err error

    switch a.Effect {
    case ir.KillProcess:
        err = effects.KillProcess(a.Target)
    case ir.BlockIP:
        err = effects.BlockIP(a.Target)
    case ir.Quarantine:
        err = effects.QuarantineFile(a.Target)
    }

    audit.Append(auditPath, audit.Entry{
        Time:   time.Now(),
        Action: string(a.Effect),
        Target: a.Target,
        Result: result(err),
    })

    return err
}

func result(err error) string {
    if err != nil {
        return err.Error()
    }
    return "success"
}
