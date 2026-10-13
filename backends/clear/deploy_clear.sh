#!/bin/bash
source /acc/local/share/python/acc-py/base/pro/setup.sh
set -e
cd "$(dirname "$(readlink -f "$0")")/../../.."
PY=$(readlink -f "$(command -v python)")
"$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))' || { echo "Python >= 3.11 needed, Acc-Py provides $("$PY" --version 2>&1)"; exit 1; }

P=('/*' '!*atf2*' '!*ATF2*' '!*facet2*' '!*FACET2*' '!*esrf*' '!*ESRF*')
for r in machine-interfaces response-matrix system-identification orbit-bump beam-based-alignment emittance-measurement; do
    [ -d $r ] || git clone --filter=blob:none --sparse https://gitlab.cern.ch/flight-simulator/$r.git
    git -C $r sparse-checkout set --no-cone "${P[@]}"
done

[ -d venv ] || "$PY" -m venv venv
source venv/bin/activate
pip config --site set global.index-url https://acc-py-repo.cern.ch/repository/vr-py-releases/simple/
pip config --site set global.trusted-host acc-py-repo.cern.ch
pip install -U pip
pip install -e machine-interfaces -e machine-interfaces/backends/clear -e response-matrix \
    -e system-identification -e orbit-bump -e beam-based-alignment -e emittance-measurement
python -c "import pyda, pyda_japc, RF_Track, machine_interfaces_clear; print('OK')"

for f in */*_GUI.py; do
    s=$(basename "$f" .py).sh
    cat > "$s" <<EOF
#!/bin/bash
source /acc/local/share/python/acc-py/base/pro/setup.sh
cd "$PWD/$(dirname "$f")"
exec "$PWD/venv/bin/python" "$(basename "$f")"
EOF
    chmod +x "$s"
done
echo "Done: $PWD"
