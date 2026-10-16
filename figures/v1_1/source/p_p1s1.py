from patchlib import *
im=load('src/img-006.png'); K=(25,25,25); W=(255,255,255)
def ttl(box,spec,size=27):
    fill(im,box,W); cx=(box[0]+box[2])/2; draw_rich(im,(cx,box[3]-6),spec,size,K,anchor='c')
ttl((628,10,950,47),[('τ','bi'),('S','b_sub'),(' (accumulation time constant)','b')],26)
ttl((1105,10,1450,47),[('Π','bi'),('i','bi_sup'),('baseline','b_sub'),(' (interoceptive precision)','b')],26)
ttl((95,468,460,505),[('β','bi'),('SM','b_sub'),(' (somatic-marker gain)','b')])
ttl((1120,480,1470,513),[('β','i'),('SM','n_sub'),(' × ','n'),('Π','i'),('i','i_sup'),('baseline','n_sub'),(' collinearity (Pearson ','n'),('r','i'),(')','n')],25)
# axis labels Pi
fill(im,(1018,150,1060,330),W)
draw_rot(im,(1040,235),[('Recovered ','n'),('Π','i'),('i','i_sup'),('baseline','n_sub')],27,K)
fill(im,(1230,410,1350,450),W)
draw_rich(im,(1290,443),[('True ','n'),('Π','i'),('i','i_sup'),('baseline','n_sub')],27,K,anchor='c')
# bar label and legend M-hat
fill(im,(1318,832,1450,862),W); draw_rich(im,(1384,857),[('M','n^'),(' estimation','n')],23,K,anchor='c')
# legend entries
def leg(box,spec,size=21):
    fill(im,box,W); draw_rich(im,(box[0]+2,box[3]-6),spec,size,K)
leg((576,912,846,944),[('τ','i'),('S','n_sub'),(' (accumulation time constant)','n')],17)
leg((870,912,1165,944),[('Π','i'),('i','i_sup'),('baseline','n_sub'),(' (interoceptive precision)','n')],18)
ImageDraw.Draw(im).ellipse((848,919,866,937),fill=(0,150,136))
leg((288,958,600,992),[('β','i'),('SM','n_sub'),(' (somatic-marker gain)','n')])
fill(im,(1236,949,1448,978),W); draw_rich(im,(1238,972),[('Pre-session ','n'),('M','n^'),(' estimation','n')],20,K)
im.save('out/P1S1.png')
