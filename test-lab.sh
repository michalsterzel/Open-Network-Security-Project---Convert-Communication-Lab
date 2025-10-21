#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Testing lab connectivity: Agent and Detective -> DNS (192.168.10.1)"

run_check() {
  local vm_dir="$1"
  local name="$2"

  echo
  echo "== $name =="
  pushd "$vm_dir" > /dev/null

  echo "IP addresses (internal interface enp0s8):"
  vagrant ssh -c "ip -4 addr show enp0s8 | sed -n 's/.*inet \([0-9.]*\/.*\).*/\1/p' || ip -4 addr show | sed -n 's/.*inet \([0-9.]*\/.*\).*/\1/p'"

  echo "Ping DNS (192.168.10.1):"
  vagrant ssh -c "ping -c 4 192.168.10.1 || true"

  popd > /dev/null
}

run_check "$ROOT_DIR/Agent" "Agent"
run_check "$ROOT_DIR/Detective" "Detective"

echo
echo "Test complete."