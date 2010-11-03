""" Thanks to the sympy project
REMINDER: remove the clock from the window and put it to the engine """

from fos.lib.pyglet.window import Window
from fos.lib.pyglet.clock import Clock

from threading import Thread, Lock

gl_lock = Lock()

class ManagedWindow(Window):
    """
    A pyglet window with an event loop which executes automatically
    in a separate thread. Behavior is added by creating a subclass
    which overrides setup, update, and/or draw.
    """

    default_win_args = dict(width=640,
                            height=480,
                            vsync=False,
                            resizable=False)

    def __init__(self, **win_args):
        """
        It is best not to override this function in the child
        class, unless you need to take additional arguments.
        Do any OpenGL initialization calls in setup().
        """
        self.win_args = dict(self.default_win_args, **win_args)
        self.Thread=Thread(target=self.__event_loop__)
        self.Thread.start()

    def __event_loop__(self, **win_args):
        """
        The event loop thread function. Do not override or call
        directly (it is called by __init__).
        """
        gl_lock.acquire()
        try:
            try:
                super(ManagedWindow, self).__init__(**self.win_args)
                self.switch_to()
                self.setup()
            except Exception, e:
                print "Window initialization failed: %s" % (str(e))
                self.has_exit = True
        finally:
            gl_lock.release()

        clock = Clock()
        clock.schedule_interval(self.update, self.update_dt)
        
        while not self.has_exit:
            # the clock needs to tick but we are not using dt
            # dt = clock.tick()
            gl_lock.acquire()
            clock.tick(poll=False)
            try:
                try:
                    self.switch_to()
                    self.dispatch_events()
                    self.clear()
                    # the update is called as a scheduled function
                    # using the clock, not in the event loop anymore
#                    self.update(dt)
                    self.draw()
                    self.flip()
                except Exception, e:
                    print "Uncaught exception in event loop: %s" % str(e)
                    self.has_exit = True
            finally:
                gl_lock.release()
        super(ManagedWindow, self).close()

    def setup(self):
        """
        Called once before the event loop begins.
        Override this method in a child class. This
        is the best place to put things like OpenGL
        initialization calls.
        """
        pass

    def update(self, dt):
        """
        Called before draw during each iteration of
        the event loop. dt is the elapsed time in
        seconds since the last update. OpenGL rendering
        calls are best put in draw() rather than here.
        """
        pass

    def draw(self):
        """
        Called after update during each iteration of
        the event loop. Put OpenGL rendering calls
        here.
        """
        pass



#    def close(self):
#        '''Close the window.
#
#        After closing the window, the GL context will be invalid.  The
#        window instance cannot be reused once closed (see also `set_visible`).
#
#        The `pyglet.app.EventLoop.on_window_close` event is dispatched on
#        `pyglet.app.event_loop` when this method is called.
#        '''
#        self.has_exit = True
#        try:
#            super(ManagedWindow, self).close()
#        except Exception, e:
#            print "exception while closing the window %s" % str(e)
#            pass
        
            
if __name__ == '__main__':
    ManagedWindow()
