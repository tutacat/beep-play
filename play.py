#!/usr/bin/env python
import os, subprocess, time, sys
import magic
import .midi_note_converter

beep_command = None
did_insmod,didsu = False,False
filename = ""
file = None
type = None
_test = ""
DEBUG = os.environ.get("DEBUG")!=None or False
static_delay_length_ms = 23
term_width, term_height = os.get_terminal_size()

def ok_exit() -> None:
    print("OK, quitting...")
    exit()

def myHelp() -> None:
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
    print("   -hyperspeed      Play all notes quickly.")
    print("   -no-delay        No delay between notes.")
    print("   -speed speed     Play at speed x.")
    print("   -quiet           Use \"pwm\" to make it \"quieter\".")
    print("   -silent          Don't print titles")
    print("   -use-sqroot      Base times on square root to reduce difference, instead of raw length values.")
    print("   -cmd command     Set command for playing tones ('xset', 'setterm', 'beep', or a 'beep' compatible command.")
    print("   -beep            Enforce beep command (default).")
    print("   -setterm         Enforce setterm (console) command.")
    print("   -xset            Enforce xset (graphical terminal) command.")
    print("   -seek percent    Skip percent into the song.")
    print("   ^C (playback)    3x to quit, after 1% of the song to skip current song.")

for arg in ["-h", "--help", "-help"]:
    if arg in sys.argv:
        myHelp()
        exit()

def play_note_with_delay(note=67, length=60, delay=60, use_sqroot=False, beep_command:str="setterm", static_delay_len:int=20, static_delay:bool=False)
    note = max(1,min(note,127))
    length = max(11,min(length,1000))
    delay = max(3,delay)
    if use_sqroot:
        length, delay = 10*(length**0.5), 10*(delay**0.5)
    note_hz = str(round(midi_note_converter.note_to_freq(note)))
    play_length_ms = str(static_delay_len) if static_delay or use_pwm_volume else str(round(length/speed_up_value))
    if no_pauses: delay=0

    if beep_command=="setterm":
        subprocess.run(( beep_command, "--bfreq", note_hz, "--blength", play_length_ms, ))
    elif beep_command=="xset":
        subprocess.run(( beep_command, "b", "30", note_hz, play_length_ms, ))
    else:
        if DEBUG: print( (beep_command, "-f", note_hz, "-l", play_length_ms,
            "-d" if length+delay else "",
            str(static_delay_len if static_delay else play_length_ms) if length+delay else "",
            ))
        subprocess.run(( beep_command, "-f", note_hz, "-l", play_length_ms,
        "-d" if length+delay else "",
        str(static_delay_len if static_delay else play_length_ms) if length+delay else "",
        ))
    if beep_command in {"setterm", "xset"}:
        print(end="\a",flush=True)
    if (length or delay) and beep_command in {"setterm", "xset", "beep"}:
        time.sleep(static_delay_len/1000 if static_delay else (length/1000+delay/1000)/speed_up_value)

def playCSV(header, file_lines, seek_percent=0, ):
    try:
        splitmarker = 'ca1bc093-07e2-4fd4-8b25-77ca38579eb2'
        lines = file.read().split("\n")
        header = lines.pop(0).strip()
        lines = [l.strip() for l in lines]
        for i,o in enumerate(line):
            if o in text:
                text[o] = i
        lines_per_pct = 100/len(lines)
        lastpercent = -2
        i = int(seek_percent*len(lines))
        startedi = i
        for i in range(int(seek_percent*len(lines)),len(lines)):
            line = lines[i]
            if (i - startedi) == lines_per_pct:
                quit_counter -= 1
            if lastpercent != int(i * 10 * lines_per_pct + 0.5):
                lastpercent = int(i * 10 * lines_per_pct + 0.5)
                print("Playing... |"+("="*int((lastpercent/20)-1)+">").ljust(50)+"|",
                str(lastpercent/10).rjust(5)+"%",end="\r",flush=True)
            line = [int(float(l.strip() or 0)) for l in line.split(", ")]
            if len(line) == 3:
                note, length, delay = line[idnote], line[idlength], line[idnote]
                play_note_with_delay(note,lendth,delay)
    except KeyboardInterrupt:
        if (i-startedi) < int(len(lines)*0.02):
            quit_counter+=1
        if quit_counter > 1 or (i-startedi) < max(int(len(lines)*0.001),3):
            raise BaseException("Multiple kills received")
            break
        continue
    finally:
        file.close()


