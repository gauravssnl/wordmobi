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

For unifying this process, three additional classes are suggested.

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

A simple application may be created as follow. User attention is focused on
application and not on appuifw stuff:

from windows import Application, Dialog
from appuifw import note

class MyApp(Application):
    def __init__(self):
        self.items = [ u"Option A",
                       u"Option B",
                       u"Option C" ]
        self.menu = [ (u"Menu A", self.option_a),
                      (u"Menu B", self.option_b),
                      (u"Menu C", self.option_c) ]
        
        self.body = Listbox( self.items, self.check_items )
        
        Application.__init__(self,
                             u"MyApp title",
                             self.body,
                             self.menu)
    
    def check_items(self):
        idx = self.body.current()
        ( self.option_a, self.option_b, self.option_c )[idx]()

    def option_a(self): note(u"A","info")
    def option_b(self): note(u"B","info")
    def option_c(self): note(u"C","info")

Suppose now user wants to add a dialog call in self.option_a:

class Notepad(Dialog):
    def __init__(self, txt=u""):
        self.body = Text(txt)
        Application.__init__(self, u"MyApp title", self.body)
    
class MyApp(Application)
    def __init__(self):
        self.txt = u""

        ....
    
    def option_a(self):
        def cbk():
            if not self.dlg.cancel:
                self.txt = self.dlg.body.get()
            self.refresh()
            return True
        
        self.dlg = Notepad(cbk, self.txt)
        self.dlg.run()

When a dialog is created, a callback function need to be defined.
This callback is called when the user cancels or closes the dialog.
Inside the callback body, it is possible to check if the dialog was
canceled verifying the cancel variable. Dialog variables may be
accessed as well. The callback function must either return True or False.
If it returns True, self.refresh() must be called before, inside callback
body. This way, the menu, body and exit handler will be updated using
the context of the dialog caller. If it returns False, self.refresh() is called
inside dialog context and dialog is restored.

'''

from appuifw import *
import e32
import key_codes

__all__ = [ "Application", "Dialog" ]

class Window(object):
    """ This class is responsible for holding UI contents like menu, body
        and exit handler and exchanging properly all UI elements for
        the derived classes. Moreover, it may lock/unlock the UI when necessary.
    """
    __ui_lock = False
    
    def __init__(self, title, body, menu = None, exit_handler = None):
        """ Creates a new window given a title, body and optional
            menu and exit handler. 
        """
    
        self.title = title
        self.body = body
    
        if menu is None:
            menu = [(u"Exit", self.close_app)]

        if exit_handler is None:
            exit_handler = self.close_app

        self.menu =  menu
        self.exit_handler = exit_handler

    def set_title(self,title):
        " Sets the current application title "
        app.title = self.title = title

    def get_title(self):
        " Returns the current application title "
        return self.title

    def bind(self, key, cbk):
        " Bind a key to the body. A callback must be provided."
        self.body.bind(key,cbk)
        
    def refresh(self):
        " Update the application itens (menu, body and exit handler) "
        app.title = self.title
        app.menu = self.menu
        app.body = self.body
        app.exit_key_handler = self.exit_handler

    def run(self):
        " Show the dialog/application "
        self.refresh()
        
    def lock_ui(self,title = u""):
        """ Lock UI (menu, body and exit handler are disabled).
            You may set a string to be shown in the title area.
        """
        Window.__ui_lock = True
        app.menu = []
        app.exit_key_handler = lambda: None
        if title:
            app.title = title

    def unlock_ui(self):
        "Unlock UI. Call refresh() for restoring menu, body and exit handler."
        Window.__ui_lock = False

    def ui_is_locked(self):
        "Chech if UI is locked or not, return True or False"
        return Window.__ui_lock

class Application(Window):
    """ This class represents the running application itself
        and it is responsible for handling the termination semaphore.
        Only one Application class must be instantiated per application.
    """
    __highlander = None
    __lock = None
    
    def __init__(self, title, body, menu = None, exit_handler = None):
        """ Only one application is allowed. It is resposible for starting
            and finishing the program.
            run() is overrided for controling this behavior.
        """
        if Application.__highlander:
            raise
        Application.__highlander = self

        if not Application.__lock:
            Application.__lock = e32.Ao_lock()

        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        """ Signalize the application lock, allowing run() to terminate the application.
        """
        Application.__lock.signal()
            
    def run(self):
        """ Show the the application and wait until application lock is
            signalized. After that, make all necessary cleanup.
        """
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
    """ This class is in the charge of showing/hiding dialogs when necessary.
        Many dialogs are allowed, each one with their own set of body+menu+exit
        handler.
    """
    def __init__(self, cbk, title, body, menu = None, exit_handler = None):
        """ Create a dialog. cbk is called when dialog is closing.
            Dialog contents, like title and body need
            to be specified. If menu or exit_handler are not specified,
            defautl values for dialog class are used. 
        """
        self.cbk = cbk
        self.cancel = False        
        Window.__init__(self, title, body, menu, exit_handler)

    def close_app(self):
        """ When closing the dialog, a call do self.cbk() is done.
            If this function returns True the dialog is not refreshed
            and the latest dialog/window takes control. If something fails
            during calback execution, callback function should return False
            and does not call refresh(). Using self.cancel it is possible
            to determine when the dialog  was canceled or not. 
        """
        if self.cbk() == False:
            self.refresh()

    def cancel_app(self):
        """ Close the dialog but turn the cancel flag on.
        """
        self.cancel = True
        self.close_app()
