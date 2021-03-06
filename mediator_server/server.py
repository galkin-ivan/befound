import socket
import threading
import time
import errno
import pickle
import sys
import logging
sys.path.append('../../BeFOUND/Network-settings/')
from network_settings import *
from program_info import *

class ServerMediator:
    """
    Промежуточный сервер, который будет стоять на Raspberry
    Отвечает за прием данных с кнопок и перенаправление посылки локальному
    серверу
    """
    def __init__(self, port, port_to_send, host = "127.0.0.1",
                 host_to_send = "127.0.0.1", socket_timeout = 8):
        """
        Инициализация объекта сервера
        port - порт
        port_to_send - порт, на который требуется переслать посылку
        host - IP сервера нашего
        host_to_send - IP сервера, которому надо отправить посылку
        socket_timeout - таймаут сервера. Отключается тревожная кнопка

        self.__run - запущен ли сервер
        """
        self.port = port
        self.host = host
        self.port_to_send = port_to_send
        self.host_to_send = host_to_send
        self.__socket_timeout = socket_timeout
        self.__run = False

        log = '{0} Server init. ADDRESS: {1}, PORT: {2}'.format(
            SERVER_NAME,
            self.host,
            self.port)
        logging.info(log)
        print(log)
        print("'stop' to stop server"
              "'info' to get info about server")

    def __repr__(self):
        """
        Вывод информации о сервере: порт и IP
        """
        return 'Server(port={}, host={})'.format(self.port, self.host)

    def __create_or_update_socket_to_send(self):
        """
        Создать или обновить сокет для отправки данных локальному серверу
        """
        logging.info("socket create")
        self.__sock_to_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock_to_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                       1)
        self.__sock_to_send.connect((self.host_to_send, self.port_to_send))

    # start listen and send data to local server
    def start_listen_and_send(self):
        """
        Начать прослушку всех пакетов от всех тревожных кнопок
        Обрабатываем исключение EPIPE, когда локальный сервер выключен,
        а отсюда продолжают посылаться данные
        """
        logging.info("listening starts")

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((self.host, self.port))
        self.__sock.settimeout(self.__socket_timeout)

        self.__create_or_update_socket_to_send()

        self.__run = True

        log = "Server started... Socket timeout: {0} sec.".format(
            self.__socket_timeout)
        logging.info(log)
        print(log)

        while self.__run:
            try:
                self.data = self.__sock.recv(1024).decode()
                self.__sock_to_send.send(self.data.encode())

                log_recv = 'Received: <{0}>'.format(self.data)
                logging.info(log_recv)
                print(log_recv)
            except socket.timeout:
                log_ex = 'Socket timeout. Dont pay attention to this message'
                logging.warning(log_ex)
                print(log_ex)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    log_ex = 'Local server rejected connection, because'\
                             'timeout left. Connect again'
                    logging.warning(log_ex)
                    print(log_ex)

                    self.__create_or_update_socket_to_send()

        self.__sock.close()
        self.__sock_to_send.close()
        log = 'Server now is stopped'
        logging.info(log)
        print(log)

    def stop_server(self):
        """
        Остановка сервера
        """
        self.__run = False

        log = 'Server is closing...'
        logging.info(log)
        print(log)


if __name__ == '__main__':
    logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s',
                        level=logging.DEBUG, filename=u'mediator_s.log')

    server = ServerMediator(MEDIATOR_SERVER_PORT, MEDIATOR_SERVER_PORT_TO_SEND,
                            MEDIATOR_SERVER_HOST, MEDIATOR_SERVER_HOST_TO_SEND,
                            MEDIATOR_SERVER_SOCKET_TIMEOUT)
    t = threading.Thread(target=server.start_listen_and_send)
    t.start()

    while True:
        input_msg = input()
        if (input_msg == 'stop'):
            server.stop_server()
            break
        elif (input_msg == 'info'):
            print(repr(server))

    t.join()

    print(CAPTION)
