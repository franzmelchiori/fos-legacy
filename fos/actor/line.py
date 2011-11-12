import numpy as np
from fos.lib.pyglet.gl import *
from fos.lib.pyglet.lib import load_library
glib=load_library('GL')
from fos.actor.axes import Axes
from fos import Actor,World, Window, WindowManager

class Line(Actor):
    """ Lines, curves, tracks actor

    """

    def __init__(self,tracks,colors=None, line_width=2.,affine=None):
	if affine==None:
		self.affine=np.eye(4)
	else: self.affine=affine
	self.tracks_no=len(tracks)
	self.tracks_len=[len(t) for t in tracks]
	self.tracks=tracks
        self.vertices = np.ascontiguousarray(np.concatenate(self.tracks).astype('f4'))        
	if colors==None:
        	self.colors = np.ascontiguousarray(np.ones((len(self.vertices),4)).astype('f4'))
	else:		
        	self.colors = np.ascontiguousarray(colors.astype('f4'))	
        self.vptr=self.vertices.ctypes.data
        self.cptr=self.colors.ctypes.data        
        self.count=np.array(self.tracks_len, dtype=np.int32)
        self.first=np.r_[0,np.cumsum(self.count)[:-1]].astype(np.int32)
        self.firstptr=self.first.ctypes.data
        self.countptr=self.count.ctypes.data
        self.line_width=line_width
        self.items=self.tracks_no
        self.show_aabb = False        
        mn=self.vertices.min()
	mx=self.vertices.max()
	self.make_aabb((np.array([mn,mn,mn]),np.array([mx,mx,mx])),margin = 0)        
    
    def update(self, dt):
        pass

    def draw(self):
        #glEnable(GL_MULTISAMPLE)
	glEnable(GL_DEPTH_TEST)
	glEnable(GL_LINE_SMOOTH)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
	glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
	glLineWidth(self.line_width)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3,GL_FLOAT,0,self.vptr)
        glColorPointer(4,GL_FLOAT,0,self.cptr)
        glPushMatrix()
        glib.glMultiDrawArrays(GL_LINE_STRIP, \
                                self.firstptr,\
                                self.countptr,\
                                self.items)
        glPopMatrix()
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)      
        glLineWidth(1.)
	glDisable(GL_LINE_SMOOTH)
	glDisable(GL_BLEND)
	glDisable(GL_DEPTH_TEST)
	#glDisable(GL_MULTISAMPLE)

if __name__ == '__main__':    
	
    tracks=[100*np.random.rand(100,3),100*np.random.rand(20,3)]
    colors=np.ones((120,4))
    colors[0:100,:3]=np.array([1,0,0.])
    colors[100:120,:3]=np.array([0,1,0])
    ax = Line(tracks,colors,line_width=20)

    w=World()
    w.add(ax)        
    wi = Window(caption=" Line plotting (fos.me)",\
            bgcolor=(0,0.,0.2,1),width=800,height=600)
    wi.attach(w)    	
    wm = WindowManager()
    wm.add(wi)
    wm.run()
    
