from burp import IBurpExtender
from burp import IMenuItemHandler
import simplejson as json
from javax.swing import *
from java.awt import *

jsonOffset = "\r\n\r\n{"
menuItemRequest  = "Decode JSON (request)"
menuItemResponse = "Decode JSON (response)"
class BurpExtender(IBurpExtender,IMenuItemHandler):

    def registerExtenderCallbacks(self,IBurpExtenderCallbacks):
        self.__callBacks = IBurpExtenderCallbacks
        self.__callBacks.registerMenuItem("Decode JSON (request)",self)
        self.__callBacks.registerMenuItem("Decode JSON (response)",self)

    def menuItemClicked(self,menuItemCaption,messageInfo):
        if menuItemCaption == menuItemRequest:
            parseJSON(messageInfo[0].request.tostring())
        elif menuItemCaption == menuItemResponse:
            parseJSON(messageInfo[0].response.tostring())

def parseJSON(content):
    offset = content.find(jsonOffset)
    if offset == -1: return
    jsonObj = json.loads(content[offset+len(jsonOffset)-1:])
    jsonObj = json.dumps(jsonObj,ensure_ascii=True,indent=4 * ' ')
    jsonObj = '\n'.join([l.rstrip() for l in  jsonObj.splitlines()])
    showWindow(jsonObj)
    
def showWindow(jsonObj):
    frame = JFrame("jsonViewer",
                              defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                              layout = BorderLayout(),
                              locationRelativeTo = None,
                              size = (400,400))
    scrollPane = JScrollPane(JTextArea(jsonObj,editable=False))
    frame.add(scrollPane)
    frame.show()
    

