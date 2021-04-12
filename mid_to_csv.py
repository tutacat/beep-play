#!/usr/bin/env python
import mido, os, sys
if sys.argv:
    files = sys.argv[1:]
else:
    files=os.listdir()
    print("Choose a file by number")
    if len(files)<1:
        input("No files.\nenter to continue...")
        exit()
    for i,f in enumerate(files):
        print("[%d] %s"%(i,f))
    ans=-1
    while ans<0 or ans>len(files)-1:
        try:
            ans=int(input().strip())
        except:
            ans=-1
        if ans<0 or ans>len(files)-1:
            print("Please enter an integer between 0 and %d"%(len(files)-1))
    files=[files[ans]]
def readl(file):
    for track in file.tracks:
        for e in track:
            if e.type=='note_on':
                yield (e.note,e.time,e.velocity)
for fln in files:
    try:
        fname=fln
        out_csv=open(fln.split("/")[-1].split(".")[0]+'.csv','w')
        print(fln)
        mfile=mido.MidiFile(fname,type=1)
        out_csv.write("note,length,delay\n")
        for m in readl(mfile):
            try:
                if m:
                    out_csv.write("{},{},{}\n".format(m[0],m[1],m[2]))
            except:
                pass
    except:
        pass
    finally:
        out_csv.close()
