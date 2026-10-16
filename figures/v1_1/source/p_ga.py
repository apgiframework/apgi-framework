from patchlib import *
im=load('src/img-000.png')
W=(252,252,252)
# GA-2 legend
fill(im,(735,950,1380,1068),W)
draw_rich(im,(752,1003),[('S','b'),('t','b_sub'),(': accumulated precision-weighted surprise','n')],37,(20,20,20))
draw_rich(im,(752,1052),[('θ','bi'),('t','bi_sub'),(': allostatically regulated access threshold','n')],37,(20,20,20))
# GA-3 reverse broadcast arrow
fill(im,(1283,662,1502,795),W); fill(im,(1500,662,1528,768),W)
p0,p1=(1300,705),(1505,785)
arrow(im,p0,p1,(70,40,90),width=40,head=95,headw=110)
arrow(im,(p0[0]+5,p0[1]+2),(p1[0]-7,p1[1]-3),(164,125,180),width=28,head=80,headw=86)
# GA-4 footer + heart label
c=sample(im,1385,1100,2); print('band',c)
fill(im,(1370,1086,2048,1143),c)
draw_rich(im,(1709,1128),[('Somatic Marker Hypothesis (SMH)','b')],34,(255,255,255),anchor='c')
tc=(150,55,35)
fill(im,(160,615,545,692),W)
draw_rich(im,(350,672),[('(somatic marker)','n')],50,tc,anchor='c')
# GA-5 label on ATP arrow
draw_rich(im,(1480,492),[('metabolic cost raises ','b'),('θ','bi'),('t','bi_sub')],33,(60,110,40),anchor='c')
im.save('out/GA.png')
