#!/usr/bin/python
# -*- coding: cp1252 -*-
"""
Author: Marcelo Barros de Almeida
<marcelobarrosalmeida@gmail.com>
License:
- GPLv2, for non-profit use
- For profit use, you must contact the author for discussing licensing model.
"""
from Tkinter import *
import tkMessageBox as msgbox
import tkFileDialog as inputbox
import os
import re
import sys
import math
from PIL import Image as img
import threading

CHRESGUI_VERSION = 'alpha 1'

def convert_thread(**op):
    # to be a thread in future
    files = os.listdir(op['srcdir'])
    files = filter(lambda x: x.lower().find('.jpg') > 0 or \
                   x.lower().find('.jpeg') > 0, files)
    nf = len(files)
    log = op['log']
    cancel = op['cancel']
    endconv = op['finished']
    
    if nf == 0:
        log('No image files to convert !')
        endconv()
        return
    
    nd = int(math.log10(nf)) + 1
    frm = "%s%%0%dd.jpg" % (op['prefix'],nd)
    n = 1
    m = 0
    for fs in files:
        if cancel():
            log('Operation aborted by user.')
            endconv()
            return
        fsrc = os.path.join(op['srcdir'],fs)
        fd = frm % (n)
        fdst = os.path.join(op['dstdir'],fd)
        # get next valid filename
        while os.path.exists(fdst):
            log(' FAILED (file %s exists)' % fd)
            n = n + 1
            fd = frm % (n)
            fdst = os.path.join(op['dstdir'],fd)
        im = img.open(fsrc)
        # calculate size
        (wo,ho) = im.size
        if op['percen']:
            w = int(wo*float(op['width'])/100.0)
            h = int(ho*float(op['height'])/100.0)
        else:
            w = op['width']
            h = op['height']
        log('Processing %s -> %s (%d/%d)' % (fs,fd,m+1,nf))
        im.resize((w,h),img.ANTIALIAS).save(fdst,"JPEG")
        n = n + 1
        m = m + 1
    log('Done. %d files converted.' % m)
    endconv()
        
