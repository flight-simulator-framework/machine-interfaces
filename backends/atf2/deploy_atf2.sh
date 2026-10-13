#!/bin/bash
set -e
cd "$(dirname "$(readlink -f "$0")")/../../.."
PY=$(readlink -f "$(command -v "${PYTHON:-python3}")")
"$PY" -c 'import sys; sys.exit(sys.version_info < (3, 11))' || { echo "Python >= 3.11 needed: PYTHON=/path/to/python3.11 bash $0"; exit 1; }

P=('/*' '!*clear*' '!*CLEAR*' '!*facet2*' '!*FACET2*' '!*esrf*' '!*ESRF*')
for r in machine-interfaces response-matrix system-identification orbit-bump beam-based-alignment emittance-measurement atf2-knobs; do
    [ -d $r ] || git clone --filter=blob:none --sparse https://github.com/flight-simulator-framework/$r.git
    git -C $r sparse-checkout set --no-cone "${P[@]}"
done

[ -d venv ] || "$PY" -m venv venv
source venv/bin/activate
pip install -U pip
pip install -e machine-interfaces -e machine-interfaces/backends/atf2 -e response-matrix \
    -e system-identification -e orbit-bump -e beam-based-alignment -e emittance-measurement -e atf2-knobs
python -c "import epics, cpymad, RF_Track, machine_interfaces_atf2; print('OK')"
make -C machine-interfaces/backends/atf2/machine_interfaces_atf2/libmagnet libmagnet.so CFLAG=-fPIC \
    || echo "WARNING: libmagnet.so not built (needs gcc and gfortran), magnet K/I conversion is unavailable."

for f in */*_GUI.py atf2-knobs/Knobs/GUIs/*_GUI.py; do
    s=$(basename "$f" .py).sh
    cat > "$s" <<EOF
#!/bin/bash
cd "$PWD/${f%%/*}"
exec "$PWD/venv/bin/python" "${f#*/}"
EOF
    chmod +x "$s"
done
echo "Done: $PWD"
