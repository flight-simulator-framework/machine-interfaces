# ATF2 consoles – new installation

## A. Install

The commands below:

1. Create the workspace directory if it does not exist and enter it.
2. Clone `machine-interfaces`, initially checking out only files at the repository root.
3. Check out `backends/atf2`, including the deployment script.
4. Run the deployment script, which:
   - Checks that the selected Python version is 3.11 or newer.
   - Clones the application repositories, including `atf2-knobs`.
   - Configures sparse checkout to exclude paths regarding other machines.
   - Creates or reuses a shared virtual environment.
   - Installs the local packages in editable mode, including the ATF2 backend, and their required dependencies.
   - Checks the required imports.
   - Attempts to build `libmagnet.so` for magnet current–strength conversion. Building it requires GCC, GNU Fortran and Make.
   - Creates executable launchers for the application GUIs and ATF2 tuning tools. Each launcher enters the application directory and starts the GUI using the shared virtual environment.

Run these commands on the ATF2 control computer:

```
mkdir -p ~/flight-simulator-repositories && cd ~/flight-simulator-repositories
git clone --filter=blob:none --sparse https://gitlab.cern.ch/flight-simulator/machine-interfaces.git
git -C machine-interfaces sparse-checkout add backends/atf2
bash machine-interfaces/backends/atf2/deploy_atf2.sh
```

Python >= 3.11 is taken from `python3`; for another one run
`PYTHON=/path/to/python3.11 bash machine-interfaces/backends/atf2/deploy_atf2.sh`.
The magnet K/I conversion library (libmagnet) is built with `gcc` and `gfortran`.

## B. Test the GUIs

From `~/flight-simulator-repositories` (or with the full path from anywhere):

```
./SysID_GUI.sh
./ComputeResponseMatrix_GUI.sh
./BBA_GUI.sh
./BumpsApplication_GUI.sh
./Emittance_Measurement_GUI.sh
./BeamTuning_GUI.sh
./IPBSM_Opt_GUI.sh
./IPBSM_Stability_GUI.sh
./DR_SkewBO_GUI.sh
```

QM and other variants: `./SysID_QM_GUI.sh`, `./BBA_QM_GUI.sh`, `./ComputeResponseMatrix_QM_GUI.sh`, ...
The real machine needs the ATF2 EPICS environment (e.g. `EPICS_CA_ADDR_LIST`) of the console.

## C. Updating later

```
cd ~/flight-simulator-repositories && for r in */.git; do git -C "$(dirname $r)" pull --ff-only; done
```
If the dependencies changed, run `bash machine-interfaces/backends/atf2/deploy_atf2.sh` again afterwards.
