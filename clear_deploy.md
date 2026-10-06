# CLEAR consoles – new installation

## A. Install


```
cd /clear/data/Python/dev/marlene/flight-simulator-repositories
git -C machine-interfaces pull
git -C machine-interfaces sparse-checkout add backends/clear
bash machine-interfaces/backends/clear/deploy_clear.sh
```

## B. Test the GUIs

From `/clear/data/Python/dev/marlene/flight-simulator-repositories` (or with the full path from anywhere):

```
./SysID_GUI.sh
./ComputeResponseMatrix_GUI.sh
./BBA_GUI.sh
./BumpsApplication_GUI.sh
./Emittance_Measurement_GUI.sh
```

QM and other variants: `./SysID_QM_GUI.sh`, `./BBA_QM_GUI.sh`, `./ComputeResponseMatrix_QM_GUI.sh`, ...

## C. Updating later

```
cd /clear/data/Python/dev/marlene/flight-simulator-repositories && for r in */.git; do git -C "$(dirname $r)" pull --ff-only; done
```
If the dependencies changed, run `bash machine-interfaces/backends/clear/deploy_clear.sh` again afterwards.

