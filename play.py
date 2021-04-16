#!/usr/bin/env python
import os, subprocess, time, sys

cmd = None
did_insmod,didsu = False,False
fname = ""
file = None
type = None
_test = ""
DEBUG = os.environ.get("DEBUG")!=None or False
fastlen = 8

def okex():
    print("OK, quitting...")
    exit()

def myHelp():
    print("== CSV beeper player (midi derivative) ==")
    print("  Usage:")
    print("play.py [options] file1 ... file2 ...")
    print()
    print("Supports currently csv only.")
    print(" >  note, length, delay (MIDI + millis)")
    print(" >  a   , b     , c")
    print()
    print("Options:")
    print("   -h -help         Show this help.")
    print("   -fast            Play all notes quickly.")
    print("   -nod             No delay between notes.")
    print("   -x speed         Play at speed x.")
    print("   -c -cmd cmd  Other command (beep compatible).")
    print("   -pwd             Use \"pwm\" to make it \"quieter\".")
    print("   -nsqd            Match file times, not based on sqrt, uneven length.")
    print("   -beep            Enforce beep command (default).")
    print("   -setterm         Enforce setterm (console) command.")
    print("   -xset            Enforce xset (graphical terminal) command.")
    print("   -skip percent    Skip percent into the song.")
    print("   ^C (playback)    Twice to quit, after 1.5% of the song to skip.")

for arg in ["-h", "--help", "-help"]:
    if arg in sys.argv:
        myHelp()
        exit()

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

fast = "-fast" in sys.argv
if fast:
    sqd = False
    sys.argv.remove("-fast")

usepwm = "-pwm" in sys.argv
if usepwm:
    sys.argv.remove("-pwm")

if "-beep" in sys.argv:
    sys.argv.remove("-beep")
    cmd = "beep"

if "-xset" in sys.argv:
    sys.argv.remove("-xset")
    cmd = "xset"

if "-setterm" in sys.argv:
    sys.argv.remove("-setterm")
    cmd = "setterm"

skip=0
if "-skip" in sys.argv:
    sys.argv.remove("-skip")
    skip = float(sys.argv.pop(n))/100

if sys.argv[1:] == []:
    myHelp()
    exit()
    
def FPE(string):
    print("FilePlaybackError: "+string)
#class FilePlaybackError(BaseException):
#    pass
class SystemError(BaseException):
    pass
commands=["beep","setterm","xset"]
if cmd == None:
    for c in commands:
        _test = subprocess.getoutput(c+" -l 0")
        if c == "setterm": _test = subprocess.getoutput(c+" --blength 0")
        elif c == "xset": _test = subprocess.getoutput(c+" b 0")
        else: _test = subprocess.getoutput(c+" -l 0")
        if _test.find("not")<0 and (_test.find("device")>0 or _test.find("display")>0):
            cmd=c
            break
    if not cmd: cmd="beep"
if DEBUG: print(f"cmd = {cmd}")
setterm=cmd==commands[1]
if (input("pcspkr is really annoying, are you sure? (y/N) ").strip().lower()+" ")[0] == "y":
    if not "pcspkr" in subprocess.getoutput("lsmod"):
        if (input("We need sudo for modprobe (pcspkr) (y/N) ").strip().lower()+" ")[0] == "y":
            subprocess.run(("sudo","modprobe","pcspkr"))
            if "pcspkr" in subprocess.getoutput("lsmod"):
                did_insmod,didsu = True,True
                print("pcspkr will be disabled later.")
            else: okex()
        else: okex()
else: okex()
if not cmd:
    raise SystemError("No supported command ("+",".join(commands)+")")
cancel_counter = 0 # allow skip a song but also kill
for a in sys.argv[1:]:
    a=os.path.realpath(a)
    if a != os.path.realpath(__file__) and os.path.isfile(a):
        fname=a
        print("" if DEBUG else "\r" + fname.split("/")[-1].ljust(80))
        type = fname.split(".")[-1]
        if type in ["csv"]:
            file = open(fname,"r")
        else:
            continue
        if DEBUG: print(type)
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
                    n = 100/len(lines)
                    lastpercent = -2
                    i = int(skip*len(lines))
                    startedi = i
                    for line in lines[int(skip*len(lines)):]:
                        i+=1
                        if (i - startedi) == int(len(lines)*0.015):
                            cancel_counter -= 1
                        if lastpercent != int(i*10*n+0.5):
                            lastpercent = int(i*10*n+0.5)
                            print("Playing... |"+("="*int((lastpercent/20)-1)+">").ljust(50)+"|",
                              str(lastpercent/10).rjust(5)+"%",end="\r",flush=True)
                        line = [int(float(l.strip() or 0)) for l in line.split(",")]
                        if len(line)==3:
                            note, length, delay = line[idnote], line[idlength], line[idnote]
                            note = max(1,min(note,127))
                            length = max(11,min(length,1000))
                            delay = max(3,delay)
                            if sqd:
                                length, delay = 10*(length**0.5), 10*(delay**0.5)
                            note = str(round(2**((note-69)/12)*440))
                            playlen = str(fastlen) if fast or usepwm else str(round(length/x2))
                            if nodelay: delay=0
                            if cmd=="setterm":
                                subprocess.run(( cmd,"--bfreq", note, "--blength", playlen, ))
                            elif cmd=="xset":
                                subprocess.run(( cmd,"b", "30", note, playlen, ))
                            else:
                                subprocess.run(( cmd, "-f", note, "-l", playlen,
                                  "-d" if length+delay else "",
                                  str(fastlen if fast else playlen) if length+delay else "",
                                  ))
                            if cmd in ["setterm","xset"]:
                                print(end="\a",flush=True)
                            if length+delay and cmd in ["setterm","xset"]:
                                time.sleep(fastlen/1000 if fast else (length/1000+delay/1000)/x2)
                elif type in ["mid","midi"]:
                    FPE("Midi not supported")
                elif not type:
                    FPE("No type for '"+fname+"'")
                else:
                    FPE("Unsupported type: "+str(type))
            except:
                file.close()
                cancel_counter+=1
                if cancel_counter > 1:
                    raise
                continue
            file.close()
    else:
        FPE("No file: "+fname)
if c == "setterm": subprocess.run((cmd, "--bfreq", "400", "--blength", "0"))
elif c == "xset": subprocess.run((cmd, "b", "0", "400", "0"))
