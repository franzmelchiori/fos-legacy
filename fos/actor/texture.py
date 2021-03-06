import numpy as np
import nibabel as nib
import pyglet
pyglet.options['debug_gl'] = True
pyglet.options['debug_x11'] = True
#pyglet.options['debug_gl_trace'] = True
pyglet.options['debug_texture'] = True

from ctypes import *
from pyglet.gl import *
from fos.core.actor import Actor
from fos.core.utils import screen_to_model
import fos.core.collision as cll
from pyglet.window import key
from fos import World, Window, WindowManager
from fos.actor.axes import Axes

class Texture2D(Actor):

    def __init__(self,data,affine=None):
        """ creates a 2d texture actor showing data
        
        Parameters
        ----------- 
        data : array, shape (X,Y) for Grayscale  
                or (X.Y,3) for RGB
                or (X,Y,4) for RGBA
                                
        affine : array, shape (4,4), space affine
        
        """

        self.shape=data.shape
        self.data=data
        self.affine=affine        
        if data.ndim==2:      
            self.size=data.shape        
            self.format = GL_LUMINANCE #GL_RGBA GL_RGB GL_LUMINANCE
            self.components = 1 # 3 for RGB and 4 for RGBA        
        if data.ndim==3:
            self.size=data.shape[:2]
            if data.shape[2]==3:
                self.format = GL_RGB
                self.components = 3                
            if data.shape[2]==4:
                self.format = GL_RGBA
                self.components = 4
        self.x,self.y,self.z=0,0,0
        self.vertices=np.array([[-100,-100,-100],[100,100,100]])
        self.make_aabb(margin=0)
        self.show_aabb=False          
        self.create_texture()
        
    def create_texture(self):        
        self.texture_index = c_uint(0)        
        glGenTextures(1,byref(self.texture_index))
        glBindTexture(GL_TEXTURE_2D, self.texture_index.value)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        #glPixelStorei(GL_PACK_ALIGNMENT,1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        w,h = self.size
        glTexImage2D(GL_TEXTURE_2D, 0, self.components, w, h, 0, self.format, GL_UNSIGNED_BYTE, self.data.ctypes.data)
        self.list_index = glGenLists(1)
        glNewList( self.list_index,GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE,GL_REPLACE)
        glBindTexture(GL_TEXTURE_2D, self.texture_index.value)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-w/2., -h/2., 0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-w/2., h/2., 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(w/2., h/2., 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(w/2., -h/2., 0.0)        
        glEnd()
        glFlush()
        glDisable(GL_TEXTURE_2D)
        glEndList()

    def draw(self):
        self.set_state()
        glPushMatrix()        
        glCallList(self.list_index)
        glPopMatrix()            
        self.unset_state()
   
    def process_pickray(self,near,far):
        pass
    
    def process_mouse_motion(self,x,y,dx,dy):
        self.mouse_x=x
        self.mouse_y=y
    
    def process_keys(self,symbol,modifiers):        
        if symbol == key.SPACE:
            print('Space')

    def set_state(self):
        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)                       
   
    def update(self,dt):
        pass


if __name__ =='__main__':
    
    ax = Axes(100)
    data=np.round(255*np.random.rand(182,218,4)).astype(np.ubyte)
    #data=np.round(255*np.ones((182,218,4))).astype(np.ubyte)
    data[70:120,:,:3]=100    
    data[:,:,3]=150
    data=data.astype(np.ubyte)
    tex=Texture2D(data)
    w=World()
    w.add(ax)
    w.add(tex)
    wi = Window(caption="Texture by Free On Shades (fos.me)",\
                bgcolor=(0,0.,0.2,1),width=800,height=600)
    wi.attach(w)
    wm = WindowManager()
    wm.add(wi)
    wm.run()
    



