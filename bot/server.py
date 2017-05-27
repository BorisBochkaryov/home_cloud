# -*- coding: utf-8 -*-
import socket, hashlib, time
from threading import Thread

class Server:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.freeKeys = list()
        self.busyKeys = list()
        self.sock.bind(('0.0.0.0', 27517))
        self.sock.listen(100)
        thread = Thread(target = self.startListen, args = ())
        thread.start()

    def getKernalInf(self,idchat):
        if [x[0] for x in self.busyKeys if x[2] == idchat] != []:
            [sockClient] = [x[0] for x in self.busyKeys if x[2] == idchat]
            sockClient.send(b'kernalinfo')
            data = sockClient.recv(10240)
            return data
        else:
            return b'error'

    def getList(self,idchat):
        if [x[0] for x in self.busyKeys if x[2] == idchat] != []:
            [sockClient] = [x[0] for x in self.busyKeys if x[2] == idchat]
            sockClient.send(b'list')
            data = sockClient.recv(10240)
            return data
        else:
            return b'error'

    # ожидание клиентов
    def startListen(self):
        while 1:
            conn, addr = self.sock.accept()
            thread = Thread(target = self.workWithHome, args = ( conn, addr ))
            thread.start()

    # работа с "облаком"
    def workWithHome(self, client, addr):
        data = client.recv(10240)
        print(b'From home: ' + data)
        if not data:
            return
        elif data == b'hello':
            print('Пользователь запросил ключ')
            # проверка на то, что сокет не имеет ключ
            if [ client in (x[0] for x in self.freeKeys) ] == [ False ]:
                youKey = self.genKey()
                print('Пользователем получен ключ', youKey)
                client.send(b'youkey ' + youKey)
                self.freeKeys.append([client, youKey])
                print(self.freeKeys)
        else:
            # если пришел ключ
            if [x for x in self.busyKeys if x[1] == data] != []:
                print('Пользователь имеет ключ')
                [clientList] = [x for x in self.busyKeys if x[1] == data]
                index = self.busyKeys.index(clientList)
                del self.busyKeys[index]
                self.busyKeys.append([client, data, clientList[2]])
                print(self.busyKeys)
                client.send(b'successful')
            else:
                # ключ не найден
                print('Пользователь прибыл без ключа')
                youKey = self.genKey()
                client.send(b'clear ' + youKey)

    # отправка файла от пользователя
    def getFile(self, nameFile, idChat):
        if [x[0] for x in self.busyKeys if x[2] == idChat] != []:
            [sockClient] = [x[0] for x in self.busyKeys if x[2] == idChat]
            sockClient.send(b'getf ' + nameFile.encode())
            data = sockClient.recv(10240)
            return data
        else:
            return b'error'

    # сохранение ключа доступа
    def saveKey(self, key, idChat):
        if [ key in (x[1] for x in self.freeKeys) ] == [ True ]:
            [sockClient] = [x[0] for x in self.freeKeys if x[1] == key]
            index = self.freeKeys.index([sockClient, key])
            del self.freeKeys[index]
            self.busyKeys.append([sockClient, key, idChat])
            return "ok"
        else:
            return "not found"

    # получение ключа для пользователя
    def genKey(self):
        return str.encode(hashlib.md5(str(time.time()).encode('utf-8')).hexdigest())

    def close(self):
        self.socket.close()

    # отправка файла в Home
    def sendFile(self, idChat, file, nameFile, sizeFile):
        [sockClient] = [x[0] for x in self.busyKeys if x[2] == idChat]
        sockClient.send(b'sendf ' + str.encode(nameFile))
        time.sleep(0.1)
        sockClient.send(str.encode(str(sizeFile)))
        time.sleep(0.1)
        sockClient.send(file)


if __name__ == "__main__":
    server = Server()