class ChResGUI:
    def __init__(self,rootwin):
        self.__rootwin = rootwin
        self.__allvalid = False
        self.__w = self.__h = 0
        self.__percen = False
        self.__cancel = False

        # Config parser problem when running from windows start menu.
        # Don´t ask me why ...
        based = os.path.dirname(sys.argv[0])
        if based: # fix for linux when running like 'python chresgui.py'
            os.chdir(based)
            
        self.createGUI()
        
    def createGUI(self):
        self.__rootwin.title("chres " +  CHRESGUI_VERSION)
        if sys.platform == "win32":
            self.__rootwin.wm_iconbitmap('chresgui.ico')
        elif sys.platform == "mac":
            pass # ??? which icon file to use ?
        else:
            self.__rootwin.wm_iconbitmap('@chresgui.xbm')
        
        self.dirfrm = Frame(self.__rootwin) 
        self.dirfrm.pack(side=TOP,expand=YES, fill=BOTH)

        labs = [ 'Source dir', 'Dest dir', 'New resolution', 'New prefix' ]
        txt  = [ '.', '.', '640x480', 'VGA-' ]
        buts = [ '...', '...', ' ? ', ' ? ' ]
        cbks = [ self.selSourceDir, self.selDestDir, self.resHelp, self.prefixHelp ]
        self.var = {}
        self.ctrl = {}

        for n in range(len(labs)):
            lab = labs[n]
            self.var[lab] = StringVar()
            self.var[lab].set(txt[n])
            self.var[lab].trace_variable('w', self.validateEntries)
            Label(self.dirfrm, text=labs[n]+':').grid(row=n,column=0,sticky=W)
            self.ctrl[lab] = Entry(self.dirfrm, textvariable=self.var[lab],width=30)
            self.ctrl[lab].grid(row=n,column=1,sticky=W)
            self.ctrl[lab+'-but'] = Button(self.dirfrm, text=buts[n], command=cbks[n],width=2)
            self.ctrl[lab+'-but'].grid(row=n,column=2,sticky=W)

        self.validateEntries()
        
        self.logfrm = Frame(self.__rootwin) 
        self.logfrm.pack(side=TOP,expand=YES, fill=X)

        self.progress = StringVar()
        self.progress.set('')
        Label(self.logfrm, textvariable=self.progress).grid(row=0,column=0,sticky=W)

        self.butfrm = Frame(self.__rootwin) 
        self.butfrm.pack(side=TOP,expand=YES,fill=X)

        labs = ['About','Cancel','Convert','Close']
        cbks = [self.showAbout,self.cancel,self.convert,self.closeApp]
        for n in range(len(labs)):
            lab = labs[n]+'-but'
            self.ctrl[lab] = Button(self.butfrm, text=labs[n], command=cbks[n], width=10)
            self.ctrl[lab].grid(row=0,column=n)#pack(side=TOP,expand=NO)

        self.ctrl['Cancel-but']['state'] = DISABLED

        self.__rootwin.resizable(width=False,height=False)
        
    def validateEntries(self,*args):
        # should be divided in future for better performance
        self.__allvalid = True
        paths = [ 'Source dir', 'Dest dir']
        for p in paths:
            if(os.path.isdir(self.var[p].get())):
               self.ctrl[p]['background'] = 'lightgrey'
            else:
                self.ctrl[p]['background'] = 'red'
                self.__allvalid = False

        res = self.var['New resolution'].get().strip()
        # eg: 12% or 123x321 are valid entries
        err = False
        if re.compile('^(\d+%{1,1}|\d+x{1,1}\d+)$').match(res):
            n = res.find('%')
            if  n > 0:
                self.__percen = True
                self.__w = self.__h = int(res[0:n])
                if self.__w == 0:
                   err = True
            else:
                self.__percent = False
                v = res.split('x')
                self.__w = int(v[0])
                self.__h = int(v[1])
                if self.__w == 0 or self.__h == 0:
                    err = True
        else:
            err = True
        
        if not err:
               self.ctrl['New resolution']['background'] = 'lightgrey'
        else:
            self.ctrl['New resolution']['background'] = 'red'
            self.__allvalid = False

        pre = self.var['New prefix'].get().strip()
        if re.compile('^[\w\-.]*$').match(pre):
               self.ctrl['New prefix']['background'] = 'lightgrey'
        else:
            self.ctrl['New prefix']['background'] = 'red'
            self.__allvalid = False

    def message(self,txt): self.progress.set(txt)
    def cancel(self): self.__cancel = True
    def checkCancel(self): return self.__cancel
    def endConv(self):
        # threads and tk: what is the better way to go ?
        for k in self.ctrl.keys():
            self.ctrl[k]['state'] = NORMAL
        self.ctrl['Cancel-but']['state'] = DISABLED
        
    def convert(self):
        if not self.__allvalid:
            msg = "Please, there are invalid entry value(s). Fix it(them) before."
            msgbox.showinfo('Invalid entries',msg,parent=self.__rootwin)
            return

        for k in self.ctrl.keys():
            self.ctrl[k]['state'] = DISABLED
        self.ctrl['Cancel-but']['state'] = NORMAL
        self.__cancel = False
        
        self.__tsk = threading.Thread(target=convert_thread,
                                      kwargs={'srcdir':self.var['Source dir'].get(),\
                                              'dstdir':self.var['Dest dir'].get(),\
                                              'prefix':self.var['New prefix'].get(),\
                                              'percen':self.__percen,\
                                              'width':self.__w,\
                                              'height':self.__h,\
                                              'log':self.message,\
                                              'cancel':self.checkCancel, \
                                              'finished':self.endConv})
        self.__tsk.start()

            
    def selSourceDir(self):
        sel = inputbox.askdirectory(title="Source directory",\
                                    initialdir=self.var['Source dir'].get(),\
                                    mustexist=1)
        if sel:
            self.var['Source dir'].set(sel)
        
    def selDestDir(self):
        sel = inputbox.askdirectory(title="Destination directory",\
                                    initialdir=self.var['Dest dir'].get(),\
                                    mustexist=1)
        if sel:
            self.var['Dest dir'].set(sel)

    def closeApp(self):
        self.__rootwin.destroy()
                
    def addMessageQueue(self,event):
        self.progress.set(self.msgQueue.get())

    def prefixHelp(self):
        msg = "Define a prefix to be added to pictures.\n"
        msg = msg + "Only digits, letters, '.', '-' and '_' are allowed. Examples:\n\n"
        msg = msg + "- PICT-\n"
        msg = msg + "- MMM.DD\n"
        msg = msg + "- VGA_\n"
        msgbox.showinfo('Prefix help',msg,parent=self.__rootwin)

    def resHelp(self):
        msg = "You can use percent or fixed resolution when filling this field.\n"
        msg = msg + "Some examples:\n\n"
        msg = msg + "- 25%\n"
        msg = msg + "- 640x480\n"
        msg = msg + "- 130%\n"
        msg = msg + "- 1600x1200\n"
        msgbox.showinfo('Resolution help',msg,parent=self.__rootwin)
        
    def showAbout(self):
        msg = "chres version " + CHRESGUI_VERSION + "\n\n"
        msg = msg + "Copyright (c) 2007-\n"
        msg = msg + "Marcelo Barros de Almeida\n"
        msg = msg + "<marcelobarrosalmeida@gmail.com>\n\n"
        msg = msg + "License:\n"
        msg = msg + "- GPLv2, for non-profit use\n"
        msg = msg + "- For profit use, you must contact the author for discussing licensing model."
        msgbox.showinfo('ChRes',msg,parent=self.__rootwin)

if __name__ == "__main__":
    rootwin= Tk()
    myapp = ChResGUI(rootwin)
    rootwin.mainloop()


