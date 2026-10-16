from patchlib import *
im=load('src/img-019.png'); K=(40,40,40)
fill(im,(214,436,256,456),from_pt=(260,440)); fill(im,(224,424,256,456),from_pt=(260,440))
g=sample(im,795,690,1)
rep(im,(798,673,1052,701),[[('Landauer floor: ','n'),('E','i'),(' ≥ ','n'),('k','i'),('B','i_sub'),('T','i'),(' ln 2','n')]],20,K,bg=g)
p=sample(im,1178,700,1)
rep(im,(1180,660,1650,697),[[('Compare with the 0.10–0.12 J estimates','b')]],22,(105,35,215),bg=p,pad=2)
rep(im,(1180,703,1650,736),[[('(BOLD-calibrated / spike-count; unvalidated)','n')]],19,(60,60,60),bg=p,pad=2)
im.save('out/P4F1.png')
