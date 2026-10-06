# CLEAR consoles – new installation

## A. Install


```
cd /clear/data/Python/dev/marlene/flight-simulator-repositories
git -C machine-interfaces pull
git -C machine-interfaces sparse-checkout add backends/clear
bash machine-interfaces/backends/clear/deploy_clear.sh
```

## B. Test the GUIs

```
/bin/bash run_gui.sh system-identification SysID_GUI.py
/bin/bash run_gui.sh response-matrix ComputeResponseMatrix_GUI.py
/bin/bash run_gui.sh beam-based-alignment BBA_GUI.py
/bin/bash run_gui.sh orbit-bump BumpsApplication_GUI.py
/bin/bash run_gui.sh emittance-measurement Emittance_Measurement_GUI.py
```

## C. Updating later

```
cd /clear/data/Python/dev/marlene/flight-simulator-repositories && for r in */.git; do git -C "$(dirname $r)" pull --ff-only; done
```

If the dependencies changed, run `bash machine-interfaces/backends/clear/deploy_clear.sh` again afterwards.

