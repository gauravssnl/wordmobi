# Single or Multiple Selection (For now only single works)
# TODO Multiple Selection
ESingle = 0
EMultiple = 1

# Filetypes
ENoMediaFile = 0
EImageFile = 1
EVideoFile = 2
EAudioFile = 3
ERAMFile = 4
EPlaylistFile = 5
EGMSFile = 6
EMusicFile = 7
EPresentationsFile = 8
EAnyMediaFile = 9

from appuifw import popup_menu

def browse (filetype = EAnyMediaFile, title=None, softkey=None):
    useDefaultTitle = 0
    useDefaultSoftkey = 0
    if title is None:
        useDefaultTitle = 1
        title = u""
    if softkey is None:
        useDefaultSoftkey = 1
        softkey = u""
    filename = popup_menu([u"file_a",u"file_b",u"file_c",u"file_d" ],title)
    return filename
 
