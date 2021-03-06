# QSmartControl, Copyright Jasper Smits, 2022, released under MIT License

from .LaserCommunication import LaserCommunication
from threading import Thread, Lock
from time import sleep

# It seems an undocumented feature of the laser is that it will turn off when the connection is not kept alive.
# We will just make a "keep alive" thread, and to make sure that it doesn't interfere with other I/O, a mutex to go with it.

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
    def __init__(self,admin_mode = False,ip="169.254.0.1",port=10001,timeout=3,keep_alive=3):
        self.lasercommunication = LaserCommunication(ip,port,timeout)
        self.admin_mode = admin_mode

        # Threading/keep alive stuff
        self.__running = True

        self.mutex = Lock()
        self.keep_alive_time = keep_alive
        self.keep_alive_thread = Thread(target=self.keep_alive_loop)
        self.keep_alive_thread.start()

    def join_keep_alive_thread(self):
        self.__running = False
        self.keep_alive_thread.join()

    def keep_alive_loop(self):
        while self.__running:
            self.status 
            sleep(self.keep_alive_time)

    @property
    def ready_for_flashlamp(self):
        return True if self.state == 2 else False
        # Note that we will probably get a better result here if we look at STATUS, but I don't want to spend time parsing it.

    @property
    def ready_for_qswitch(self):
        return True if self.state == 5 else False
        # Note that we will probably get a better result here if we look at STATUS, but I don't want to spend time parsing it.

    def to_dict(self):
        """Return a description of the object as a dictionary."""
        _dict = dict()

        _dict["cooling_temp"] = self.cooling_temp
        _dict["powersupply_version"] = self.powersupply_version
        _dict["laserbrain_version"] = self.laserbrain_version
        _dict["flashlamp_voltage"] = self.flashlamp_voltage
        _dict["flashlamp_pulse_width"] = self.flashlamp_pulse_width
        _dict["flashlamp_trigger"] = self.flashlamp_trigger
        _dict["qswitch_trigger"] = self.qswitch_trigger
        _dict["mode"] = self.mode
        if self.mode == "Burst":
            _dict["cycles"] = self.__get_QSPAR1()
            _dict["total_length"] = self.__get_QSPAR2()
            _dict["shots"]  = self.__get_QSPAR3()
        elif self.mode == "F/N Mode":
            _dict["divider"] = self.__get_QSPAR2()
        else: #Scan
            _dict["total_length"] = self.__get_QSPAR2()
            _dict["shots"] = self.__get_QSPAR3()
        _dict["qswitch_delay"] = self.qswitch_delay
        _dict["qswitch_sync_delay"] = self.qswitch_sync_delay

        return _dict

    def settings_from_dict(self,_dict,admin=False):
        """Set settings from dict, will not set the "admin" settings unless specified."""

        # Only non-admin thing is the qswitch mode.

        if "qswitch_trigger" in _dict:
            self.qswitch_trigger = _dict["qswitch_trigger"]

        if "flashlamp_trigger" in _dict:
            self.flashlamp_trigger = _dict["flashlamp_trigger"]

        if "mode" in _dict:
            if _dict["mode"] == "Burst":
                try:
                    self.set_mode("Burst", {"cycles": int(_dict["cycles"]), 
                                            "total_length": int(_dict["total_length"]),
                                            "shots": int(_dict["shots"])})
                except:
                    raise ValueError("Error setting mode to Burst, missing parameters. (Required cycles, total_length, shots.)")

            elif _dict["mode"] == "Scan":
                try:
                    self.set_mode("Scan", {"total_length": int(_dict["total_length"]),
                                            "shots": int(_dict["shots"])})
                except:
                    raise ValueError("Error setting mode to Scan, missing parameters. (Required total_length, shots.)")

            elif _dict["mode"] == "F/N Mode":
                try:
                    self.set_mode("F/N Mode", {"divider": int(_dict["divider"])})
                except:
                    raise ValueError("Error setting mode to F/N Mode, missing parameters. (Required divider.)")

        if admin:
            raise Exception("This feature has not yet been implemented.")


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

    @property
    def qsw(self):
        """Status of the qswitch."""
        msg = self.__get("QSW")
        msg = msg.split("QSW = ")[1]
        return bool(int(msg))

    @property
    def cooling_temp(self):
        """Returns the temprature of the cooling water."""
        return self.__get_CGTEMP()
    @property
    def powersupply_version(self):
        """Returns the version of the powersupply."""
        return self.__get_PSVER()

    @property
    def laserbrain_version(self):
        """Return the version of the laser firmware board(?)"""
        return self.__get_LVERS()

    @property
    def state(self):
        """Returns state of the laser as a number."""
        return self.get_state()

    @property
    def state_str(self):
        """Returns state of the laser as a string."""
        return self.get_state(code=False,string=True)


    @property
    def flashlamp_voltage(self):
        """Flash Lamp voltage in V"""
        return self.__get_CAPVSET()

    @flashlamp_voltage.setter
    def flashlamp_voltage(self,voltage):
        if isinstance(voltage,int):
            return self.__set_CAPVSET(voltage)
        else:
            raise ValueError("Value must be an integer.")
   
    @property
    def flashlamp_pulse_width(self):
        """Flash Lamp Pulse Width in us"""
        return self.__get_LPW()

    @flashlamp_pulse_width.setter
    def flashlamp_pulse_width(self,pulse_width):
        if isinstance(pulse_width,int):
            return self.__set_LPW(pulse_width)
        else:
            raise ValueError("Value must be an integer.")
   
    @property
    def flashlamp_shots(self):
        """Number of shots of the flashlamp, system-tracked."""
        return self.__get_SSHOT()

    ### We choose not to implement USHOT (User Shot Tracker) right now, although it could be useful to track the number of shots in a given experiment. I welcome contributions to the project. ;-)

    @property
    def flashlamp_trigger(self):
        """Flashlamp trigger mode."""
        trig = self.__get_TRIG()[0]
        if trig == "I":
            return "Internal"
        else:
            return "External"

    @property
    def qswitch_trigger(self):
        """QSwitch trigger mode."""
        trig = self.__get_TRIG()[1]
        if trig == "I":
            return "Internal"
        else:
            return "External"

    def set_both_triggers(self,flashlamp_trig,qswitch_trig):
        if flashlamp_trig == "Internal":
            fl_int = True
        elif flashlamp_trig == "External":
            fl_int = False
        else:
            ValueError('Value must be "Internal" or "External".')

        if qswitch_trig == "Internal":
            qs_int = True
        elif qswitch_trig == "External":
            qs_int = False
        else:
            ValueError('Value must be "Internal" or "External".')
        
        return self.__set_TRIG(fl_int,qs_int)

    @flashlamp_trigger.setter
    def flashlamp_trigger(self,trig):
        # This is actually quite involved since both triggers are set at once. I will just write a helper code.
        if trig == "Internal" or trig == "External":
            self.set_both_triggers(trig,self.qswitch_trigger)
        else:
            raise ValueError('Value must be "Internal" or "External".')
        
    @qswitch_trigger.setter
    def qswitch_trigger(self,trig):
        # This is actually quite involved since both triggers are set at once. I will just write a helper code.
        if trig == "Internal" or trig == "External":
            self.set_both_triggers(self.flashlamp_trigger,trig)
        else:
            raise ValueError('Value must be "Internal" or "External".')

    ## The QSPAR variables are exposed through system mode (Scan, Burst, F/N).
    ## Note that F/N and Scan are basically the same (Continuous), but since the Q-Touch treats them differently, we will here as well.
    ## We make the following distictions:
    ##  - In Burst Mode when QSPAR1 != 0
    ##  - In F/N mode when QSPAR3 == 1
    ##  - In Scan mode otherwise


    @property
    def mode(self):
        """
        Returns the mode in which the laser is operating;
        The QSPAR variables are exposed through system mode (Scan, Burst, F/N).
        Note that F/N and Scan are basically the same (Continuous), but since the Q-Touch treats them differently, we will here as well.
        We make the following distictions:
        - In Burst Mode when QSPAR1 != 0
        - In F/N mode when QSPAR3 == 1
        - In Scan mode otherwise
        """

        qs1 = self.__get_QSPAR1()
        qs2 = self.__get_QSPAR2()
        qs3 = self.__get_QSPAR3()

        if qs1 != 0:
            return "Burst"
        elif qs3 == 1:
            return "F/N Mode"
        else:
            return "Scan"

    def set_mode(self,mode,**mode_kwargs):
        """
        See also `mode`.

        We can't really set QSPAR1-3 independently with this structure, so we have to set the mode and settings at the same time.

        mode_kwargs:
        Burst:
        - cycles
        - shots per cycle
        - total length of cycle (in base freq)

        Scan:
        - shots per cycle
        - total length of cycle (in base freq)

        F/N:
        - divider
        """
        if mode == "Burst":
            if len(mode_kwargs) != 3:
                raise ValueError("Setting mode to Burst requires 3 options. ('cycles','shots','total_length')")
            if "cycles" not in mode_kwargs:
                raise ValueError("Must set number of cycles ('cycles') in Burst mode.")
            if "shots" not in mode_kwargs:
                raise ValueError("Must set number of shots ('shots') in Burst mode.")
            if "total_length" not in mode_kwargs:
                raise ValueError("Must set total length of cycle ('total_length') in Burst mode.")
            
            cycles       = mode_kwargs["cycles"]
            shots        = mode_kwargs["shots"]
            total_length = mode_kwargs["total_length"]

            if not isinstance(cycles,int):
                raise ValueError("Value must be integer. ('cycles')")
            if not isinstance(shots,int):
                raise ValueError("Value must be integer. ('shots')")
            if not isinstance(total_length,int):
                raise ValueError("Value must be integer. ('total_length')")
            
            idle_shots = total_length-shots

            if idle_shots < 0:
                raise ValueError("Value of 'total_length' must be >= 'shots'.")

            self.__set_QSPAR1(cycles)
            self.__set_QSPAR2(total_length)
            self.__set_QSPAR3(shots)

        elif mode == "F/N Mode":
            if len(mode_kwargs) != 1:
                raise ValueError("Setting mode to F/N requires 1 option. ('divider')")
            if "divider" not in mode_kwargs:
                raise ValueError("Must set number of shots ('divider') in F/N mode.")
            
            divider      = mode_kwargs["divider"]

            if not isinstance(divider,int):
                raise ValueError("Value must be integer. ('shots')")

            if divider < 1:
                raise ValueError("Value of 'divider' must be >= '1'.")

            self.__set_QSPAR1(0)
            self.__set_QSPAR2(divider)
            self.__set_QSPAR3(1)

        elif mode == "Scan":
            if len(mode_kwargs) != 2:
                raise ValueError("Setting mode to Burst requires 2 options. ('shots','total_length')")
            if "shots" not in mode_kwargs:
                raise ValueError("Must set number of shots ('shots') in Burst mode.")
            if "total_length" not in mode_kwargs:
                raise ValueError("Must set total length of cycle ('total_length') in Burst mode.")
            
            shots        = mode_kwargs["shots"]
            total_length = mode_kwargs["total_length"]

            if not isinstance(shots,int):
                raise ValueError("Value must be integer. ('shots')")
            if not isinstance(total_length,int):
                raise ValueError("Value must be integer. ('total_length')")
            
            idle_shots = total_length-shots

            if idle_shots < 0:
                raise ValueError("Value of 'total_length' must be >= 'shots'.")

            self.__set_QSPAR1(0)
            self.__set_QSPAR2(total_length)
            self.__set_QSPAR3(shots)
            pass
        else:
            raise ValueError('Value of "mode" must be "Burst", "F/N Mode" or "Scan".')
   
    @property
    def status(self):
        """Returns the status string."""
        return self.__get_STATUS()

    def transfer_control_to_QTouch(self):
        self.__set("SSWITCH 1")
        del self

    @property
    def qswitch_delay(self):
        """Q-Switch delay in ns"""
        return self.__get_QDLY()

    @qswitch_delay.setter
    def qswitch_delay(self,delay):
        if isinstance(delay,int):
            if delay < 255 and delay >= 0:
                return self.__set_QDLY(delay)
            else:
                raise ValueError("Value must be between 0 and 255.")
        else:
            raise ValueError("Value must be an integer.")

    @property
    def qswitch_sync_delay(self):
        """Q-Switch sync output delay in ns"""
        return self.__get_QDLYO()

    @qswitch_sync_delay.setter
    def qswitch_sync_delay(self,delay):
        if isinstance(delay,int):
            if delay < -500 and delay > 500:
                return self.__set_QDLYO(delay)
            else:
                raise ValueError("Value must be between -500 and 500.")
        else:
            raise ValueError("Value must be an integer.")
    ## Communication commands.
    def __get(self,command):
        try:
            with self.mutex:
                msg = self.lasercommunication.send_and_recv(command)

            return msg
        except:
            raise OSError ## Polish this
        
    def __set(self,command):
        try:
            with self.mutex:
                response = self.lasercommunication.send_and_recv(command)

            if "ERROR" not in response:
                return 0
            else:
                raise IOError ## Polish this
        except:
            raise IOError ## Polish this
    
    
    ## System commands
    def __get_STATUS(self):
        full_response = self.__get("STATUS")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        return full_response

    ## System commands
    def __get_PSVER(self):
        full_response = self.__get("PSVERS")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        version       = float(full_response.split("PSVERS = ")[1])
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
        if self.admin_mode:
            response = self.__set(f"ECHO {value}")
            if response != 0:
                raise IOError ## Flesh this out later
            return response
        else:
            raise RunetimeError("Trying to access a protected function while LaserSettings is not in admin mode.")
        
    ## State Command
    def __get_STATE(self,as_string = False):
        full_response = self.__get("STATE")
        if "ERROR" in full_response:
            raise IOError ## Flesh this out later
        state       = int(full_response.split("STATE = ")[1])
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
    def __get_TRIG(self):
        full_response = self.__get("TRIG")
        if "ERROR" in full_response:
            raise Exception
        return full_response.split("TRIG = ")[1]

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
        response = self.__set(message)
        if response != 0:
            raise IOError ## Flesh this out later
        return response
  
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
