from patchlib import *
im=load('src/img-016.png'); d=ImageDraw.Draw(im)
inside=sample(im,250,240,1); out=(254,254,254); print('inside',inside)
thin=sample(im,164,420,0); print('thin',thin)
d.rounded_rectangle((161,226,598,328),radius=13,outline=out,width=4)
d.rounded_rectangle((164,229,595,325),radius=11,outline=inside,width=3)
d.rounded_rectangle((164,229,595,325),radius=11,outline=thin,width=2)
RD=(205,30,30)
for (y0,y1,sub) in [(188,220,'4,3'),(338,370,'3,2'),(484,517,'2,1')]:
    fill(im,(395,y0,478,y1),out)
    draw_rich(im,(402,y1-8),[('κ','n'),(sub,'n_sub'),(' ↑','dj')],22,RD)
fill(im,(411,842,442,870),out); fill(im,(586,842,616,870),out)
im.save('out/P3F4.png')
