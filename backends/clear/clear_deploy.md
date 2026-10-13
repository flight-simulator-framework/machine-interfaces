# CLEAR consoles – new installation

## A. Install

The commands below:

1. Create the workspace directory if it does not exist and enter it.
2. Clone `machine-interfaces`, initially checking out only files at the repository root.
3. Check out `backends/clear`, including the deployment script.
4. Run the deployment script, which:
   - Loads CERN Acc-Py.
   - Checks that the Acc-Py Python version is 3.11 or newer.
   - Clones the application repositories from CERN GitLab.
   - Configures checkout to exclude paths related to other machines.
   - Creates or reuses a shared virtual environment.
   - Configures the Acc-Py package index and installs the local packages in editable mode, including the CLEAR backend.
   - Checks the required imports.
   - Creates executable launchers such as `SysID_GUI.sh`. Each launcher loads Acc-Py, enters the application directory and starts the GUI using the shared virtual environment.

Run these commands on the CLEAR console:

```
mkdir -p /clear/data/Python/dev/marlene/flight-simulator-repositories && cd /clear/data/Python/dev/marlene/flight-simulator-repositories
git clone --filter=blob:none --sparse https://gitlab.cern.ch/flight-simulator/machine-interfaces.git
git -C machine-interfaces sparse-checkout add backends/clear
bash machine-interfaces/backends/clear/deploy_clear.sh
```

CERN GitLab holds mirrors of the [GitHub repositories](https://github.com/flight-simulator-framework), where development, issues and pull requests are hosted.

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

