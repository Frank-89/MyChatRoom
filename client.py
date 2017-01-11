#!/usr/bin/python
# encoding: utf-8

import wx
import telnetlib
from time import sleep
import thread


class LoginFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.serverAddressLabel = wx.StaticText(self, label="Server Address", pos=(10, 50), size=(120, 25))
        self.userNameLabel = wx.StaticText(self, label="UserName", pos=(40, 100), size=(120, 25))
        self.serverAddress = wx.TextCtrl(self, pos=(120, 47), size=(150, 25))
        self.userName = wx.TextCtrl(self, pos=(120, 97), size=(150, 25))
        self.loginButton = wx.Button(self, label='Login', pos=(80, 145), size=(130, 30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self, event):
        try:
            serverAddress = self.serverAddress.GetLineText(0).split(':')
            con.open(serverAddress[0], port=int(serverAddress[1]), timeout=10)
            response = con.read_some()
            if response != 'Connect Success':
                self.showDialog('Error', 'Connect Fail!', (95, 20))
                return
            con.write('login ' + str(self.userName.GetLineText(0)) + '\n')
            response = con.read_some()
            if response == 'UserName Empty':
                self.showDialog('Error', 'UserName Empty!', (135, 20))
            elif response == 'UserName Exist':
                self.showDialog('Error', 'UserName Exist!', (135, 20))
            else:
                self.Close()
                ChatFrame(None, -2, title='Chat Client - ' + str(self.userName.GetLineText(0)), size=(600, 400))
        except Exception:
            self.showDialog('Error', 'Connect Fail!', (95, 20))

    def showDialog(self, title, content, size):
        dialog = wx.Dialog(self, title=title, size=size)
        dialog.Center()
        wx.StaticText(dialog, label=content)
        dialog.ShowModal()


class ChatFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(300, 25))
        self.sendButton = wx.Button(self, label="Send", pos=(310, 320), size=(58, 25))
        self.usersButton = wx.Button(self, label="Users", pos=(373, 320), size=(58, 25))
        self.closeButton = wx.Button(self, label="Close", pos=(436, 320), size=(58, 25))
        # show message
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        # show online users
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        # close chat window
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        thread.start_new_thread(self.receive, ())
        self.Show()

    def send(self, event):
        message = str(self.message.GetLineText(0)).strip()
        if message != '':
            con.write('say ' + message + '\n')
            self.message.Clear()

    def lookUsers(self, event):
        con.write('look\n')

    def close(self, event):
        con.write('logout\n')
        con.close()
        self.Close()

    def receive(self):
        while True:
            sleep(0.6)
            result = con.read_very_eager()
            if result != '':
                self.chatFrame.AppendText(result)

if __name__ == '__main__':
    app = wx.App()
    con = telnetlib.Telnet()
    LoginFrame(None, -1, title="Login", size=(280, 200))
    app.MainLoop()
