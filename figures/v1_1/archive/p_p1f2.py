from patchlib import *
im=load('src/img-002.png'); W=(255,255,255); K=(30,30,30)
bg=sample(im,1150,200); print('bg',bg)
# B headers
fill(im,(1222,22,1518,138),bg); fill(im,(1560,22,2040,138),bg)
draw_rich(im,(1375,72),[('baseline','n')],46,K,anchor='c')
draw_rich(im,(1375,126),[('M','n^'),('(c,a) ≈ 0','n')],46,K,anchor='c')
draw_rich(im,(1800,72),[('somatic-marker retrieval','n')],46,K,anchor='c')
draw_rich(im,(1800,126),[('M','n^'),('(c,a) high','n')],46,K,anchor='c')
# B right: weaken SST->pyramid inhibition
glow=sample(im,1846,300,1); print('glow',glow)
fill(im,(1783,309,1840,343),bg)
d=ImageDraw.Draw(im); d.line([(1774,349),(1833,408)],fill=bg,width=16)
d.polygon([(1813,400),(1838,393),(1845,402),(1845,418),(1826,430)],fill=bg)
d.rectangle((1838,392,1846,430),fill=glow)
tbar(im,(1787,326),(1834,326),K,width=3,half=10)
tbar(im,(1776,352),(1826,402),K,width=3,half=10)
# elevated Pi^i_eff label
fill(im,(1874,255,2048,372),bg)
draw_rich(im,(1962,300),[('elevated','n')],44,K,anchor='c')
draw_rich(im,(1962,356),[('Π','n'),('i','n_sup'),('eff','n_sub')],46,K,anchor='c')
# C labels
fill(im,(1625,684,1992,742),bg); fill(im,(1656,742,1992,824),bg); fill(im,(1629,742,1660,771),bg); fill(im,(1629,789,1660,823),bg)
draw_rich(im,(1634,730),[('dendritic Ca','n'),('2+','n_sup')],44,K)
draw_rich(im,(1662,782),[('plateau','n')],44,K)
draw_rich(im,(1662,818),[('apical–basal coincidence','n')],31,K)
# A: delete duplicate upper label
g=sample(im,1000,560); print('panelA bg',g)
fill(im,(868,575,1082,724),g)
fill(im,(1634,766,1660,779),bg)
im.save('out/P1F2.png')
