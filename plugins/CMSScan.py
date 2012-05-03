from burp import IBurpExtender
import re

PATTERNS = {"Wordpress":"/wp-content/plugins/(.*?)/",
            "Joomla":"option=(.*?)&",
            "Drupal":"/modules/(.*?)/"}
PLUGINS = []

class BurpExtender(IBurpExtender):
    def processProxyMessage(self,messageReference, messageIsRequest, remoteHost, remotePort,
                            serviceIsHttps, httpMethod, url, resourceType, statusCode,
                            responseContentType, message, interceptAction):
        if not messageIsRequest:
            if responseContentType != None and responseContentType.find("text/html")>-1:
                for key,value in PATTERNS.items():
                    result = re.findall(value,message.tostring())
                    if len(result) > 0:
                        for plugin in result:
                            if plugin not in PLUGINS:
                                PLUGINS.append(plugin)
                                print "[+] CMSScan: Host:%s  %s plugin detected --> %s" % (remoteHost,key,plugin)
        return message