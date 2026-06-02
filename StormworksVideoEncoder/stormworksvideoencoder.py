import imageio.v3 as iio
import math
import numpy as np
import os



YUVmatrix = np.dot(1/255,
[
[0.30,  0.5990/0.5957,  0.2130/0.5226],
[0.59, -0.2773/0.5957, -0.5251/0.5226],
[0.11, -0.3217/0.5957,  0.3121/0.5226]
])




def fread(frame: int):
    im = iio.imread(
        location,
        index=math.floor(frame),
        plugin="pyav",
    )
    signal = []
    bl = []
    quads = []
    hdsignal = []
    hdi = []
    hdq = []
    hdcolor = []
    mf = math.floor
    YUV = np.dot(im, YUVmatrix) #convert to YUV
    for p in range(0, height * 24):
        TL=YUV[(p*2)//96*2][(p*2)%96][0]
        TR=YUV[(p*2)//96*2][(p*2+1)%96][0]
        BL=YUV[(p*2)//96*2+1][(p*2)%96][0]
        BR=YUV[(p*2)//96*2+1][(p*2+1)%96][0]
        bl = (TL+TR+BL+BR)/4
        i = YUV[(p*2)//96*2][(p*2)%96][1]
        q = YUV[(p*2)//96*2][(p*2)%96][2]
        if bl == 0:
            lr = 0
            tb = 0
            ch = 0
        else:
            #find brightness distribution inside each square
            lr = (TL-TR+BL-BR)/bl
            tb = (TL+TR-BL-BR)/bl
            ch = (TL-TR-BL+BR)/bl
            
        if lr != 0: #all values gamma corrected
            lr = min(max(mf(lr/(abs(lr)**0.5)*5.5+0.5),-11),11)
        else:
            lr = 0
        
        if tb != 0:
            tb = min(max(mf(tb/(abs(tb)**0.5)*5.5+0.5),-11),11)
        else:
            tb = 0
        
        if ch != 0:
            ch = min(max(mf(ch/(abs(ch)**0.5)*5.5+0.5),-11),11)
        else:
            ch = 0
        
        if abs(i) > 0.01 and abs(i) < 100:
            ipr = mf(min(max((i/abs(i)**0.5)*18+0.5,-18),18))
        else:
            ipr = 0
        
        if abs(q) > 0.01 and abs(q) < 10:
            qpr = mf(min(max((q/abs(q)**0.5)*12+0.5,-12),12))
        else:
            qpr = 0
        ilp = (ipr+1)//3
        qlp = (qpr+1)//3
        sign = lr+tb*23+ch*529+6083 #this is the real encoding
        signal.insert(p*4+1,bl*110)
        signal.insert(p*4+2,sign//111)
        signal.insert(p*4+3,sign%111)
        signal.insert(p*4+4,qlp*13+ilp+58)
        hdi.insert(p+1,min(max(ipr-ilp*3+1,0),2))
        hdq.insert(p+1,min(max(qpr-qlp*3+1,0),2))
    hdtext = ""
    for n in range(0, height * 12):
        hdcolor.insert(n,hdi[n*2]+hdq[n*2]*3+hdi[n*2+1]*9+hdq[n*2+1]*27)
        hdtext = hdtext + chr((hdcolor[n]+9))

    text = ""
    for n in range(0, height * 96): #convert everything to text
        text = text + chr(mf(signal[n]+9.5))
    text = text + hdtext
    text=text.replace('"','~').replace('&', '{').replace(chr(10),'}').replace(chr(13),'|') #remove some unusable characters
    xpos = (frame-1)%50-25
    ypos = 25-(((frame-1)%5000)//50)/2
    obj = f'</object></c><c type="58"><object id="{frame+16317}" n="frame_{frame}" v="{text}"><pos x="{xpos}" y="{ypos}"/>'
    f = open("resources/object.xml", 'a')
    f.write(obj)
    f.close
    

for video in os.listdir("videos"):
    if video.endswith(".mp4"):
        f = open("resources/object.xml", 'w')
        f.write("")
        nameofmodule = video
        print(nameofmodule)
        location = os.path.join("videos", video)
        metadata = iio.immeta(location, plugin="pyav") #get fps and number of frames
        fps = metadata.get('fps')
        props = iio.improps(location, plugin="pyav")
        num_frames = int (metadata.get('duration') * fps)
        height = props.shape[1]
        print(f"Framecount: {num_frames}")
        print(f"Framerate: {fps}")
        for n in range(1,num_frames):
            fread(n)
            print(n)
        f = open("resources/object.xml")
        videofile = f.read()
        f.close
        f = open("resources/template.xml") #set important values + title
        file = f.read().replace("TITLE_HERE",nameofmodule.replace(".mp4","")).replace("FRAMERATE_HERE",f"{fps:.3f}").replace("FRAMECOUNT_HERE",f"{num_frames-1}").replace("FRAMEHEIGHT_HERE",f"{height}").replace("≥",videofile)
        f.close
        f = open(f"xmls/{nameofmodule}".replace(".mp4",".xml"), 'w')
        f.write(file)
        f.close()



print("done")