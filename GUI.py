from Tkinter import *
import time
import RPi.GPIO as GPIO
import cv2
import numpy as np
import picamera

GPIO.setmode(GPIO.BCM)
#encoder
clk = 18
dt = 23
zero = 24
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(zero, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#motor
motor1 = 2
motor2 = 3
enable = 4
GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)
GPIO.setup(enable, GPIO.OUT)
pwm = GPIO.PWM(enable, 50)
#led
led = 9
GPIO.setup(led, GPIO.OUT)
#vakumpump
pump = 22
GPIO.setup(pump, GPIO.OUT)
#servo
servo1 = 27 #lock
servo2 = 17 #lyft
GPIO.setup(servo1, GPIO.OUT)
servoPwm = GPIO.PWM(servo1, 100)
GPIO.setup(servo2, GPIO.OUT)
servoPwm2 = GPIO.PWM(servo2, 500)
#Kamera
camera = picamera.PiCamera()

class Medicine:
    def __init__(self, color,amount,used,position):
        self.color=color
        self.amount=amount
        self.used=used
        self.position=position
        
class scheduledMed:
    def __init__(self, Medicine, day, time, state):
        self.Medicine=Medicine
        self.day=day
        self.time=time
        self.state=state
        
def pressInput():
    temp = time.ctime().split()
    time0 = temp[3]
    time1=time0.split(":")  
    global uptime
    uptime = int(str(time1[0])+str(time1[1])+str(time1[2]))
    
    testColor = e1.get()
    testAmount = e2.get()
    if not testColor.isdigit() and testAmount.isdigit() and int(testAmount) > 0 and int(testAmount) < 10 and len(listMed)<=6:
        check = 0
        index = 0
        for i in range(0,len(listMed)):
            if testColor == listMed[i].color:
                check = 1
                index = i
        if check==1:
            if (listMed[index].amount+int(testAmount)) < 9:
                #listMed[index].amount = str(int(listMed[index].amount) + int(testAmount))
                listMed[index].amount=listMed[index].amount + int(testAmount)
                lb1.delete(index)
                lb1.insert(index, listMed[index].color + "-----" + str(listMed[index].amount) + "--(" + str(listMed[index].used) + ")")
                moveTo(listMed[index].position + 1024)
            else:
                print "Can't handle more han 8 pills"
                print
        else:
            temp = Medicine(testColor,int(testAmount),0,(len(listMed)*256)+160)
            listMed.append(temp)
            lb1.insert(len(listMed), temp.color + "-----" + str(temp.amount) + "--(" + str(temp.used) + ")")
            moveTo(temp.position + 1024)
        e1.delete(0,END)
        e2.delete(0,END)        
    else:
        print "First box needs to be text, and second needs to be number bigger than 0 and smaller than 10. Can't handle more than 6 types of medicine"
        print
        
def pressOutput():
    temp = time.ctime().split()
    time0 = temp[3]
    time1=time0.split(":")  
    global uptime
    uptime = int(str(time1[0])+str(time1[1])+str(time1[2]))
    
    testMedicine = lb1.curselection()
    testDay = e3.get()
    testTime = e4.get()
    if (testDay == "monday" or testDay == "Monday" or testDay == "tuesday" or testDay == "Tuesday" or testDay == "wednesday" or testDay == "Wednesday" or testDay == "thursday" or testDay == "Thursday" or testDay == "friday" or testDay == "Friday" or testDay == "saturday" or testDay == "Saturday" or testDay == "sunday" or testDay == "Sunday") and testTime.isdigit() and int(testTime) < 2400 and int(testTime) > 0 and ((int(testTime)%100)<60) and len(listMed)>0 and len(testMedicine)>0 and len(str(testTime))==4:
        temp = int(testTime)%100
        if temp < 10:
           temp = "0"+str(temp)         
        if listMed[testMedicine[0]].used + 1 > listMed[testMedicine[0]].amount :
            print "Can't schedule more of that pill"
            print
        else:
            scheduled = scheduledMed(listMed[testMedicine[0]],testDay,int(testTime),0)
            listSchedule.append(scheduled)
            lb2.insert(len(listSchedule),listMed[testMedicine[0]].color + "---" + testDay + " at " + str(int(testTime)/100) + ":" + str(temp))                                      
            listMed[testMedicine[0]].used = listMed[testMedicine[0]].used + 1
            lb1.delete(testMedicine[0])
            lb1.insert(testMedicine[0],listMed[testMedicine[0]].color + "-----" + str(listMed[testMedicine[0]].amount) + "--(" + str(listMed[testMedicine[0]].used) + ")")           
            e3.delete(0,END)
            e4.delete(0,END)
    else:
        print "A medicine needs to be marked, first box needs to be a weekday, second box needs to be a number less than 2400, greater than 0 and have 4 digits"
        print

