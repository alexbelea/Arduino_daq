Code to read 0-5V voltage off the Arduino analogue A0-A4 and output via serial USB to python script.

Outputs .csv and plot

1. Create VENV:                     python -m venv .venv
2. start the venv	 	    source .venv/bin/active or .\.venv\Scripts\active (linux/win)
3. install pip requirements:        pip install -r requirements.txt
4. load the cpp code to Arduino
5. (optional?) close arduino IDE to free up the serial socket
6. run the listener 