


import LaserCommunication

state_dict = {\
              0: "Boot Fault",
              1: "Warm up",\
              2: "Laser ready for RUN command",\
              3: "Flashing -- lamp disabled",\
              4: "Flashing -- awaiting for shutter to be opened",\
              5: "Flashing -- Pulse enabled",\
              6: "Pulsed Laser ON, NLO warm up",\
              7: "Harmonic generator thermally stabilized",\
              8: "NLO Optimization",\
              9: "APM ok : NLO ready"\
              }

class LaserSettings:
    def __init__(self,admin_mode = False):
        self.lasercommunication = LaserCommunication.LaserCommunication()
        self.admin_mode = admin_mode
        
        ## Get firmware settings
        self.powersupply_ver = self.__get_PSVER()
        self.laserbrain_ver  = self.__get_LVERS()
        
    def get_cooling_temp(self):
        return self.__get_CGTEMP()
        
    def get_state(self,code=True,string=False):
        if code and string:
            out = self.__get_STATE()
            return (out,state_dict[out])
        elif string:
            return self.__get_STATE(string=True)
        else:
            return self.__get_STATE()
            
    def enable_flash(self):
        return self.__FL_RUN()
        
    def disable_flash(self):
        return self.__FL_STOP()
        
    def enable_qsw(self):
        return self.__QS_RUN()
        
    def disable_qsw(self):
        return self.__QS_STOP()
        
    
    def __get(self,command):
        try:
            return self.lasercommunication.send_and_recv("PSVER")
        except:
            raise OSError ## Polish this
        
    def __set(self,command):
        try:
            response = self.lasercommunication.send_and_recv("PSVER")
            if "ERROR" not in response:
                return 0
            else:
                raise IOError ## Polish this
        except:
            raise IOError ## Polish this
            
    ## System commands
    def __get_PSVER(self):
        full_response = self.__get("PSVER")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        version       = float(full_response.split("PSVER = ")[1])
        return version
        
    def __get_LVERS(self):
        full_response = self.__get("LVERS")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        version       = float(full_response.split("LVERS = ")[1])
        return version
        
    def __get_UIVERS(self):
        full_response = self.__get("UIVERS")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        version       = float(full_response.split("UIVERS = ")[1])
        return version
        
    def __get_CGTEMP(self):
        full_response = self.__get("CGTEMP")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        temp       = float(full_response.split("CGTEMP = ")[1])
        return temp
        
    def __get_CHKSERIAL(self):
        full_response = self.__get("CHKSERIAL")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        check       = int(full_response.split("CHKSERIAL = ")[1])
        return check
        
    def __set_CHKSERIAL(self,value):
        response = self.__set(f"CHKSERIAL {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __set_ECHO(self,value):
        response = self.__set(f"ECHO {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    ## State Command
    def __get_STATE(self,as_string = False):
        full_response = self.__get("STATE")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        state       = int(full_response.split("STATE ")[1])
        if as_string:
            return state_dict[state]
        else:
            return state
            
    ## Flashlamp commands
    def __get_CAPVSET(self):
        full_response = self.__get("CAPVSET")
        if "ERROR" in full_response:
            raise Exception ## Flesh this out later
        value       = int(full_response.split("CAPVSET = ")[1])
        return value
        
    def __set_CAPVSET(self,value):
        if self.admin_mode:
            response = self.__set(f"CAPVSET = {value}")
            if response != 0:
                raise IOError ## Flesh this out later
            return response
        else:
            raise RuntimeError("Trying to access a protected function while LaserSettings is not in admin mode.")
           
    def __get_LPW(self):
        full_response = self.__get("LPW")
        if "ERROR" in full_response:
            raise Exception ## Flesh this out later
        value       = int(full_response.split("LPW = ")[1])
        return value
        
    def __set_LPW(self,value):
        if self.admin_mode:
            response = self.__set(f"LPW = {value}")
            if response != 0:
                raise IOError ## Flesh this out later
            return full_response
        else:
            raise RuntimeError("Trying to access a protected function while LaserSettings is not in admin mode.")
            
    def __get_SSHOT(self):
        full_response = self.__get("SSHOT")
        if "ERROR" in full_response:
            raise Exception ## Flesh this out later
        check       = int(full_response.split("SSHOT = ")[1])
        return check
        
    def __get_USHOT(self):
        full_response = self.__get("USHOT")
        if "ERROR" in full_response:
            raise Exception ## Flesh this out later
        value       = int(full_response.split("USHOT = ")[1])
        return value
        
    def __reset_USHOT(self):
        if self.admin_mode:
            response = self.__set(f"USHOT 0")
            if response != 0:
                raise IOError ## Flesh this out later
            return response
        else:
            raise RuntimeError("Trying to access a protected function while LaserSettings is not in admin mode.")
            
    def __set_TRIG(self,flash_internal = True, q_internal=True):
        message = "TRIG "
        if flash_internal:
            message+="I"
        else:
            message+="E"
        if q_internal:
            message+="I"
        else:
            message+="E"
        response = self.__set(f"message")
        if response != 0:
            raise IOError ## Flesh this out later
        return full_response
  
    def __FL_RUN(self):
        response = self.__set(f"RUN")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __FL_STOP(self):
        response = self.__set(f"STOP")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __get_QSPAR1(self):
        full_response = self.__get("QSPAR1")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        check       = int(full_response.split("QSPAR1 = ")[1])
        return check
        
    def __set_QSPAR1(self,value):
        response = self.__set(f"QSPAR1 {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __get_QSPAR2(self):
        full_response = self.__get("QSPAR2")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        check       = int(full_response.split("QSPAR2 = ")[1])
        return check
        
    def __set_QSPAR2(self,value):
        response = self.__set(f"QSPAR2 {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __get_QSPAR3(self):
        full_response = self.__get("QSPAR3")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        check       = int(full_response.split("QSPAR3 = ")[1])
        return check
        
    def __set_QSPAR3(self,value):
        response = self.__set(f"QSPAR3 {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __get_QDLY(self):
        full_response = self.__get("QDLY")
        if "ERROR" in full_response:
            raise Exception ## Flesh this out later
        value       = int(full_response.split("QDLY = ")[1])
        return value
        
    def __set_QDLY(self,value):
        if self.admin_mode:
            response = self.__set(f"QDLY {value}")
            if response != 0:
                raise IOError ## Flesh this out later
            return response
        else:
            raise RuntimeError("Trying to access a protected function while LaserSettings is not in admin mode.")
         
    def __get_QDLYO(self):
        full_response = self.__get("QDLYO")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        check       = int(full_response.split("QDLYO = ")[1])
        return check
        
    def __set_QDLYO(self,value):
        response = self.__set(f"QDLYO {value}")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __QS_RUN(self):
        response = self.__set(f"QSW 1")
        if response != 0:
            raise IOError ## Flesh this out later
        return response
        
    def __QS_STOP(self):
        response = self.__set(f"QSW 0")
        if response != 0:
            raise IOError ## Flesh this out later
        return response