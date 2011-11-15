import numpy as np
import nibabel as nib
import pyglet as pyglet
from pyglet.gl import *
from fos.core.arrayimage import ArrayInterfaceImage
from fos.core.actor import Actor
from fos.core.utils import screen_to_model
import fos.core.collision as cll
from pyglet.window import key


# cube ///////////////////////////////////////////////////////////////////////
#    v6----- v5
#   /|      /|
#  v1------v0|
#  | |     | |
#  | |v7---|-|v4
#  |/      |/
#  v2------v3

t=0.5#np.sqrt(2.)/2.
# vertex coords array
cube_vertices = np.array([[t,t,t],  [-t,t,t],  [-t,-t,t],  [t,-t,t],   # v0-v1-v2-v3
                      [t,t,t],  [t,-t,t],  [t,-t,-t],  [t,t,-t],        # v0-v3-v4-v5
                      [t,t,t],  [t,t,-t],  [-t,t,-t],  [-t,t,t],        # v0-v5-v6-v1
                      [-t,t,t],  [-t,t,-t],  [-t,-t,-t],  [-t,-t,t],    # v1-v6-v7-v2
                      [-t,-t,-t],  [t,-t,-t],  [t,-t,t],  [-t,-t,t],    # v7-v4-v3-v2
                      [t,-t,-t],  [-t,-t,-t],  [-t,t,-t],  [t,t,-t]],'f4')   # v4-v7-v6-v5




