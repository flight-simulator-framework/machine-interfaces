# ESRF consoles – new installation

## A. Install

The commands below:

1. Create the workspace directory if it does not exist and enter it.
2. Clone `machine-interfaces`, initially checking out only files at the repository root.
3. Check out `backends/esrf`, including the deployment script.
4. Run the deployment script, which:
   - Checks that the selected Python version is 3.11 or newer.
   - Clones the application repositories.
   - Configures sparse checkout to exclude paths regarding other machines .
   - Creates or reuses a shared virtual environment.
   - Installs the local packages in editable mode, including the ESRF backend, and their required dependencies.
   - Checks the required imports, including Tango and RFTrack.
   - Creates executable launchers such as `SysID_GUI.sh`. Each launcher enters the application directory and starts the GUI using the shared virtual environment.

Run these commands on the ESRF control computer:

```
mkdir -p ~/flight-simulator-repositories && cd ~/flight-simulator-repositories
git clone --filter=blob:none --sparse https://gitlab.cern.ch/flight-simulator/machine-interfaces.git
git -C machine-interfaces sparse-checkout add backends/esrf
bash machine-interfaces/backends/esrf/deploy_esrf.sh
```

Python >= 3.11 is taken from `python3`; for another one run
`PYTHON=/path/to/python3.11 bash machine-interfaces/backends/esrf/deploy_esrf.sh`.

## B. Test the GUIs

From `~/flight-simulator-repositories` (or with the full path from anywhere):

```
./SysID_GUI.sh
./ComputeResponseMatrix_GUI.sh
./BBA_GUI.sh
./BumpsApplication_GUI.sh
./Emittance_Measurement_GUI.sh
```

QM and other variants: `./SysID_QM_GUI.sh`, `./BBA_QM_GUI.sh`, `./ComputeResponseMatrix_QM_GUI.sh`, ...
The real machine needs the Tango environment (`TANGO_HOST`) of the console.

## C. Updating later

```
cd ~/flight-simulator-repositories && for r in */.git; do git -C "$(dirname $r)" pull --ff-only; done
```
If the dependencies changed, run `bash machine-interfaces/backends/esrf/deploy_esrf.sh` again afterwards.