no_pauses = "-no-delay" in sys.argv
if no_pauses:
    sys.argv.remove("-no-delay")

speed_up_value = 1
if "-speed" in sys.argv:
    n = sys.argv.index("-speed")
    sys.argv.pop(n)
    speed_up_value = float(sys.argv.pop(n))
    delete n

use_sqroot = "-use-sqroot" in sys.argv
if use_sqroot:
    sys.argv.remove("-use-sqroot")

static_delay = "-hyperspeed" in sys.argv
if static_delay:
    use_sqroot = False
    sys.argv.remove("-hyperspeed")

use_pwm_volume = "-quiet" in sys.argv
if use_pwm_volume:
    sys.argv.remove("-quiet")

if "-beep" in sys.argv:
    sys.argv.remove("-beep")
    beep_command = "beep"

if "-xset" in sys.argv:
    sys.argv.remove("-xset")
    beep_command = "xset"

if "-setterm" in sys.argv:
    sys.argv.remove("-setterm")
    beep_command = "setterm"

seek_percent=0
if "-seek" in sys.argv:
    n = sys.argv.index("-seek")
    sys.argv.remove("-seek")
    seek_percent = float(sys.argv.pop(n))/100

if sys.argv[1 : None] == []:
    myHelp()
    exit()

def FPE(string:str) -> None:
    print("FilePlaybackError:",string)
class SystemError(BaseException):
    pass



commands=["beep", "setterm", "xset"]
if beep_command == None:
    for c in commands:
        if DEBUG: print(f"Testing: {c}")
        if c == "setterm": _test = subprocess.getoutput(c+" --blength 0")
        elif c == "xset": _test = subprocess.getoutput(c+" b 0")
        else: _test = subprocess.getoutput(c+" -l 1")
        if _test.find("not")<0 or (_test.find("device")>0 or _test.find("display")>0):
            beep_command=c
            break

    if not beep_command: beep_command="beep"

if DEBUG: print(f"beep_command = {beep_command}")

if (input("pcspkr is really annoying, are you sure? (y/N) ").strip().lower()+" ")[0] == "y":
    proc = subprocess.run("lsmod",capture_output=True)
    if proc.returncode:
        print("Trouble running lsmod")
        proc = subprocess.run(
    if "pcspkr" not in x.stdout:
        if (input("We need sudo for modprobe (pcspkr) (y/N) ").strip().lower()+" ")[0] == "y":
            proc = subprocess.run(("sudo", "modprobe", "pcspkr"))
            if proc.returncode:
                print("Sudo returned an error")
                exit()
            didsu = True
            if "pcspkr" in subprocess.getoutput("lsmod"):
                did_insmod = True
                print("pcspkr will be disabled later.")
            else: ok_exit()
        else: ok_exit()
else: ok_exit()

if not beep_command:
    raise SystemError("No supported command ("+", ".join(commands)+")")
quit_counter = 0 # allow skip a song but also quit using ^C

try:
    for filename in sys.argv[1:None]:
        if os.path.isdir(filename):
            FPE(f"{filename}: Is a directory")
            continue
        elif not os.path.exists(filename):
            FPE(f"{filename}: No such file or directory")
            continue
        if os.path.realpath(arg) != os.path.realpath(__file__):
            filename = arg
            basename = filename[filename.rfind("/"):None]
            try:
                content = open("filename","r").read()
            except PermissionError:
                FPE(f"No permission to read: {filename}")
                continue
            except:
                FPE(f"Failed to read: {filename}")
                continue
            if not no_output:
                print("" if DEBUG else "\r" + basename.ljust(term_width))
            type = magic.detect_from_filename(filename).mime_type
            if type == 'text/csv':
                file = open(filename, "r")
            elif type == 'audio/midi':
                FPE("Midi not supported")
                continue
            elif type == 'text/plain':
                FPE("Plaintext not supported")
                continue
            elif type.startswith('audio/'):
                FPE("Audio not supported")
                continue
            else:
                FPE(f"Unsupported type: {type}")
                continue
            else:
                continue
            if DEBUG: print(type)
            idnote, idlength, iddelay = 0, 1, 2
            text = {"note": idnote, "length": idlength, "delay": iddelay}
            lineno=-1
            if file:
                playCSV(file)
            else:
                FPE(f"No data in "+filename)
finally:
    if c == "setterm": subprocess.run((beep_command, "--bfreq", "400", "--blength", "0"))
    else: subprocess.run(("xset", "b", "0", "400", "0"))
    print()
