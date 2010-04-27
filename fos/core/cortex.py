import os
import time
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import Image
import PIL.ImageOps as iops
from fos.core.utils import list_indices as lind
from os.path import join as pjoin

from dipy.core import track_metrics as tm

import fos.core.collision as cll

data_path = pjoin(os.path.dirname(__file__), 'data')



class CorticalSurface(object):

    def __init__(self,fname):

       
        self.fname = fname
        
        self.position  = [0.0, 0.0, 0.0]

        self.scale     = None #[100., 50., 20.]

        
        self.ambient   = [1, 1, 1, 1.]
        
        self.diffuse   = [1, 1, 1, 1.]
        
        self.specular  = [1, 1, 1, 1.]

        #self.shininess = 5.

        #self.emission  = [0.1, 0.1, 0.1, 1.]
       
        
        self.list_index = None
        
        self.name_index = None

        self.pts = None

        self.polys = None

        self.normals = None
        


    def load_polydata(self):

        f=open(self.fname,'r')
        
        lines=f.readlines()

        taglines=[l.startswith('POINTS') or l.startswith('POLYGONS')  for l in lines]

        pts_polys_tags=[i for i in lind(taglines,True)]

        if len(pts_polys_tags)<2:

            NameError('This must be the wrong file no polydata in.')

        #read points
            
        pts_index = pts_polys_tags[0]
              
        pts_tag = lines[pts_index].split()

        pts_no = int(pts_tag[1])

        pts=lines[pts_index+1:pts_index+pts_no+1]

        self.pts=np.array([np.array(p.split(),dtype=np.float32) for p in pts])

        #read triangles
        
        polys_index = pts_polys_tags[1]

        #print polys_index

        polys_tag = lines[polys_index].split()

        polys_no = int(polys_tag[1])

        polys=lines[polys_index+1:polys_index+polys_no+1]

        self.polys=np.array([np.array(pl.split(),dtype=np.int) for pl in polys])[:,1:]

        print 'polys.shape', self.polys.shape

        print 'polys[0]', self.polys[0]


    def calculate_normals(self):
        
        p=self.pts

        print 'pts.shape',p.shape
        

        normals=np.zeros((len(self.pts),3),np.float32)

        normalscnt=np.zeros((len(self.pts),1),np.float32)
        

        l=self.polys

        

        '''
        normals=np.cross(p[l[:,0]]-p[l[:,1]],p[l[:,1]]-p[l[:,2]],axisa=1,axisb=1)

        #print 'normals.shape', normals.shape

        #print normals[:20]

        div=np.sqrt(np.sum(normals**2,axis=1))

        div=div.reshape(len(div),1)

        normals=normals/div

        '''


        '''
        trnormal=np.cross(p[l[:,0]]-p[l[:,1]],p[l[:,1]]-p[l[:,2]],axisa=1,axisb=1)

        div=np.sqrt(np.sum(trnormals**2,axis=1))

        div=div.reshape(len(div),1)

        trnormals = trnormals/div

        trnormals[l] = 

        for tr in trnormals:

            normals[l] += normal

           

        '''
        for l in self.polys:

            normal = np.cross( p[l[0]] - p[l[1]], p[l[1]] - p[l[2]] )

            normal = normal/np.linalg.norm(normal)

            normals[l] += normal
            
            normalscnt[l] += 1

        #'''

        self.normals=(normals/normalscnt).astype(np.float32)

        print 'normals.shape', self.normals.shape
        #print 'normals.dtype', self.normals.dtype
        
        print self.normals[:20]
        
        

    def init(self):

        time1=time.clock()

        self.load_polydata()

        print 'load disk',time.clock() - time1

        self.calculate_normals()

        print 'calc normals', time.clock() - time1

        self.list_index = gl.glGenLists(1)

        gl.glNewList( self.list_index,gl.GL_COMPILE)

       
        #gl.glEnable(gl.GL_NORMALIZE)  

        gl.glEnable(gl.GL_BLEND)
      
        gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)

        #gl.glDisable(gl.GL_LIGHTING)        

        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        
        #gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)

        gl.glVertexPointerf(self.pts)

        #print 'oops'

        gl.glNormalPointerf(self.normals)

        triangles=np.ravel(self.polys).astype(np.uint)

        #print 'normals'
                
        gl.glDrawElementsui(gl.GL_TRIANGLES,triangles)
            

        #print 'draw'

        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)
        
        #gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

        gl.glEndList()


        print 'time ',time.clock()-time1

    
    def display(self):
        
        #self.ambient[3]-=0.001
        
        #self.diffuse[3]-=0.001
        
        #self.specular[3]-=0.001        


        gl.glMaterialfv( gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT, self.ambient )

        gl.glMaterialfv( gl.GL_FRONT_AND_BACK, gl.GL_DIFFUSE, self.diffuse )

        gl.glMaterialfv( gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, self.specular )



        gl.glCallList(self.list_index)
    





    


