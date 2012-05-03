from burp import IBurpExtender
from burp import IMenuItemHandler
from javax.swing import *
from java.awt import *
import sys
import os
import string
#add plugins path
PLUGINSPATH = os.path.join(os.getcwd(),"plugins")
CONFIGPATH  = os.path.join(PLUGINSPATH,"config.txt")
sys.path.append(PLUGINSPATH)


class BurpExtender(IBurpExtender,IMenuItemHandler):

    def __init__(self):
        self.__callBacks = None
        self.__frame = None
        self.__table = None
        self.__plugins = {}
        self.loadPlugins()
        self.createMenu()        
    
    def processProxyMessage(self,messageReference, messageIsRequest, remoteHost, remotePort,
                            serviceIsHttps, httpMethod, url, resourceType, statusCode,
                            responseContentType, message, interceptAction):
        for plugin in self.__plugins.values():
            if plugin.isActive():
                plugin.object.processProxyMessage(messageReference,
                                                      messageIsRequest,
                                                      remoteHost,
                                                      remotePort,
                                                      serviceIsHttps,
                                                      httpMethod,
                                                      url,
                                                      resourceType,
                                                      statusCode,
                                                      responseContentType,
                                                      message,
                                                      interceptAction
                                                      )

        return message

    def processHttpMessage(self,toolName,messageIsRequest,messageInfo):
        for plugin in self.__plugins.values():
            if plugin.isActive():
                plugin.object.processHttpMessage(toolName,messageIsRequest,messageInfo)
                
    def registerExtenderCallbacks(self,IBurpExtenderCallbacks):
        self.__callBacks = IBurpExtenderCallbacks
        self.__callBacks.registerMenuItem("Plugins Manager",self)
        map(lambda plugin: plugin.object.registerExtenderCallbacks(IBurpExtenderCallbacks),self.__plugins.values())
        
    def newScanIssue(self,issue):
        for plugin in self.__plugins.values():
            if plugin.isActive():
                plugin.object.newScanIssue(issue)

    def setCommandLineArgs(self,args):
        map(lambda plugin: plugin.object.setCommandLineArgs(args),self.__plugins.values())
    
    def applicationClosing(self):
        for plugin in self.__plugins.values():
            if plugin.isActive():
                plugin.object.applicationClosing()

            
    def loadPlugins(self):
        print "[+] Loading plugins..."
        try:
            config = file(CONFIGPATH,'r')
        except IOError:
            print "[-] There is no configuration file : %s" % CONFIGPATH
            return
        for line in config:
            if line[0] == "#":
                continue #leave comment line
            line = map(string.strip,line.split(","))
            print "[+] %s plugin found. State: %s" % (line[0],line[1])
            self.__plugins[line[0]] = Plugin(line[0],line[1])
        del config
        

    def createMenu(self):
        self.__frame = JFrame("Plugins Manager",
                              defaultCloseOperation = JFrame.DISPOSE_ON_CLOSE,
                              layout = BorderLayout(),
                              locationRelativeTo = None)
        panel = JPanel()
        plugins = [[plugin.getName(),plugin.getState()] for plugin in self.__plugins.values()]
        self.__table = JTable(plugins,["Plugin Name","State"])
        scroll = JScrollPane(self.__table)
        panel.add(scroll)
        self.__frame.add(panel,BorderLayout.NORTH)
        panel2 = JPanel(FlowLayout())
        self.__frame.add(panel2,BorderLayout.SOUTH)
        panel2.add(JButton("Reload",actionPerformed=self.onReload))
        panel2.add(JButton("Change state",actionPerformed=self.onChangeState))
        self.__frame.pack()        
            
    def menuItemClicked(self,menuItemCaption,messageInfo):
        if menuItemCaption == "Plugins Manager":
            self.__frame.show()
        print menuItemCaption

    def onReload(self,event):
        row = self.__table.getSelectedRow()
        if  row != -1:
            model = self.__table.getModel()
            self.__plugins[model.getValueAt(row,0)].reload()
                
    def onChangeState(self,event):
        row = self.__table.getSelectedRow()
        if  row != -1:
            model = self.__table.getModel()
            state = self.changeState(model.getValueAt(row,1)) #State column
            model.setValueAt(state,row,1)
            self.__plugins[model.getValueAt(row,0)].setState(state)

    def changeState(self,state):
        if state == "1": return "0"
        return "1"

class Plugin():
    def __init__(self,name,state):
        self.__name = name
        self.__state  = state
        self.__module = __import__(name)
        self.__object = self.__module.BurpExtender()

    def getName(self):
        return self.__name
    
    def isActive(self):
        return self.__state == "1"

    def setState(self,state):
        self.__state = state

    def getState(self):
        return self.__state

    @property
    def object(self):
        return self.__object

    def reload(self):
        print "[+] Reloading module : %s" % self.__name
        self.__module = reload(self.__module)
        self.__object = self.__module.BurpExtender()

        



