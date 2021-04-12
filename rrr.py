#!/usr/bin/env python
import math, random, subprocess, time
sin=math.sin
commands=["/usr/bin/setterm","/usr/bin/xset"]
fname = ""
file = None
type = None
_test = ""
cmd = None
class SystemError(BaseException):
    pass
for c in commands:
    _test = subprocess.getoutput("setterm --blength 256")
    if not _test:
        raise SystemError(c+" error")
    if _test.find("not support")<0 and _test.find("error")<0:
        cmd=c
        break
    else:
        setterm=False
setterm=cmd==commands[0]
if not cmd:
    raise SystemError("No supported command ("+",".join(commands)+")")
i=0
while 1:
    note=sin(i*.1)*9+60
    subprocess.run(( cmd,"--bfreq" if setterm else "b", str(round(2**((note-69)/12)*440)), "--blength" if setterm else "", str(round(100)) ))
    print(end="\a",flush=True)
    time.sleep(0.1)
    i+=1
subprocess.run(( cmd,"--bfreq" if setterm else "b", "400", "--blength" if setterm else "", "200" ))
