#coding:utf-8
from __future__ import print_function
import RPi.GPIO as GPIO
import time
import os

from myThread import myThread

'''my code'''
#定义一些全局变量
currentAction = "rest"
currentAttitude = "up"
#获取动作类别
def getTheCurrentAction(fileName = "actionTempData.dat"):
	if os.path.exists(fileName) == True:
		if os.path.getsize(fileName):
			with open (fileName , "r") as f:
				actionStr = f.read()  #读取字符串
				f.close()
			os.remove(fileName)
			# print("the current action1 is :" , actionStr)
			return  actionStr
		else:
			return None
	else:
		return None

#获取姿态数据类别
def getTheCurrentAttitude(fileName = "attitudeTempData.dat"):
	if os.path.exists(fileName) == True:
		if os.path.getsize(fileName):
			with open (fileName , "r") as f:
				attitudeStr = f.read()  #读取字符串
				if "+" in attitudeStr:
					# tempStr1 , tempStr2 = attitudeStr.split("+")
					return  attitudeStr
				else:
					return None
				f.close()
			os.remove(fileName)
		else:
			return None
	else:
		return None


class myCar(object):

	def __init__(self , controlType = 0):
		########电机驱动接口定义#################
		self.ENA = 13	#//L298使能A
		self.ENB = 20	#//L298使能B
		self.IN1 = 19	#//电机接口1
		self.IN2 = 16	#//电机接口2
		self.IN3 = 21	#//电机接口3
		self.IN4 = 26	#//电机接口4

		########车辆运行动作映射关系##############
		self.actionMapDict = {"forword" : "fist" , "back" : "open_hand" , "stop" : "love" ,
							  "turnLeft" : "one" , "turnRight" : "two"}
		self.attitudeActionMapDict = {"runDir":"open_hand" , "rotationDir":"fist" , "stop" : "love"} 
		
		self.actionType = None  #动作类型
		self.stepMove = 10  #执行最小步长
		self.stepRation = 10 #旋转最小步长
		self.startFlag = False   #程序开始标志位
		self.actionCount = 0  #对动作进行计数
		self.controlType = controlType #小车的控制类型（0：肌电+姿态 ； 1： 肌电）

	def start(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		#########电机初始化为LOW##########
		GPIO.setup(self.ENA,GPIO.OUT,initial=GPIO.LOW)
		GPIO.setup(self.IN1,GPIO.OUT,initial=GPIO.LOW)
		GPIO.setup(self.IN2,GPIO.OUT,initial=GPIO.LOW)
		GPIO.setup(self.ENB,GPIO.OUT,initial=GPIO.LOW)
		GPIO.setup(self.IN3,GPIO.OUT,initial=GPIO.LOW)
		GPIO.setup(self.IN4,GPIO.OUT,initial=GPIO.LOW)

		self.removeExitFile()
		self.removeExitFile(fileName = "attitudeTempData.dat")

	#########定义电机正转函数##########
	def turnLeft(self , angle = 90):
		print ('motor turn left')
		if angle == -1:
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,True)
			GPIO.output(self.IN2,False)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,True)
			GPIO.output(self.IN4,False)
			time.sleep(((self.stepRation * 1.0) / 90.0 ) * 0.46)
		else:
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,True)
			GPIO.output(self.IN2,False)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,True)
			GPIO.output(self.IN4,False)
			time.sleep(((angle * 1.0) / 90.0 ) * 0.46)
			self.stop()

	#########定义电机反转函数##########
	def turnRight(self , angle = 90):
		print ('motor turn right')
		if angle == -1 :
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,False)
			GPIO.output(self.IN2,True)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,False)
			GPIO.output(self.IN4,True)
			time.sleep(((self.stepRation * 1.0) / 90.0 ) * 0.46)
		else:
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,False)
			GPIO.output(self.IN2,True)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,False)
			GPIO.output(self.IN4,True)
			time.sleep(((angle * 1.0) / 90.0 ) * 0.46)
			self.stop()
	#########定义电机反转函数##########
	def forword(self , distance = 100):
		print ('motor forword')
		if distance == -1 :
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,True)
			GPIO.output(self.IN2,False)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,False)
			GPIO.output(self.IN4,True)
			time.sleep(((self.stepMove * 1.0) / 45.0 ) * 1)
		else:
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,True)
			GPIO.output(self.IN2,False)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,False)
			GPIO.output(self.IN4,True)
			time.sleep(((distance * 1.0) / 45.0 ) * 1)
			self.stop()
	#########定义电机反转函数##########
	def back(self , distance = 100):
		print ('motor back')
		if distance == -1 :
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,False)
			GPIO.output(self.IN2,True)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,True)
			GPIO.output(self.IN4,False)
			time.sleep(((self.stepMove * 1.0) / 45.0 ) * 1)
		else:
			GPIO.output(self.ENA,True)
			GPIO.output(self.IN1,False)
			GPIO.output(self.IN2,True)
			GPIO.output(self.ENB,True)
			GPIO.output(self.IN3,True)
			GPIO.output(self.IN4,False)
			time.sleep(((distance * 1.0) / 45.0 ) * 1)
			self.stop()
	#########定义电机停止函数##########
	def stop(self):
		print ('motor stop')
		GPIO.output(self.ENA,False)
		GPIO.output(self.ENB,False)
		GPIO.output(self.IN1,False)
		GPIO.output(self.IN2,False)
		GPIO.output(self.IN3,False)
		GPIO.output(self.IN4,False)
	######小车运行函数##############
	def carRun(self , actionType , attitude1 , attitude2):
		#肌电+姿态数据
		if self.controlType == 0:
			if actionType == self.attitudeActionMapDict["runDir"]:
				if attitude1 == "up": 	#前进    
					self.forword(distance = -1)
				elif attitude1 == "down":
					self.back(distance = -1)  #后退
			if actionType == self.attitudeActionMapDict["rotationDir"]:
				if attitude2 == "left":
					self.turnLeft(angle = 30)
				elif attitude2 == "right":
					self.turnRight(angle = 30)
			if actionType == self.attitudeActionMapDict["stop"]:
				self.stop()

		#肌电
		elif self.controlType == 1:
			
			if actionType == self.actionMapDict["forword"]:
				self.forword(distance = -1)
			elif actionType == self.actionMapDict["back"]:
				self.back(distance = -1)
			elif actionType == self.actionMapDict["turnLeft"]:
				self.turnLeft(angle = 30)
			elif actionType == self.actionMapDict["turnRight"]:
				self.turnRight(angle = 30)
			elif actionType == self.actionMapDict["stop"]:
				self.stop()

	def safeAction(self):
		'''安全措施函数'''
		if self.startFlag == True:
			if self.actionCount > 300:
				print("wfy")
				self.stop()
				self.mThread.forcedStopThread()

	def removeExitFile(self , fileName = "actionTempData.dat" ):
		'''删除已经存在的文件'''
		if os.path.exists(fileName) == True:
			os.remove(fileName)


	def getTheActionMain(self):
		'''得到动作类别线程函数'''
		while True:
			#肌电+姿态传感器
			if self.controlType == 0:
				self.actionType = getTheCurrentAction()
				tempAttitudeStr = getTheCurrentAttitude()
				if tempAttitudeStr == None:
					pass
				else:
					self.attitude1 , self.attitude2 = tempAttitudeStr.split("+")
					print("self.attitude1 is :" , self.attitude1)
					print("self.attitude2 is :" , self.attitude2)
				if self.actionType == None:
					self.actionCount += 1
				else:
					self.startFlag = True
					self.actionCount = 0
			#肌电
			elif self.controlType == 1:
				self.actionType = getTheCurrentAction()
				if self.actionType == None:
						self.actionCount += 1
				else:
					self.startFlag = True
					self.actionCount = 0

			self.safeAction()
			# self.carRun(self.actionType , self.attitude1 , self.attitude2 )
			time.sleep(0.01)

	def setTheActionMain(self):
		'''设置动作类别线程函数'''
		os.system("python myoMain.py")
		time.sleep(0.01)

	def run(self):
		'''主函数'''
		try:
			self.mThread = myThread()
			self.mThread.addThread('setTheActionMain' , self.setTheActionMain , 0)
			self.mThread.addThread('getTheActionMain' , self.getTheActionMain , 0)
			self.mThread.runThread()
		except KeyboardInterrupt:
			self.stop()
			self.mThread.forcedStopThread()

if __name__ == "__main__":

	mCar = myCar()
	mCar.start()
	mCar.run()








	


