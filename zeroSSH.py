#!/usr/bin/env python

# GUI
import wx

#import Zeroconf

# Bonjour code
import threading
import sys
import os
import bonjour
import select
import struct
import socket

PTR_RECORD_TYPE=12
INTENET_CLASS_TYPE=1
SERVICE_ADD=2
        
class server_list (wx.Frame):
    def __init__ (self,parent,title):
        wx.Frame.__init__(self, parent, title=title, size=(636, 300),
            style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)

        self.zeroconf=zeroListener(self)
	self.hosts={} # used to store hosts.

        frame_panel = wx.Panel(self)
	frame_sizer = wx.BoxSizer(wx.VERTICAL)

        selector_panel = wx.Panel(frame_panel)
        selector_sizer = wx.BoxSizer(wx.HORIZONTAL)

        button_panel = wx.Panel(frame_panel)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dbCBlist={} #[]
        self.db_selector = wx.ListBox (selector_panel, -1)
        
        z=self.db_selector.Append ('ZeroConf / Bonjour')
        self.dbCBlist[z]=[self.zeroConf]
        
        z=self.db_selector.Append ('Bookmarks')
        self.dbCBlist[z]=[self.dbList,'bookmarks.xml']
##        
##        self.db_selector.Append ('History')
##        self.dbCBlist.append([self.dbList,'history.xml'])
##        
##        self.db_selector.Append ('Quick Connect')
##        self.dbCBlist.append([self.quickConnect])
        
        self.db_selector.Bind(wx.EVT_LISTBOX, self.OnDbSelect)
        
        self.host_selector = wx.ListBox (selector_panel, -1)
        self.service_selector = wx.ListBox (selector_panel, -1)

        self.add_button = wx.Button (button_panel,wx.ID_ANY,"+")
        self.del_button = wx.Button (button_panel,wx.ID_ANY,"-")

        selector_sizer.Add(self.db_selector,1,wx.EXPAND)
        selector_sizer.Add(self.host_selector,1,wx.EXPAND)
        selector_sizer.Add(self.service_selector,1,wx.EXPAND)
        selector_panel.SetSizer(selector_sizer)
        selector_panel.Layout()

        button_sizer.Add(self.add_button)
        button_sizer.Add(self.del_button)
        button_panel.SetSizer(button_sizer)
        button_panel.Layout()

        frame_sizer.Add(selector_panel,1,wx.EXPAND)
        frame_sizer.Add(button_panel)
        frame_panel.SetSizer(frame_sizer)
        frame_panel.Layout()

    def quickConnect (self):
	print "Quick Connection"

    def dbList (self, file):
	print file 

    def zeroConf (self): # (wx.Frame):
	#zeroListener(self)
        self.host_selector.Bind(wx.EVT_LISTBOX, self.zeroconf.resolveService)
        self.zeroconf.scanner.start()
        #scanServices()

    def OnDbSelect (self,event):
	selection=self.dbCBlist[self.db_selector.GetSelection()]
        selection[0](*selection[1:])

class zeroListener:
        def __init__ (self, parent):
            self.parent=parent
            self.scanner=threading.Thread(target=self.scanServices)

        def scanServices(self):            
            # Allocate a service discovery ref and browse for the specified service type
            serviceRef = bonjour.AllocateDNSServiceRef()
            ret = bonjour.pyDNSServiceBrowse ( serviceRef,
                                    0,  # no flags
                                    0,  # all network interfaces
                                    "_ssh._tcp",  # meta-query record name
                                    'local.',
                                    self.BrowseCallback,  # callback function ptr
                                    None)
            if ret != bonjour.kDNSServiceErr_NoError:
                print "ret = %d; exiting" % ret
                sys.exit(1)

            # Get socket descriptor and loop
            fd = bonjour.DNSServiceRefSockFD(serviceRef)

            while 1:
                ret=select.select([fd],[],[],1)
                for fd in ret[0]:
	            bonjour.DNSServiceProcessResult(serviceRef)
            bonjour.DNSServiceRefDeallocate(serviceRef)

        def resolveService (self,event):
            serviceName,regtype,replyDomain = self.parent.hosts[self.parent.host_selector.GetSelection()]

            # finds the ip/port:
            sdRef2=bonjour.AllocateDNSServiceRef()
            bonjour.pyDNSServiceResolve(sdRef2,0,0,serviceName,regtype,
                                           replyDomain,self.ResolveCallback,
                                           None)
            bonjour.DNSServiceProcessResult(sdRef2)
           
        def ResolveCallback(self,sdRef,flags,interfaceIndex,errorCode,fullname,
                            hosttarget,port,txtLen,txtRecord,userdata):
            os.execl('./putty.exe','putty.exe',socket.gethostbyname(hosttarget))
            #os.execlp('xterm','xterm','-e',"ssh %s" % socket.gethostbyname(hosttarget))
            #os.execlp('open','Terminal.app',"ssh://%s/" % socket.gethostbyname(hosttarget))

        # Callback for service query
        def BrowseCallback(self,sdRef,flags,interfaceIndex,
                            errorCode,serviceName,regtype,replyDomain,userdata):

            if flags & SERVICE_ADD:
                #print serviceName
                z=self.parent.host_selector.Append(serviceName.decode('utf-8'))
                self.parent.hosts[z]=[serviceName,regtype,replyDomain]

# finds the ip/port:
#                sdRef2=bonjour.AllocateDNSServiceRef()
#                x1=bonjour.pyDNSServiceResolve(sdRef2,0,0,serviceName,regtype,
#                                               replyDomain,self.ResolveCallback,
#                                               None)
#                bonjour.DNSServiceProcessResult(sdRef2)

            elif flags == 0:
                pass#print 'Service name removed:', serviceName

    
        def removeService(self,server,type,name):
            print "Service",repr(name),"removed"

        def addService(self, server, type, name):
            self.host_selector.Append(repr(name))

class zeroSSH (wx.App):
    def OnInit(self):
        frame = server_list(None, "zeroSSH - connection manager")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True

if [ __name__ == '__main__' ]:        
    app = zeroSSH(redirect=True)
    app.MainLoop()

