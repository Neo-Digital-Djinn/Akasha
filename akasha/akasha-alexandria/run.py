"""
Alexandria Temporal Kernel — Entry Point

Usage:
    python run.py --generator <type>
    python run.py --verify-ledger

Generator types:
    manual    Read hypothesis from input.json
    symbolic  Deterministic axiom (self-evident test)
    local     Ollama-compatible local LLM (requires ollama installed)
    api       External API scaffold (implement in api_adapter.py)
    bridge    Generic HTTP bridge (POST to localhost:8080)
"""

import argparse
import yaml

from alexandria.kernel import Kernel
from generators.manual_adapter import ManualAdapter
from generators.local_adapter import LocalAdapter
from generators.api_adapter import APIAdapter
from generators.tasker_bridge_adapter import HTTPBridgeAdapter, TaskerBridgeAdapter
from generators.symbolic_adapter import SymbolicAdapter

GENERATORS = {
    "manual":   ManualAdapter,
    "local":    LocalAdapter,
    "api":      APIAdapter,
    "bridge":   HTTPBridgeAdapter,
    "tasker":   TaskerBridgeAdapter,   # alias for backward compatibility
    "symbolic": SymbolicAdapter,
}


def main():
    parser = argparse.ArgumentParser(description="Alexandria Temporal Kernel")
    parser.add_argument("--generator", type=str, help="Generator type")
    parser.add_argument("--verify-ledger", action="store_true",
                        help="Verify ledger integrity and exit")
    args = parser.parse_args()

    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)

    gen_type = args.generator or config.get("generator", "symbolic")

    kernel = Kernel()

    if args.verify_ledger:
        print(kernel.ledger.verify_integrity())
        return

    if gen_type not in GENERATORS:
        print(f"Unknown generator: {gen_type!r}. Available: {list(GENERATORS)}")
        raise SystemExit(1)

    adapter = GENERATORS[gen_type]()
    hypothesis = adapter.propose()

    result = kernel.evaluate(hypothesis)
    print(result)


if __name__ == "__main__":
    main()