class Slicer(Actor):

    def __init__(self,affine,data,alpha):
        """ creates a slicer object
        
        Parameters
        -----------
        affine : array, shape (4,4), image affine
                
        data : array, shape (X,Y,Z), data volume
        
        alpha : transparency
                
        """

        self.shape=data.shape
        self.data=data
        self.affine=affine
        #volume center coordinates
        self.vxi,self.vxj,self.vxk=self.shape[0]/2,self.shape[1]/2,self.shape[2]/2
        #self.update_vox_coords(self.vxi,self.vxj,self.vxk)
        self.x,self.y,self.z=0,0,0
        self.alpha=alpha        
        #slicer step
        self.step=1        
        self.sli=self.update_slice(0,self.vxi)
        self.slj=self.update_slice(1,self.vxj)
        self.slk=self.update_slice(2,self.vxk)        
        self.show_slices=np.array([True,True,True])        
        self.vertices=np.array([[-100,-100,-100],[100,100,100]])
        self.make_aabb(margin=0)
        self.show_aabb=True
        #masking        
        self.masks_list=[]
        self.mask=np.zeros(data.shape)
        self.cube_roi_element=cube_vertices
        self.cube_size=1
        self.cube_size_max=min((self.vxi,self.vxj,self.vxk))
        self.cube_size_min=1        
        self.cube_roi_color_selected=np.array([1,1,0,1.],'f4')
        self.cube_roi_color_stored=np.array([0,1,1,1.],'f4')
        self.cube_roi_vertices=None
        self.cube_roi_colors=None
        self.cube_first=None
        self.cube_count=None
        self.cube_no=0
        
    def add_roi(self,cube,color):
        cube_roi_colors=np.ascontiguousarray(np.tile(color,(len(self.cube_roi_element),1)))        
        self.cube_no+=1
        if self.cube_roi_colors==None:            
            self.cube_roi_vertices=np.ascontiguousarray(cube.copy(),dtype=np.float32)
            self.cube_roi_colors=np.ascontiguousarray(np.tile(color,(len(self.cube_roi_element),1)),dtype=np.float32)            
            #self.cube_first=np.array([0],dtype=np.int32)
            #self.cube_count=np.array([24],dtype=np.int32)
        else:
            self.cube_roi_vertices=np.append(self.cube_roi_vertices,cube,axis=0)
            self.cube_roi_vertices=np.ascontiguousarray(self.cube_roi_vertices,dtype=np.float32)            
            self.cube_roi_colors=np.append(self.cube_roi_colors,cube_roi_colors,axis=0)
            self.cube_roi_colors=np.ascontiguousarray(self.cube_roi_colors,dtype=np.float32)            
            #self.cube_first=np.append(self.cube_first,np.array([self.cube_first[-1]+24]))
            #self.cube_count=np.append(self.cube_count,np.array([24]))            
            #self.cube_first=np.ascontiguousarray(self.cube_first,dtype=np.int32)
            #self.cube_count=np.ascontiguousarray(self.cube_count,dtype=np.int32)
    def change_roi(self,vertices,color):
        curr=(self.cube_no-1)*24        
        if vertices!=None:
            self.cube_roi_vertices[curr:curr+24]=vertices
        if color!=None:
            colors=np.tile(color,(24,1))
            self.cube_roi_colors[curr:curr+24]=colors

    def update_slice(self,slice,position):       
        if slice==0:
            sl=self.data[position,:,:]#axis flipping check affine
        if slice==1:
            sl=self.data[:,position,:].T #no axis flipping
        if slice==2:            
            sl=self.data[:,:,position].T #no axis flipping           
        sl=np.interp(sl,[sl.min(),sl.max()],[0,255]).astype(np.uint8)        
        sl_rgba=np.ones(sl.shape+(4,),dtype=np.uint8)
        sl_rgba[:,:,0]=sl
        sl_rgba[:,:,1]=sl
        sl_rgba[:,:,2]=sl
        if self.alpha==None:            
            sl_rgba[:,:,3]=sl
        else:
            sl_rgba[:,:,3]=self.alpha
        tex = ArrayInterfaceImage(sl_rgba).texture       
        spr=pyglet.sprite.Sprite(tex, x=0, y=0)                       
        spr.position=(-spr.width/2, - spr.height/2)        
        return spr

    def draw(self):        
        if np.sum(self.show_slices)!=0:        
            self.set_state()            
            if self.show_slices[0]:
                glPushMatrix()
                glRotatef(-90.,0,1,0.)
                glTranslatef(0,0,-self.x)
                self.sli.draw()
                glPopMatrix()        
            if self.show_slices[1]:
                glPushMatrix()
                glRotatef(90.,1,0,0.)
                glTranslatef(0,0,-self.y)
                self.slj.draw()
                glPopMatrix()          
            if self.show_slices[2]:
                glPushMatrix()
                glTranslatef(0,0,self.z)
                self.slk.draw()     
                glPopMatrix()                
            #self.draw_aabb()
            if self.cube_roi_vertices!=None:
                #print('drawing cube')
                self.draw_cube()            
            self.unset_state()

    def draw_cube(self):        
        #print self.cube_no
        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glVertexPointer(3,GL_FLOAT,0,self.cube_roi_vertices.ctypes.data)
        glColorPointer(4,GL_FLOAT,0,self.cube_roi_colors.ctypes.data)
        glPushMatrix()
        #glib.glMultiDrawArrays(GL_QUADS, self.cube_first.ctypes.data,self.cube_count.ctypes.data, self.cube_no)
        for i in range(self.cube_no):
            glDrawArrays(GL_QUADS,i*24,24)
        glPopMatrix()
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    
    def process_pickray(self,near,far):
        pass
    
    def process_mouse_motion(self,x,y,dx,dy):
        self.mouse_x=x
        self.mouse_y=y
    
    def process_keys(self,symbol,modifiers):
        
        #NEEDS to change
        if modifiers & key.MOD_SHIFT:            
            print 'Shift'
            #print("Increase step.")
            self.step=5             
        if symbol == key.UP:
            print 'Up'
            if self.vxk<self.data.shape[-1]:            
                self.vxk+=self.step
                self.z+=self.step                
            self.slk=self.update_slice(2,self.vxk)            
            self.step=1 
        if symbol == key.DOWN:
            print 'Down'            
            if self.vxk>=0:            
                self.vxk-=self.step
                self.z-=self.step  
            self.slk=self.update_slice(2,self.vxk)            
            self.step=1
        if symbol == key.LEFT:
            print 'Left'
            if self.vxi>=0:            
                self.vxi-=self.step
                self.x-=self.step       
            self.sli=self.update_slice(0,self.vxi)
            self.step=1         
        if symbol == key.RIGHT:
            print 'Right'
            if self.vxi<self.data.shape[0]:            
                self.vxi+=self.step
                self.x+=self.step
            self.sli=self.update_slice(0,self.vxi)
            self.step=1            
        if symbol == key.PAGEUP:
            print 'PgUp'
            if self.vxj<self.data.shape[1]:            
                self.vxj+=self.step
                self.y+=self.step                
            self.slj=self.update_slice(1,self.vxj)
            self.step=1
        if symbol == key.PAGEDOWN:
            print 'PgDown'
            if self.vxj>=0:            
                self.vxj-=self.step
                self.y-=self.step            
            self.slj=self.update_slice(1,self.vxj)
            self.step=1
        #HIDE SLICES
        if symbol == key._0:
            print('0')
            if np.sum(self.show_slices)==0:
                self.show_slices[:]=True
            else:
                self.show_slices[:]=False
        if symbol == key._1:
            print('1')
            self.show_slices[0]= not self.show_slices[0]            
        if symbol == key._2:
            print('2')
            self.show_slices[1]= not self.show_slices[1]            
        if symbol == key._3:
            print('3')
            self.show_slices[2]= not self.show_slices[2]            
        if symbol == key.HOME:
            print('Home')
            if self.alpha<255:
                self.alpha+=1
                self.sli=self.update_slice(0,self.vxi)
                self.slj=self.update_slice(1,self.vxj)
                self.slk=self.update_slice(2,self.vxk)
        if symbol == key.END:            
            print('End')
            if self.alpha>0:
                self.alpha-=1
                self.sli=self.update_slice(0,self.vxi)
                self.slj=self.update_slice(1,self.vxj)
                self.slk=self.update_slice(2,self.vxk)
        if symbol == key.M:
            print('M - Maximizing ROI')
            if self.cube_size<self.cube_size_max:
                self.cube_size+=1
                self.cube_roi_element=self.cube_size*cube_vertices+self.cube_center
                self.change_roi(self.cube_roi_element, [1,1,0,1])
                print('ROI magnification %d' % self.cube_size)
        if symbol == key.N:
            print('N - miNimizing ROI')
            if self.cube_size>self.cube_size_min:
                self.cube_size-=1
                self.cube_roi_element=self.cube_size*cube_vertices+self.cube_center
                self.change_roi(self.cube_roi_element, [1,1,0,1])
                print('ROI magnification %d' % self.cube_size)
        if symbol == key.SPACE:
            print('Space - Select ROI')
            x, y = self.mouse_x, self.mouse_y
            # Define two points in model space from mouse+screen(=0) position and mouse+horizon(=1) position
            near = screen_to_model(x, y, 0)
            far = screen_to_model(x, y, 1)
            bx,by,bz=self.data.shape
            center=np.array([bx/2.,by/2.,bz/2.])
            #find intersection point on the closest slice
            point=self.slices_ray_intersection(near, far, center)
            if point !=None:
                self.cube_center=point
                self.cube_roi_element=self.cube_size*cube_vertices+point                        
                self.volume_point=np.round(point+center).astype(np.int)
                self.add_roi(self.cube_roi_element,[1,1,0,1.])
            else:
                print('no intersection point')
                
        if symbol == key.ENTER:
            print('Enter - Store ROI in mask')
            #self.masks_list.append(mask)
            if self.cube_size>1:                            
                v0,v1,v2=self.volume_point
                r=self.cube_size/2
                self.mask[v0-r:v0+r,v1-r:v1+r,v2-r:v2+r]=1
            if self.cube_size==1:                        
                self.mask[tuple(self.volume_point)]=1
            #self.cube_roi_colors=np.ascontiguousarray(np.tile(self.cube_roi_color_stored,(len(cube_vertices),1)))
            self.change_roi(vertices=None, color=[0,1,1,1])
                    
        if symbol == key.D:
            print('D - All ROIs deleted and mask reseted')
            self.mask[:,:,:]=0
            self.cube_roi_vertices=None
            self.cube_roi_colors=None
            self.cube_first=None
            self.cube_count=None
            self.cube_no=0
        
        if symbol == key.QUESTION:
            print """
>>>>Slicer
LEFT, RIGHT, UP, DOWN, PGUP, PGDOWN : change slice.
SHIFT + (LEFT, RIGHT, UP, DOWN, PGUP, PGDOWN): change slices faster.
1, 2, 3 : hide/show slice.
0 : hide/show all slices.
>>>>Mask
SPACE : Select ROI
M : Maximize ROI
N : minNimize ROI
ENTER : Store ROI in mask
G : Get tracks intersecting with mask
D : Delete all ROIs and reset mask
? : this menu
            """        
            
    def slices_ray_intersection(self,near,far,center):
        
        bx,by,bz=self.data.shape
        point=None
        #x plane
        px0=[self.x,-by/2.,-bz/2.]
        px1=[self.x,-by/2., bz/2.]
        px2=[self.x, by/2., bz/2.]
        success_x,dist_x,point_x = cll.intersect_segment_plane(near,far,px0,px1,px2)
        print 'success_x',success_x, 'dist x:',dist_x, 'point x', point_x            
        if success_x:
            if point_x[1]>=px0[1] and point_x[1]<=px2[1] and point_x[2]>=px0[2] and point_x[2]<=px2[2]:                        
                success_x=True                                                                                      
            else:
                success_x=False
        #y plane
        py0=[-bx/2.,self.y,-bz/2.]
        py1=[-bx/2.,self.y, bz/2.]
        py2=[ bx/2.,self.y, bz/2.]
        success_y,dist_y,point_y = cll.intersect_segment_plane(near,far,py0,py1,py2)
        #print 'dist y:',dist_y
        print 'success_y',success_y, 'dist y:',dist_y, 'point y', point_y
        if success_y:
            if point_y[0]>=py0[0] and point_y[0]<=py2[0] and point_y[2]>=py0[2] and point_y[2]<=py2[2]:                        
                success_y=True                                                                                      
            else:
                success_y=False
        #z plane
        pz0=[-bx/2.,-by/2.,self.z]
        pz1=[-bx/2., by/2.,self.z]
        pz2=[ bx/2., by/2.,self.z]
        success_z,dist_z,point_z = cll.intersect_segment_plane(near,far,pz0,pz1,pz2)            
        #print 'dist z:',dist_z
        print 'success_z',success_z, 'dist z:',dist_z, 'point z', point_z
        if success_z:
            if point_z[0]>=pz0[0] and point_z[0]<=pz2[0] and point_z[1]>=pz0[1] and point_z[1]<=pz2[1]:                        
                success_z=True                                                                                      
            else:
                success_z=False
        
        print 'success_x',success_x
        print 'success_y',success_y
        print 'success_z',success_z
        
        if dist_x==None:
            dist_x=np.finfo(np.float64)
        if dist_y==None:
            dist_y=np.finfo(np.float64)
        if dist_z==None:
            dist_z=np.finfo(np.float64)
        
        #check nearest
        if success_x:
            if dist_x < dist_y and dist_x < dist_z: 
                return point_x
        if success_y:
            if dist_y < dist_x and dist_y < dist_z: 
                return point_y
        if success_z:
            if dist_z < dist_x and dist_z < dist_y: 
                return point_z
        #print point_x, point_y, point_z
        #print 'return ',point
        return None
        
            
            
    def save_mask(self,fname,mask):               
        img_mask=nib.Nifti1Image(mask,self.affine)
        nib.save(img_mask,fname)

    def set_state(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def unset_state(self):
        glDisable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)                       
   
    def update(self,dt):
        pass





