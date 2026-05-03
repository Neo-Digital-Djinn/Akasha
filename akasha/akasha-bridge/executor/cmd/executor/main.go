
package main

import (
    "log"
    "akasha-executor/internal/runtime"
)

func main() {
    if err := runtime.Run(); err != nil {
        log.Fatal(err)
    }
}
