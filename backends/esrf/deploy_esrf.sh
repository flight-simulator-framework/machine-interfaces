#!/bin/bash
set -e
cd "$(dirname "$(readlink -f "$0")")/../../.."
PY=$(readlink -f "$(command -v "${PYTHON:-python3}")")
"$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))' || { echo "Python >= 3.11 needed: PYTHON=/path/to/python3.11 bash $0"; exit 1; }

P=('/*' '!*clear*' '!*CLEAR*' '!*atf2*' '!*ATF2*' '!*facet2*' '!*FACET2*')
for r in machine-interfaces response-matrix system-identification orbit-bump beam-based-alignment emittance-measurement; do
    [ -d $r ] || git clone --filter=blob:none --sparse https://github.com/flight-simulator-framework/$r.git
    git -C $r sparse-checkout set --no-cone "${P[@]}"
done

[ -d venv ] || "$PY" -m venv venv
source venv/bin/activate
pip install -U pip
pip install -e machine-interfaces -e machine-interfaces/backends/esrf -e response-matrix \
    -e system-identification -e orbit-bump -e beam-based-alignment -e emittance-measurement
python -c "import tango, RF_Track, machine_interfaces_esrf; print('OK')"

for f in */*_GUI.py; do
    s=$(basename "$f" .py).sh
    cat > "$s" <<EOF
#!/bin/bash
cd "$PWD/$(dirname "$f")"
exec "$PWD/venv/bin/python" "$(basename "$f")"
EOF
    chmod +x "$s"
done
echo "Done: $PWD"
