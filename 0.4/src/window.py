from appuifw import *
import e32
import key_codes

__all__ = [ "Application", "Dialog" ]

class Window(object):
    
    __ui_lock = False
    
    def __init__(self, title, body, menu = None, exit_handler = None):
    
        self.title = title
        self.body = body
    
        if menu is None:
            menu = [(u"Exit", self.close_app)]

        if exit_handler is None:
            exit_handler = self.close_app

        self.menu =  menu
        self.exit_handler = exit_handler

    def set_title(self,title):
        app.title = self.title = title

    def get_title(self):
        return self.title

    def bind(self, key, cbk):
        self.body.bind(key,cbk)
        
    def refresh(self):
        app.title = self.title
        app.menu = self.menu
        app.body = self.body
        app.exit_key_handler = self.exit_handler

    def run(self):
        self.refresh()
        
    def lock_ui(self,title = u""):
        Window.__ui_lock = True
        app.menu = []
        app.exit_key_handler = lambda: None
        if title:
            app.title = title

    def unlock_ui(self):
        Window.__ui_lock = False

    def ui_is_locked(self):
        return Window.__ui_lock

class Application(Window):

    __highlander = None
    __lock = None
    
    def __init__(self, title, body, menu = None, exit_handler = None):
        """ Only one application is allowed. It is resposible for starting and finishing the program.
            run() is overrided for controling this behavior.
        """
        if Application.__highlander:
            raise Application.__highlander
        Application.__highlander = self

        if not Application.__lock:
            Application.__lock = e32.Ao_lock()

        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        Application.__lock.signal()
            
    def run(self):
        old_title = app.title
        self.refresh()        
        Application.__lock.wait()
        # restore everything !
        app.set_tabs( [], None )
        app.title = old_title
        app.menu = []
        app.body = None
        #app.set_exit()        

class Dialog(Window):
    def __init__(self, cbk, title, body, menu = None, exit_handler = None):
        """ Create a dialog. cbk is called when dialog is closing. Dialog contents, like title and body need
            to be specified. If menu or exit_handler are not specified, defautl values
            for dialog class are used. 
        """
        self.cbk = cbk
        self.cancel = False        
        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        """ When closing the dialog, a call do self.cbk() is done. If this function returns True
            the dialog is not refreshed and the latest dialog/window takes control. If something fails
            during calback execution, callback function should return False and does not call refresh().
            Using self.cancel it is possible to determine when the dialog  was canceled or not. 
        """
        if self.cbk() == False:
            self.refresh()

    def cancel_app(self):
        """ Close the dialog but turn the cancel flag on.
        """
        self.cancel = True
        self.close_app()
