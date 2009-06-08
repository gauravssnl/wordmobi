import graphics
import key_codes

try:
    a = key_codes.EButton1Down
except:
    # adding missing key_codes just to avoid tests related
    # to touch enabled or not
    key_codes.EButton1Down=0x101
    key_codes.EButton1Up=0x102
    key_codes.EDrag=0x107
    key_codes.EModifierDoubleClick=0x00080000
    
class CanvasToolbar(object):
    """ Creates a toolbar given a set of square images with same size.
        Toolbar is draw as below:
        
                    IMG_BORDER   MARGIN   
                           |---|---|
            +----------------------+ --
            |                      |  | <-- MARGIN (external margin)
            |   +--------------+   | --
            |   |              |   |  | <-- IMG_BORDER (image border, for drawing selection)
            |   |   +------+   |   | --
            |   |   | ICON |   |   |
            |   |   |      |   |   |
            |   |   +------+   |   | --
            |   |              |   |  | <-- 2*IMG_BORDER
            |   |              |   |  | 
            |   |   +------+   |   | --
            |   |   | ICON |   |   |
            |   |   |      |   |   |
            |   |   +------+   |   |
            |   |              |   |
            |   +--------------+   |
            |                      |
            +----------------------+         
    
    """
    MARGIN = 3
    IMG_BORDER = 2
    def __init__(self,canvas,sel_cbk,redraw_cbk,imgs,position,bg=(255,255,128)):
        """ Created the toolbar object.
            Parameters:
                - canvas (Image): image buffer where toolbar will be drawn
                - sel_cbk (function): callback to be called when an icon is selected toolbar is touched
                - redraw_cbk (function): callback to be called when redrawing is necessary
                - imgs (list of Images): image list with icons
                - position ((int,int)): initial position for drawing the toolbar
                - background color ((int,int,int)): toolbar background color
        """
        self.canvas = canvas
        self.sel_cbk = sel_cbk
        self.redraw_cbk = redraw_cbk
        self.imgs = imgs
        self.position = [position[0],position[1],0,0]
        self.bcolor = bg
        self.img_selected = 0
        self.selected = -1
        self.last_img_selected = -1
        self.visible = False
        self.calc_size()
        self.redraw_cbk()
        
    def calc_size(self):
        """ Using the list of images, calculate toolbar size and selection image
        """
        n = len(self.imgs)
        self.img_size = self.imgs[0].size[0]
        mx = self.img_size + 2*(self.IMG_BORDER + self.MARGIN)
        my = self.img_size*n + 2*(self.IMG_BORDER*n + self.MARGIN)
        self.size = (mx,my)
        self.position[2] = self.position[0] + mx
        self.position[3] = self.position[1] + my
        self.create_sel_img(self.img_size+2*self.IMG_BORDER)

    def create_sel_img(self,sz):
        """ Creates selection image (small square with dashed border)
        """
        self.img_sel = graphics.Image.new((sz,sz))
        self.img_sel.clear(self.bcolor)
        cb = self.bcolor
        cf = (0,0,0)
        c = cb
        step = 7
        for p in range(sz):
            if p%step == 0:
                if c == cb:
                    c = cf
                else:
                    c = cb
            for b in range(self.IMG_BORDER):
                self.img_sel.point((p,b),outline=c)
                self.img_sel.point((p,sz-self.IMG_BORDER+b),outline=c)
                self.img_sel.point((b,p),outline=c)
                self.img_sel.point((sz-self.IMG_BORDER+b,p),outline=c)
                
    def move(self,pos):
        """ Move toolbar to a new position given by pos  (int,int)
        """
        self.position = [pos[0],pos[1],pos[0]+self.size[0],pos[1]+self.size[1]]
        self.redraw_cbk()
        
    def is_visible(self):
        """ Check if toolbar is visible (True) or not (False)
        """
        return self.visible
    
    def is_inside(self,p):
        """ Checks if a given point p (int,int) is inside toolbar area or not
        """
        if p[0] > self.position[0] and \
           p[0] < self.position[2] and \
           p[1] > self.position[1] and \
           p[1] < self.position[3]:
            return True
        else:
            return False
        
    def redraw(self,rect=None):
        """ Redraw the toolbar
        """
        if not self.visible:
            return
        self.canvas.rectangle(self.position,
                              outline = self.bcolor,
                              fill = self.bcolor)
        x = self.position[0] + self.MARGIN + self.IMG_BORDER
        y = self.position[1] + self.MARGIN + self.IMG_BORDER
        for n in range(len(self.imgs)):
            img = self.imgs[n]
            if self.img_selected == n:
                self.canvas.blit(self.img_sel,
                                 target=(x-self.IMG_BORDER,y-self.IMG_BORDER),
                                 source=((0,0),self.img_sel.size))
            self.canvas.blit(img,target=(x,y),source=((0,0),img.size))
            y += self.img_size + 2*self.IMG_BORDER

    def show(self):
        """ Make the toolbar visible
        """
        if not self.visible:
            self.visible = True
            self.img_selected = 0
            self.selected = -1
            self.last_img_selected = -1
        self.redraw_cbk()
                
    def hide(self):
        """ Make the toolbar invisible
        """
        self.visible = False
        self.redraw_cbk()
            
    def next(self):
        """ Move the focus to the next icon
        """
        self.img_selected = (self.img_selected + 1)%len(self.imgs)
        self.redraw_cbk()
        
    def prev(self):
        """ Move the focus to the previous icon
        """
        self.img_selected = (self.img_selected - 1)%len(self.imgs)
        self.redraw_cbk()

    def set_sel(self,pos=None):
        """ Call this function for ensuring the selection.
            For non touch UI, the selection callback is called immediately.
            For touch UI, pos (int,int) argument is used to check if we
            have a selection (typing over an icon with focus)
            or if we are just changing the focus (typing over a new icon)
        """
        if pos:
            n = int((pos[1] - self.MARGIN - self.position[1])/(self.img_size+2*self.IMG_BORDER))
            self.img_selected = min(max(n,0),len(self.imgs)-1)
            if self.img_selected == self.last_img_selected:
                self.selected = self.img_selected
                self.sel_cbk()
            else:
                self.last_img_selected = self.img_selected
            self.redraw_cbk()
        else:
            self.selected = self.img_selected
            self.sel_cbk()          
        
    def get_sel(self):
        """ Return the selected icon or -1 (no selection yet)
        """
        return self.selected

