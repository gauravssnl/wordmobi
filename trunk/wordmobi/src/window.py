'''
The API for writing applications using Python for S60 is really straightforward.
Since you have decided what kind of body your  application will use
(canvas, listbox, or text), you need to define your main menu, application title
and default callback handler for exiting. The user interface (UI) is based on events
and there is a special mechanism that relies on a semaphore for indicating that the
application is closing. The user must obtain the semaphore and wait for any signal on it.
Once signalized, the application may close properly. The UI allows tabs as well but in
this case a body must be defined for each tab. An routine for handling tabs changing is
required in such situation. 
However, if your application has more than one window, I mean, more than a set of body,
menu and exit handler, you will need exchanging these elements each time a new windows is
displayed, giving to the user the impression that he is using a multiple windows application.
Although this solution is possible, some problems arise:

* the strategy for exiting, based on semaphores, must be unique across your application.
* you may not commit any mistake when switching UI, that is, the set body+menu+exit
  handler must be consistently changed   
* an unified strategy for blocking UI when a time consuming operation is pending is necessary.
  For instance, when downloading a file, you may want to disable all menu options.
  Otherwise they will be available for the user during the download operation. 

For unifying this process, three additional classes are suggested in this article.

The first, called Window, is responsible for holding UI contents like menu, body
and exit handler and exchanging properly all UI elements for the derived classes.
Moreover, it may lock/unlock the UI when necessary.

The second class is named Application. It represents the running application itself
and it is responsible for handling the termination semaphore. Only one Application
class must be instantiated per application.

Finally, the third class is called Dialog. As its name suggests, it is in the charge
of showing/hiding dialogs when necessary. Many dialogs are allowed, each one with
their own set of body+menu+exit handler.  

Application and Dialog inherit from Window the content handler ability while each one
has different ways for finishing itself (finishing application or just the dialog).
'''
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
            raise
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
        app.set_exit()        

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
