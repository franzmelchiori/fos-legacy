import numpy as np

from fos import Window,World
from fos.actor.curve import InteractiveCurves


def test_picking_trajectories():

    curves=[100*np.random.rand(10,3),100*np.random.rand(5,3),100*np.random.rand(3,3)]
    curves=[100*np.array([[0,0,0],[1,0,0]]), 100*np.array([[0,1,0],[0,1,3]]),100*np.array([[0,2,0],[0,2,3]])]
    
    '''
    from nibabel import trackvis as tv
    #fname='/home/eg309/Data/PROC_MR10032/subj_01/101/1312211075232351192010091419011391228126452ep2dadvdiffDSI25x25x25b4000s003a001_FA_warp.trk'
    fname='/home/eg309/Data/fibers.trk'
    streams,hdr=tv.read(fname)
    T=[s[0] for s in streams]
    curves=T[:200000]
    '''
    
    #colors=np.random.rand(len(curves),4).astype('f4')
    colors=np.ones((len(curves),4)).astype('f4')
    for (i,c) in enumerate(curves):        
        orient=c[0]-c[-1]
        orient=np.abs(orient/np.linalg.norm(orient))
        colors[i,:3]=orient
    
    c=InteractiveCurves(curves,colors=colors)
    w=World()
    w.add(c)
    wi=Window()
    wi.attach(w)
