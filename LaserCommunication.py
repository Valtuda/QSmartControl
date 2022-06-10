




class LaserCommunication:
    def __init__(self):
        # Connect to laser
        pass
    
    def __send_message(self,message):
        pass
    
    def __recv_message(self):
        message = "Test response"
        return message
        
    def send_and_recv(self,message):
        self.__send_message(message)
        return self.__recv_message()
    