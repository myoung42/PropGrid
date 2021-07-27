# PropGrid
Converts a property grid for input into FRNC-5

Known limitations:
- currently cannot deal with single phase fluids.  Two Phase only.
- .xlsx files only.  other file types not supported

Download and install Python from the Microsoft Store
Download and install Git

To install, copy and paste the following commands in a powershell window, in order:
    cd c:\users\username\documents

    git clone https://github.com/myoung42/PropGrid.git

    cd PropGrid

    python -m pip install venv

    python -m venv .venv

    python -m pip install -r requirements.txt

To Run:
    -Relabel the excel columns per the list in the samplegrid.xlsx
    -If total enthalpy is given, copy it and label for both vapor and liquid enthalpy
    
    enter in powershell window:
    cd c:\users\username\documents\propgrid

    .venv/scripts/activate

    python propgrid.py