def pressRemove():
    temp = time.ctime().split()
    time0 = temp[3]
    time1=time0.split(":")  
    global uptime
    uptime = int(str(time1[0])+str(time1[1])+str(time1[2]))
    
    removeMedicine = lb2.curselection()
    if len(removeMedicine)>0:   
        index = removeMedicine[0]
        for i in range(0,len(listMed)):
            if listMed[i].color == listSchedule[index].Medicine.color:
                listMed[i].used = listMed[i].used-1
                lb1.delete(i)
                lb1.insert(i,listMed[i].color + "-----" + str(listMed[i].amount) + "--(" + str(listMed[i].used) + ")")  
        del listSchedule[index]
        lb2.delete(index)        
        
def pressGet():
    temp = time.ctime().split()
    day = temp[0]
    time0 = temp[3]
    time1=time0.split(":")
    time2=str(time1[0])+str(time1[1])    
    realTime =int(time2)
    for i in range(0,len(listSchedule)):
        check = 0
        n = 0
        for index in range(0,len(listMed)):
            if listSchedule[i].Medicine.color == listMed[index].color:
                if check == 0:
                    n = index
                    check = 1
                    
        t1 = listSchedule[i].time+3
        t2 = 60 - ((listSchedule[i].time+3)%100)
        if t1%100 > 59:
            if (t1/100)+1 >23:
                t1 = abs(t2)
            else:
                t1 = ((t1//100)+1)*100 + abs(t2)
        
        
        if t1 < 3:
            if (listSchedule[i].day=="Monday" or listSchedule[i].day=="monday") and (day=="Mon" or day == "Tue"):
                if (day == "Mon" and listSchedule[i].time <= realTime) or (day == "Tue" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"            
                        ledStop()
                        #moveTo(listMed[n].position)
                        #lyftServo(ner)
                        #pumpStart()
                        #lyftServo(upp)
                        #cameraVerifiering
                        #outputPos()
                        #lyftServo(ner)
                        #pumpStop()
                        #lyftServo(upp)
                        
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
            
            elif (listSchedule[i].day=="Tuesday" or listSchedule[i].day=="tuesday") and (day=="Tue" or day == "Wed"):
                if (day == "Tue" and listSchedule[i].time <= realTime) or (day == "Wed" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
                    
            elif (listSchedule[i].day=="Wednesday" or listSchedule[i].day=="wednesday") and (day=="Wed" or day == "Thu"):
                if (day == "Wed" and listSchedule[i].time <= realTime) or (day == "Thu" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
                    
            elif (listSchedule[i].day=="Thursday" or listSchedule[i].day=="thursday") and (day=="Thu" or day == "Fri"):
                if (day == "Thu" and listSchedule[i].time <= realTime) or (day == "Fri" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
                    
            elif (listSchedule[i].day=="Friday" or listSchedule[i].day=="friday") and (day=="Fri" or day == "Sat"):
                if (day == "Fri" and listSchedule[i].time <= realTime) or (day == "Sat" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
                        
            elif (listSchedule[i].day=="Saturday" or listSchedule[i].day=="saturday") and (day=="Sat" or day == "Sun"):
                if (day == "Sat" and listSchedule[i].time <= realTime) or (day == "Sun" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print
                        
            elif (listSchedule[i].day=="Sunday" or listSchedule[i].day=="sunday") and (day=="Sun" or day == "Mon"):
                if (day == "Sun" and listSchedule[i].time <= realTime) or (day == "Mon" and t1 > realTime):
                    if listSchedule[i].state==0:
                        listSchedule[i].state = 1 
                        #listMed[n].used = listMed[n].used-1
                        listMed[n].amount = int(listMed[n].amount)-1
                        lb1.delete(n)
                        lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                        print "Got pills"
                        ledStop()
                        if listMed[n].amount < listMed[n].used:
                            print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                            print 
                        
        
        elif ((listSchedule[i].day=="Monday") or (listSchedule[i].day=="monday")) and day=="Mon":
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1 
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = int(listMed[n].amount)-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print            
        
        elif ((listSchedule[i].day=="Tuesday") or (listSchedule[i].day=="tuesday")) and day=="Tue":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
            
        elif ((listSchedule[i].day=="Wednesday") or (listSchedule[i].day=="wednesday")) and day=="Wed":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
                
        elif ((listSchedule[i].day=="Thursday") or (listSchedule[i].day=="thursday")) and day=="Thu":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
                
        elif ((listSchedule[i].day=="Friday") or (listSchedule[i].day=="friday")) and day=="Fri":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
                
        elif ((listSchedule[i].day=="Saturday") or (listSchedule[i].day=="saturday")) and day=="Sat":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
                
        elif ((listSchedule[i].day=="Sunday") or (listSchedule[i].day=="sunday")) and day=="Sun":           
            if listSchedule[i].time <= realTime and t1 > realTime and listSchedule[i].state==0:
                listSchedule[i].state = 1
                #listMed[n].used = listMed[n].used-1
                listMed[n].amount = listMed[n].amount-1
                lb1.delete(n)
                lb1.insert(n,listMed[n].color + "-----" + str(listMed[n].amount) + "--(" + str(listMed[n].used) + ")")
                print "Got pills"
                ledStop()
                if listMed[n].amount < listMed[n].used:
                    print "There is less pills available than pills scheduled, please refill pill: " + listMed[n].color
                    print
        b4.configure(bg="#d3d3d3")

def checkOutput():
    temp = time.ctime().split()
    day = temp[0]
    time0 = temp[3]
    time1=time0.split(":")
    time2=str(time1[0])+str(time1[1])
    realTime =int(time2)    

    for i in range(0,len(listSchedule)):
        check = 0
        n = 0
        for index in range(0,len(listMed)):
            if listSchedule[i].Medicine.color == listMed[index].color:
                if check == 0:
                    n = index
                    check = 1
                    
        t1 = listSchedule[i].time+3
        t2 = 60 - ((listSchedule[i].time+3)%100)
        if t1%100 > 59:
            if (t1/100)+1 >23:
                t1 = abs(t2)
            else:
                t1 = ((t1//100)+1)*100 + abs(t2)           
        
        if t1 < 3:
            if (listSchedule[i].day=="Monday" or listSchedule[i].day=="monday") and (day=="Mon" or day == "Tue"):
                if (day == "Mon" and listSchedule[i].time <= realTime) or (day == "Tue" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print    
            
            elif (listSchedule[i].day=="Tuesday" or listSchedule[i].day=="tuesday") and (day=="Tue" or day == "Wed"):
                if (day == "Tue" and listSchedule[i].time <= realTime) or (day == "Wed" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
                    
            elif (listSchedule[i].day=="Wednesday" or listSchedule[i].day=="wednesday") and (day=="Wed" or day == "Thu"):
                if (day == "Wed" and listSchedule[i].time <= realTime) or (day == "Thu" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
                    
            elif (listSchedule[i].day=="Thursday" or listSchedule[i].day=="thursday") and (day=="Thu" or day == "Fri"):
                if (day == "Thu" and listSchedule[i].time <= realTime) or (day == "Fri" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
                    
            elif (listSchedule[i].day=="Friday" or listSchedule[i].day=="friday") and (day=="Fri" or day == "Sat"):
                if (day == "Fri" and listSchedule[i].time <= realTime) or (day == "Sat" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
                        
            elif (listSchedule[i].day=="Saturday" or listSchedule[i].day=="saturday") and (day=="Sat" or day == "Sun"):
                if (day == "Sat" and listSchedule[i].time <= realTime) or (day == "Sun" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
                        
            elif (listSchedule[i].day=="Sunday" or listSchedule[i].day=="sunday") and (day=="Sun" or day == "Mon"):
                if (day == "Sun" and listSchedule[i].time <= realTime) or (day == "Mon" and t1 > realTime):
                    if listSchedule[i].state==0 and listMed[n].amount > 0:
                        b4.configure(bg="red")
                        print "Output " + listSchedule[i].Medicine.color
                        ledStart()
                    elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                        listSchedule[i].state = 1
                        print "Pill: " + listMed[n].color + ", not available!"
                        print
        
        elif ((listSchedule[i].day=="Monday") or (listSchedule[i].day=="monday")) and day=="Mon":
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
        
        elif ((listSchedule[i].day=="Tuesday") or (listSchedule[i].day=="tuesday")) and day=="Tue":           
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")             
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0: 
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
            
        elif ((listSchedule[i].day=="Wednesday") or (listSchedule[i].day=="wednesday")) and day=="Wed":
            if listSchedule[i].time <= realTime and t1 > realTime:               
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")             
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
                
        elif ((listSchedule[i].day=="Thursday") or (listSchedule[i].day=="thursday")) and day=="Thu":           
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
                
        elif ((listSchedule[i].day=="Friday") or (listSchedule[i].day=="friday")) and day=="Fri":           
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0: 
                    b4.configure(bg="red")
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
                
        elif ((listSchedule[i].day=="Saturday") or (listSchedule[i].day=="saturday")) and day=="Sat":           
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
                
        elif ((listSchedule[i].day=="Sunday") or (listSchedule[i].day=="sunday")) and day=="Sun":           
            if listSchedule[i].time <= realTime and t1 > realTime:
                if listSchedule[i].state == 0 and listMed[n].amount > 0:
                    b4.configure(bg="red")
                    print "Output " + listSchedule[i].Medicine.color
                    ledStart()
                elif listMed[n].amount == 0 and listSchedule[i].state == 0:
                    listSchedule[i].state = 1
                    print "Pill: " + listMed[n].color + ", not available!"
                    print
       
def resetState():
    temp = time.ctime().split()
    time0 = temp[3]
    time1=time0.split(":")
    realTime0=str(time1[0])+str(time1[1])
    if realTime0 == "0000":
        for i in range(0,len(listSchedule)):
            listSchedule[i].state = 0
            
def logIn():   
    username = e5.get()
    password = e6.get()
    e5.delete(0,END)
    e6.delete(0,END)
    if logCombo(username, password) == 1:
        enable()
        temp = time.ctime().split()
        time0 = temp[3]
        time1=time0.split(":")
        global uptime
        uptime = int(str(time1[0])+str(time1[1])+str(time1[2]))
    else:
        print "Wrong username or password"

#Disables functions not suitable for patient
def disable():
    e1.configure(state=DISABLED)
    e2.configure(state=DISABLED)
    e3.configure(state=DISABLED)
    e4.configure(state=DISABLED)
    b1.configure(state=DISABLED)
    b2.configure(state=DISABLED)
    b3.configure(state=DISABLED)

#Enables functions
def enable():
    e1.configure(state=NORMAL)
    e2.configure(state=NORMAL)
    e3.configure(state=NORMAL)
    e4.configure(state=NORMAL)
    b1.configure(state=NORMAL)
    b2.configure(state=NORMAL)
    b3.configure(state=NORMAL)

#Possible login combinations
def logCombo(usr,psw):
    if usr == "username" and psw == "password":
        return 1
    elif usr == "henk" and psw == "benk":
        return 1
    elif usr == "wienerbrodinator" and psw == "kalaspuff":
        return 1
    elif usr == "karljan" and psw == "pearsson":
        return 1
    else:
        return 0
    
#Last active checker    
def checkUptime():
    temp = time.ctime().split()
    time0 = temp[3]
    time1=time0.split(":")
    realtime = str(time1[0])+str(time1[1])+str(time1[2])
    temp = uptime +100
    if (temp%10000) > 5959:
        if (temp/10000)+1>23:
            temp = "00" + "00" + str(int(temp)%100)
        else:
            temp = str(temp/10000) + "00" + str(int(temp)%100)
    else:        
        temp = str(temp/10000) + str((temp%10000)/100) + str(int(temp)%100)
           
    if temp == realtime:
        disable()
#Encoder Functions
def checkEncoder():
    global clkState
    clkState = GPIO.input(clk)
    global dtState
    dtState = GPIO.input(dt)
    global zeroState
    zeroState = GPIO.input(zero)
    if zeroState == 0:
        global counter
        counter = 0
    if clkState != clkLastState:
        if dtState != clkState:
            global counter
            counter -= 1
        else:
            global counter
            counter += 1
        #print counter
##        print str(clkState)
##        print " " + str(dtState)
##        print "  " + str(zeroState)
        
##            temp = counter
##            check = 1                        
##        
    global clkLastState
    clkLastState = clkState   
  
def moveTo(pos):
    print "Please wait!"
    while counter != pos:
        motor()
        checkEncoder()
    motorStop()        
    print "Done!"
    
def resetPos():
    print "Please wait!"
    startPos()
    time.sleep(0.2)
    while counter != 224:
        motor() 
        checkEncoder()           
    motorStop()
    print "Done!"

def startPos():
    while zeroState != 0:
        motor() 
        checkEncoder()
    motorStop()
    checkEncoder()        
    time.sleep(0.2)

def outputPos():
    print "Please wait!"
    time.sleep(0.2)
    while counter != 1900:
        motor()
        checkEncoder()
    motorStop()        
    print "Done!"

#Motor Functions
def motor():
    GPIO.output(motor1,0)
    GPIO.output(motor2,1)
def motorRev():
    GPIO.output(motor1,1)
    GPIO.output(motor2,0)
def motorStop():
    GPIO.output(motor1,0)
    GPIO.output(motor2,0)

#Led Functions
def ledStart():
    GPIO.output(led,1)    
def ledStop():
    GPIO.output(led,0)

#Pump Functions
def pumpStart():
    GPIO.output(pump,0)
def pumpStop():
    GPIO.output(pump,1)
    
#InputServo Functions
def servoOpen():
    servoPwm.ChangeDutyCycle(17)
    time.sleep(0.1)    
def servoClose():
    servoPwm.ChangeDutyCycle(9)
    time.sleep(0.1)
    
#LiftServo Functions
def servoDown(nr):
    while servoPos != nr:
        global servoPos
        servoPos = servoPos -1
        servoPwm2.ChangeDutyCycle(servoPos)
        time.sleep(0.05)                  
def servoUp():
    while servoPos != 92:
        global servoPos
        servoPos = servoPos +1
        servoPwm2.ChangeDutyCycle(servoPos)
        time.sleep(0.05)
        
#Camera Functions        
def takePicture():
    camera.capture("ImageTest" + str(num) + ".jpg")
    image = cv2.imread("ImageTest" + str(num) + ".jpg")    
    color = image[600,960]
    b,g,r = color
    print
    print "ImageTest" + str(num) + ".jpg"
    print "red " + str(r)
    print "green " + str(g)
    print "blue " + str(b)
    print ""
    global num
    num = num +1

def pickUp(pipe,nr):
    time.sleep(0.5)           
    moveTo(pipe)
    servoDown(nr)
    pumpStart()
    servoUp()
    takePicture()
    outputPos()
    servoDown(18)
    pumpStop()
    servoUp()
    time.sleep(2)
    
root = Tk()
frame = Frame(root.wm_title('test GUI'))
frame.pack()
root.geometry("715x500+0+0")

listMed=[]
listSchedule=[]

lb1 = Listbox()
lb1.place(height=150, width=200, x= 10, y=20)
lb2 = Listbox()
lb2.place(height=290,width=270,x=220,y=200)

yscroll = Scrollbar(command=lb2.yview, orient=VERTICAL)
yscroll.place(x=480,y=201,width=10, height=289)
lb2.configure(yscrollcommand=yscroll.set)

#Entry fields
e1 = Entry()
e1.place(x=220,y=20)
e2 = Entry()
e2.place(x=220,y=50)
e3 = Entry()
e3.place(x=10,y=200)
e4 = Entry()
e4.place(x=10,y=260)

#Buttons
b1 = Button(text="Add medicine", command = pressInput)
b1.place(height=50, width=105, x=380, y=20)
b2 = Button(text="Add schedule", command = pressOutput)
b2.place(height=50, width=105, x=33, y=290)
b3 = Button(text="Remove Schedule", command = pressRemove)
b3.place(height=50, width=105, x=380, y=147)
b4 = Button(text="Get Med", command = pressGet)
b4.place(height=50, width=105, x=10, y=440)

#Labels
l1=Label(text="DAY (Monday-Sunday)")
l2=Label(text="TIME (hhmm)")
l3=Label(text="MEDICINE")
l4=Label(text="INPUT: MEDICINE / AMOUNT")
l5=Label(text="SCHEDULED OUTPUTS")
l1.place(x=10,y=180)
l2.place(x=10,y=240)
l3.place(x=10,y=2)
l4.place(x=220,y=2)
l5.place(x=220,y=180)

#Step-by-step instrucion labels
l6=Label(text="Import medicine", bg="yellow")
l7=Label(text="Enter name of medicine")
l8=Label(text="Enter amount of pills, 1-10")
l82=Label(text="Press 'Add medicine' button")
l6.place(x=510,y=10)
l7.place(x=510,y=30)
l8.place(x=510,y=50)
l82.place(x=510,y=70)
l9=Label(text="Schedule medicine", bg="yellow")
l10=Label(text="Enter weekday, Monday-Sunday")
l11=Label(text="Enter time of day, 0000-2359")
l12=Label(text="Mark wanted medicine")
l122=Label(text="Press 'Add schedule' button")
l9.place(x=510,y=100)
l10.place(x=510,y=120)
l11.place(x=510,y=140)
l12.place(x=510,y=160)
l122.place(x=510,y=180)
l13=Label(text="Get scheduled medicine", bg="yellow")
l14=Label(text="Press 'Get Med' button when ")
l15=Label(text="alarms are flashing")
l13.place(x=510,y=210)
l14.place(x=510,y=230)
l15.place(x=510,y=250)
l16=Label(text="Remove scheduled medicine", bg="yellow")
l17=Label(text="Mark scheduled medicine")
l18=Label(text="to be removed")
l19=Label(text="Press 'Remove Scheduled' button")
l16.place(x=510,y=280)
l17.place(x=510,y=300)
l18.place(x=510,y=320)
l19.place(x=510,y=340)

#Loggin stuff
l20 = Label(text="Login", bg="yellow")
l21 = Label(text="Username/Password")
e5 = Entry()
e6 = Entry(root, show="*")
b5 =Button(text ="Log In", command = logIn)
l20.place(x=510,y=380)
l21.place(x=550,y=380)
e5.place(x=510,y=400)
e6.place(x=510,y=430)
b5.place(height=30, width=60, x=595, y=460)

global uptime
uptime = 0

global counter
counter = 0

global clkState
clkState = GPIO.input(clk)

global dtState
dtState = GPIO.input(dt)

global zeroState
zeroState = GPIO.input(zero)

global clkLastState
clkLastState = clkState

global servoPos
servoPos = 92

global num
num = 28

ror = []
ror = 224,476,739,995,1251,1492
##global ror1
##ror1 = 224
##global ror2
##ror2 = 476
##global ror3
##ror3 = 739
##global ror4
##ror4 = 995
##global ror5
##ror5 = 1251
##global ror6
##ror6 = 1492

nr = []
nr = 18,22,26,30,34,38,42,46
##global nr1
##nr1 = 18
##global nr2
##nr2 = 22
##global nr3
##nr3 = 26
##global nr4
##nr4 = 30
##global nr5
##nr5 = 34
##global nr6
##nr6 = 38
##global nr7
##nr7 = 42
##global nr8
##nr8 = 46
##global nr9
##nr9 = 50
##global nr10
##nr10 = 54

#Start the program in disable mode
disable()
try:
    pumpStop()
    pwm.start(8)
    servoPwm2.start(92)
    pickUp(ror[0],50)
    #moveTo(ror6)
##    startPos()
##    moveTo(224+820)
##    for j in range(1,7,1):
##        for i in range(7,-1,-1):
##            pickUp(ror[j], nr[i])

##    moveTo(ror1)
##    servoDown(nr2)
##    pumpStart()
##    servoUp()
##    outputPos()
##    pickUp(ror1)
##    pickUp(ror2)
##    pickUp(ror3)
##    pickUp(ror4)
##    pickUp(ror5)
##    pickUp(ror6)



    
    
    #outputPos()
    while 1:
        root.update_idletasks()#{root.mainloop()
        root.update()          #{root.mainloop()
        checkOutput()
        resetState()
        checkUptime()
        checkEncoder()
    
except KeyboardInterrupt:
    servoClose()
    pumpStop()
    pwm.stop()
    servoPwm.stop()
    servoPwm2.ChangeDutyCycle(92)
    print
    print "Stopping program!"
    pass    
GPIO.cleanup()



