#!/usr/bin/python
# encoding: utf-8

import asynchat
import socket
import asyncore

# server port
PORT = 6666


class EndSession(Exception):
    pass


class ChatSession(asynchat.async_chat):

    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator('\n')
        self.data = []
        self.name = None
        self.enter(LoginRoom(server))

    # remove oneself from current room and add to another room
    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    # receive data from client
    def collect_incoming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = ''.join(self.data)
        self.data = []
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server))

# handle command class
class CommandHandler:

    def unknown(self, session, cmd):
        session.push('Unknown command: %s\n' % cmd)

    def handle(self, session, line):
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(session, line)
        except TypeError:
            self.unknown(session, cmd)


class Room(CommandHandler):

    def __init__(self, server):
        self.server = server
        self.sessions = []

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)

    def do_logout(self, session, line):
        raise EndSession


class LoginRoom(Room):

    def add(self, session):
        Room.add(self, session)
        session.push('Connect Success')

    def do_login(self, session, line):
        name = line.strip()
        if not name:
            session.push('UserName Empty')
        elif name in self.server.users:
            session.push('UserName Exist')
        else:
            session.name = name
            session.enter(self.server.main_room)


class LogoutRoom(Room):

    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


class ChatRoom(Room):
    # broadcast new user login
    def add(self, session):
        session.push('Login Success')
        self.broadcast(session.name + ' has entered the room.\n')
        self.server.users[session.name] = session
        Room.add(self, session)

    # broadcast user logout 
    def remove(self, session):
        Room.remove(self, session)
        self.broadcast(session.name + ' has left the room.\n')

    def do_say(self, session, line):
        self.broadcast(session.name + ': ' + line + '\n')

    # check online users
    def do_look(self, session, line):
        session.push('Online Users:\n')
        for other in self.sessions:
            session.push(other.name + '\n')


class ChatServer(asyncore.dispatcher):

    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        # create socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        # listen to port
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)


if __name__ == '__main__':
    s = ChatServer(PORT)
    try:
        print("chat serve run at '0.0.0.0:{0}'".format(PORT))
        asyncore.loop()
    except KeyboardInterrupt:
        print("chat server exit")
