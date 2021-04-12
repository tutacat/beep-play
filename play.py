#!/usr/bin/env python
import os, subprocess, time, sys

cmd = None
did_insmod,didsu = False,False

def okex():
    print("OK, quitting...")
    exit()

def myHelp():
    print("== CSV beeper player (midi derivative) ==")
    print("  Usage:")
    print("play.py [options] file1 ... file2 ...")
    print()
    print("Console is faster than graphical term.")
    print()
    print("Supports currently csv.")
    print(" >  note, length, delay (unordered, MIDI + millis)")
    print(" >  a   , b     , c")
    print()
    print("Options:")
    print("   -h -help      Show this help.")
    print("   -fast         Play all notes quickly without delay.")
    print("   -nod          No delay between notes.")
    print("   -x speed      Play at speed x.")
    print("   -nsqd         Base times not sqrt, less even length.")
    print("   -c command    Set bell properties with this command (xset compatible).")
    print("   -xset         Enforce xset (graphical terminal).")
    print("   -setterm      Enforce setterm (console).")
    print("   -skip percent Skip percent into the song.")

if "-h" in sys.argv or "--help" in sys.argv or "-help" in sys.argv:
    myHelp()
    exit()

fast = "-fast" in sys.argv
if fast:
    sys.argv.remove("-fast")

nodelay = "-nod" in sys.argv
if nodelay:
    sys.argv.remove("-nod")

x2 = 1
if "-x" in sys.argv:
    n = sys.argv.index("-x")
    sys.argv.pop(n)
    x2 = float(sys.argv.pop(n))

sqd = not "-nsqd" in sys.argv
if not sqd:
    sys.argv.remove("-nsqd")

if "-c" in sys.argv:
    sys.argv.remove("-c")
    cmd = sys.argv.pop(n)

if "-xset" in sys.argv:
    sys.argv.remove("-xset")
    cmd = "/usr/bin/xset"

if "-setterm" in sys.argv:
    sys.argv.remove("-setterm")
    cmd = "/usr/bin/setterm"

skip=0
if "-skip" in sys.argv:
    sys.argv.remove("-skip")
    skip = float(sys.argv.pop(n))/100

if sys.argv[1:] == []:
    myHelp()
    exit()
    
fname = ""
file = None
type = None
_test = ""
def FPE(string):
    print("FilePlaybackError: "+string)
#class FilePlaybackError(BaseException):
#    pass
class SystemError(BaseException):
    pass
commands=["/usr/bin/setterm","/usr/bin/xset"]
if cmd == None:
    for c in commands:
        _test = subprocess.getoutput(f"{c} {'--blength' if c==commands[0] else 'b'} 10")
        if _test.find("not support")<0 and _test.find("error")<0 or _test.find("display")>0:
            cmd=c
            break
        else:
            setterm=False
setterm=cmd==commands[0]
if setterm:
    if (input("pcspkr is really annoying, are you sure? (y/N)").strip().lower()+" ")[0] == "y":
        if not "pcspkr" in subprocess.getoutput("lsmod"):
            if (input("We need sudo for modprobe (pcspkr) (y/N)").strip().lower()+" ")[0] == "y":
                subprocess.run(("sudo","modprobe","pcspkr"))
                if "pcspkr" in subprocess.getoutput("lsmod"):
                    did_insmod,didsu = True,True
                    print("pcspkr will be disabled later.")
                else: okex()
            else: okex()
    else: okex()
if not cmd:
    raise SystemError("No supported command ("+",".join(commands)+")")
for a in sys.argv[1:]:
    a=os.path.realpath(a)
    if a != os.path.realpath(__file__) and os.path.isfile(a):
        fname=a
        print("\r"+fname.split("/")[-1])
        type = fname.split(".")[-1]
        if type in ["csv"]:
            file = open(fname,"r")
        else:
            continue
        # print(type)
        idnote,idlength,iddelay=0,1,2
        text = {"note":idnote,"length":idlength,"delay":iddelay}
        lineno=-1
        if file:
            try:
                if type == "csv":
                    lines = file.read().split("\n")
                    line = [l.strip() for l in lines.pop(0)]
                    for i,o in enumerate(line):
                        if o in text:
                            text[o] = i
                    line = file.readline().strip()
                    n=100/len(lines)
                    lastpercent=-1
                    i=int(skip*len(lines))
                    lastpercent=int(i*n+0.5)
                    for line in lines[int(skip*len(lines)):]:
                        i+=1
                        if lastpercent != int(i*n+0.5):
                            lastpercent=int(i*n+0.5)
                            print("Playing... |"+("="*int((lastpercent/3)-1)+">").ljust(33)+"|", str(lastpercent).rjust(3)+"%",end="\r",flush=True)
                        line = [int(float(l.strip() or 0)) for l in line.split(",")]
                        if len(line)==3:
                            note, length, delay = line[idnote], line[idlength], line[idnote]
                            note = max(1,min(note,127))
                            length = max(11,min(length,1000))
                            delay = max(3,delay)
                            if sqd:
                                length, delay = 10*(length**0.5), 10*(delay**0.5)
                            note = str(round(2**((note-69)/12)*440))
                            if nodelay: delay=0
                            if setterm: subprocess.run(( cmd,"--bfreq", note, "--blength", str(round(length/x2)) ))
                            else: subprocess.run(( cmd,"b", "30", note, str(round(length/x2)) ))
                            print(end="\a",flush=True)
                            if length+delay:
                                time.sleep(.0666 if fast else (length/1000+delay/1000)/x2)
                elif type in ["mid","midi"]:
                    FPE("Midi not supported")
                elif not type:
                    FPE("No type for '"+fname+"'")
                else:
                    FPE("Unsupported type: "+str(type))
            except:
                file.close()
                continue
            file.close()
    else:
        FPE("No file: "+fname)
if setterm: subprocess.run((cmd, "--bfreq", "400", "--blength", "0"))
else: subprocess.run((cmd, "b", "0", "400", "0"))
if did_insmod:
    if not didsu:
        if (input("We need sudo for rmmod (pcspkr) (y/N)").strip().lower()+" ")[0] == "y":
            didsu = True
    if didsu:
        print("rmmoding pcspkr...")
        subprocess.run(("sudo","rmmod","pcspkr"))
    else:
        print("pcspkr mod is still active.")
        print("run 'sudo rmmod pcspkr' to deactivate it")
