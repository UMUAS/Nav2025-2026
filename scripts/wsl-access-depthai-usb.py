# ============================== INFORMATION ==============================
# If you cannot access the oak-d camera from WSL2, it is probably because
# WSL2 has no access to the real USB ports on your computer.
#
# To confrim this is the case, you can run `lsusb` in your WSL terminal
# and check whether the Luxonis/Depthai/Myriad X device is listed there.
# 
# If not, follow: https://docs.luxonis.com/software/depthai/manual-install/#Manual%20DepthAI%20installation-Installing%20dependencies-WSL%202
# 
# TLDR: You will probably install and use usbpid version >= 4.0.
# In that case, this script is for you. You will need to run it on your
# windows terminal (not in WSL2).

import time
import subprocess

while True:
    output = subprocess.run('usbipd list', capture_output=True, encoding="UTF-8")
    rows = output.stdout.split('\n')
    for row in rows:
        if ('Movidius MyriadX' in row or 'Luxonis Device' in row) and 'Not shared' in row:
            busid = row.split(' ')[0]
            out = subprocess.run(f'usbipd bind -b {busid}', capture_output=True, encoding="UTF-8")
            print(out.stdout)
            print(f'Usbipd bind Myriad X')
        if ('Movidius MyriadX' in row or 'Luxonis Device' in row) and 'Shared' in row:
            busid = row.split(' ')[0]
            out = subprocess.run(f'usbipd attach -w -b {busid}', capture_output=True, encoding="UTF-8")
            print(out.stdout)
            print(f'Usbipd attached Myriad X on bus {busid}')
    time.sleep(0.5)