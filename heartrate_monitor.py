
from max30102 import MAX30102
import hrcalc
import threading
import time
import numpy as np
import mysql.connector

class HeartRateMonitor(object):
  
    LOOP_TIME = 0.1

    def __init__(self, print_raw=False, print_result=False):
        self.bpm = 0
        if print_raw is True:
            print('IR, Red')
        self.print_raw = print_raw
        self.print_result = print_result

    def run_sensor(self):
        sensor = MAX30102()
        ir_data = []
        red_data = []
        bpms = []

        while not self._thread.stopped:
            num_bytes = sensor.get_data_present()
            if num_bytes > 0:
                while num_bytes > 0:
                    red, ir = sensor.read_fifo()
                    num_bytes -= 1
                    ir_data.append(ir)
                    red_data.append(red)
                    if self.print_raw:
                        print("{0}, {1}".format(ir, red))

                while len(ir_data) > 100:
                    ir_data.pop(0)
                    red_data.pop(0)

                if len(ir_data) == 100:
                    bpm, valid_bpm, spo2, valid_spo2 = hrcalc.calc_hr_and_spo2(ir_data, red_data)
                    if valid_bpm:
                        bpms.append(bpm)
                        while len(bpms) > 4:
                            bpms.pop(0)
                        self.bpm = np.mean(bpms)
                        if (np.mean(ir_data) < 50000 and np.mean(red_data) < 50000):
                            self.bpm = 0
                            if self.print_result:
                                print("Finger not detected")
                        if self.print_result:
                            mydb = mysql.connector.connect(host="localhost",user="admin",password="beetroot",database="data")
                            
                            if (bpm < 110 and bpm > 40):
                                if (spo2 < 100 and spo2 > 60):
                                    mycursor = mydb.cursor()
                                    sql = "INSERT INTO SensorData (BPM, SP) VALUES (%s,%s)"
                                    val = (bpm, spo2)
                                    mycursor.execute(sql, val)
                                    mydb.commit()

                                    print("BPM: {0}, SpO2: {1}".format(self.bpm, spo2))

        time.sleep(self.LOOP_TIME)

        sensor.shutdown()

    def start_sensor(self):
        self._thread = threading.Thread(target=self.run_sensor)
        self._thread.stopped = False
        self._thread.start()

    def stop_sensor(self, timeout=2.0):
        self._thread.stopped = True
        self.bpm = 0
        self._thread.join(timeout)


