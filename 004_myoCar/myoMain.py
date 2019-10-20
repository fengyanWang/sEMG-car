#coding:UTF-8
from __future__ import print_function
import os
import time
import math
import platform
import threading
import numpy as np
from myThread import myThread
from offlineClf import myModel
from sklearn.externals import joblib
from FeatureSpace import FeatureSpace
from myo import  Myo ,  VibrationType , DeviceListener 

#监听myo数据的类
class PrintPoseListener(DeviceListener):
	def __init__(self , dataType = ["emg" , "imu"]):
		self.emgData = [] #用于存储肌电数据
		self.emgDataCount = 0
		self.dataType = dataType
		self.currentOrientation=[0,0,0,0] #当前的四元数
		self.referenceOrientation=[0,0,0,0] #上个时刻的四元数
	#肌电数据处理函数
	def on_emg(self, emg, moving):
		if "emg" in self.dataType:
			self.emgData = list(self.emgData)
			self.emgData.append(emg)
			self.emgDataCount += 1
		else:
			pass

	#由四元数得到欧拉角
	def getTheEuler(self , quat):
		w ,x, y, z = quat[0], quat[1], quat[2], quat[3]
		self.roll = math.atan2( 2*w*x + 2*y*z, 1 - 2*x*x - 2*y*y )
		self.pitch = math.asin( max( -1, min( 1 , 2*w*y - 2*z*x )))
		self.yaw = math.atan2( 2*w*z + 2*x*y, 1 - 2*y*y - 2*z*z )

	#姿态数据处理函数
	def on_imu(self , quat, acc, gyro ):
		if "imu" in self.dataType:
			self.getTheEuler(quat)
		else:
			pass
#在线分类
class main(object):

	def __init__(self , dataType = ["emg" , "imu"]):

		self.emgDict = dict()
		self.numberVoter = 3
		self.dataType = dataType
		self.L = threading.Lock()
		self.modelFilePath = "emg_1535856299.pkl"

	def start(self):
		self.listener = PrintPoseListener(dataType = self.dataType)
		self.mMyo = Myo() 
		self.getSystermType()

		try:
			self.mMyo.connect() 
			self.mMyo.add_listener(self.listener)
			self.mMyo.vibrate(VibrationType.SHORT)
		except ValueError as ex:
			print (ex)
		# self.getTheModelFileName()
		self.loadModel()#导入模型
		self.mMyo.vibrate(VibrationType.MEDIUM)#震动表示模型导入完成
	#获取姿态控制的数据
	def getAttitudeControlData(self , roll , pitch , yaw):
		# print("the roll is :" , roll)
		# print("the pitch is :" , pitch)
		if pitch > 0:
			tempData1 = "up"
		elif pitch < 0:
			tempData1 = "down"
		if roll > 0:
			tempData2 = "left"
		elif roll < 0:
			tempData2 = "right"
		return tempData1 , tempData2
	#往文件中写入动作字符串
	def writeActionFile(self , fileName = "actionTempData.dat" , actionStr = "rest"):
		'''将最终的动作写入文件中'''
		if os.path.exists(fileName) == False:
			with open (fileName , "w") as f:
				f.write(actionStr)
				f.close()
				# print("write over!!")
		else:
			pass

	#采集线程主程序
	def myoRun(self):
		try:
			while True:
				self.mMyo.run()
				time.sleep(0.001)
		except KeyboardInterrupt:
			self.mMyo.safely_disconnect()

	#获取在线分类结果函数(分类线程函数)
	def onlineClf(self):

		try:
			while True:
				if "emg" in self.dataType:
					if self.listener.emgDataCount > self.model.mWinWidth  + self.numberVoter - 1:    #投票数为其加1
						self.listener.emgDataCount = 0
						self.L.acquire()
						self.listener.emgData = np.array(self.listener.emgData , dtype = np.int64)
						self.listener.emgData = self.listener.emgData.T
						self.emgDict['one'] = self.listener.emgData
						self.L.release() 
						
						self.sample = FeatureSpace(rawDict = self.emgDict, 
								  moveNames = ['one',], #动作类别
								  ChList = [0,1,2,3,4,5,6,7],  #传感器的通道数目
								  features = {'Names': self.model.mFeatureList,  #定义的特征
											  'LW': self.model.mWinWidth,  #定义的窗宽
											  'LI': self.model.mSlidingLen},   #定义的窗滑动的步长
								  one_hot = False ,
								  trainPercent=[1, 0, 0]    #是否进行onehot处理
								 )
						self.L.acquire()
						self.getTrainData()
						actionList = self.model.mModel.predict(self.trainX)
						self.writeActionFile(actionStr = str(self.getTheAction(actionList)))
						self.L.release() 
						self.listener.emgData = []
						self.emgDict.clear()
						time.sleep(0.001)
					else:
						time.sleep(0.001)
									
		except KeyboardInterrupt:
			pass

	#The feature space is divided into data sets
	def getTrainData(self):

		nDimensions = self.sample.trainImageX.shape[1]
		#训练集
		self.trainX = np.reshape(self.sample.trainImageX, (-1, nDimensions))
		self.trainY = np.squeeze(self.sample.trainImageY)
		#测试集
		self.testX = np.reshape(self.sample.testImageX, (-1, nDimensions))
		self.testY = np.squeeze(self.sample.testImageY)
		#评估集
		self.validateX = np.reshape(self.sample.validateImageX, (-1, nDimensions))
		self.validateY = np.squeeze(self.sample.validateImageY)

	'''导入已经保存的模型'''
	def loadModel(self):

		self.model = joblib.load(self.modelFilePath)
		self.actionNames = self.model.actionNames

	def getSystermType(self):
		'''获得系统平台类型'''
		self.systermType = platform.system()

	
	#投票函数
	def getTheAction(self , actionList):

		tempData = np.array(actionList)
		counts = np.bincount(tempData)
		actionNumber = np.argmax(counts)
		return self.actionNames[actionNumber]#返回定义的动作类别字符串

	#获取姿态数据
	def getTheAttitudeMain(self):
		if "imu" in self.dataType:
			while True:
				tempStr1 , tempStr2 = self.getAttitudeControlData(self.listener.roll , self.listener.pitch , self.listener.yaw)
				attitudeControlStr = tempStr1 + '+' + tempStr2
				# print("the attitude is :" , attitudeControlStr)
				self.L.acquire()
				self.writeActionFile( fileName = "attitudeTempData.dat" , actionStr = attitudeControlStr )
				self.L.release() 
				time.sleep(0.001)	
		else:
			time.sleep(0.001)
			pass

	'''myo主程序的入口'''
	def run(self):
		try:
			self.mThread = myThread()
			self.mThread.addThread('onlineClf' , self.onlineClf , 0) #加入在线识别动作线程
			self.mThread.addThread('getData' , self.myoRun , 0) #加入数据采集的线程
			self.mThread.addThread('getTheAttitudeMain' , self.getTheAttitudeMain , 0) #加入数据采集的线程
			self.mThread.runThread()
		except KeyboardInterrupt:
			self.mMyo.safely_disconnect()
			self.mThread.forcedStopThread()

if __name__ == "__main__":

	mMain = main(dataType = ["emg" , "imu"])
	mMain.start()
	mMain.run()