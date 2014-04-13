from PyQt4 import QtCore, QtGui
import subprocess

settings={'AudioMode':'local','ScaleToScreen':'False',}
mediaLocation='/home'

class MediaPlayer(QtGui.QWidget):
	def __init__(self,app,dimensions,pixmaps):
		QtGui.QWidget.__init__(self)
		self.app=app
		self.playerWidth=dimensions[0]
		self.playerHeight=dimensions[4]
		self.setWindowTitle('OMXPlayer')
		self.process=None
		self.volume=3
		self.buttonDepressedPic=pixmaps[0]
		self.buttonPressedPic=pixmaps[1]
		iconPics=pixmaps[2]
		bgPic=pixmaps[3]
		progressBarPic=pixmaps[4]
		progressCirclePic=pixmaps[5]
		self.label=QtGui.QLabel(self)
		self.label.setPixmap(bgPic)
		self.label.resize(dimensions[0],dimensions[1])
		self.label.move(0,dimensions[4])
		self.player=QtGui.QLabel(self)
		self.player.resize(dimensions[0],dimensions[4])
		self.player.setStyleSheet('background-color: black')
		self.player.move(0,0)
		self.buttons=[]
		self.volumeBars=[]
		self.volumeBarPressed=[]
		self.volumeBarDepressed=[]
		self.volumeFunctions=[]
		numButtons=len(iconPics)
		self.iconWidth=dimensions[2]
		self.iconHeight=dimensions[3]
		self.progressBarHeight=dimensions[5]
		self.volumeBarWidth=dimensions[6]
		self.spacing=(dimensions[0]-numButtons*dimensions[2]-self.volumeBarWidth*10)/(numButtons+1)
		self.gap=(dimensions[1]-dimensions[3])/2
		for i in range(0,numButtons):
			self.buttons.append(QtGui.QLabel(self.label))
			self.buttons.append(QtGui.QLabel(self.label))
			self.buttons[i*2].setPixmap(self.buttonDepressedPic)
			self.buttons[i*2+1].setPixmap(iconPics[i])
			self.buttons[i*2].resize(self.iconWidth,self.iconHeight)
			self.buttons[i*2+1].resize(self.iconWidth,self.iconHeight)
			self.buttons[i*2].move(i*self.iconWidth+(i+1)*self.spacing,self.gap+self.progressBarHeight)
			self.buttons[i*2+1].move(i*self.iconWidth+(i+1)*self.spacing,self.gap+self.progressBarHeight)
		for i in range(0,5):
			self.volumeBars.append(QtGui.QLabel(self.label))
			volumeBarHeight=self.iconHeight/6*(i+1)
			self.volumeBarDepressed.append(QtGui.QPixmap(QtCore.QString('mediaplayer/depressed.png')).scaled(QtCore.QSize(self.volumeBarWidth,volumeBarHeight)))
			self.volumeBarPressed.append(QtGui.QPixmap(QtCore.QString('mediaplayer/pressed.png')).scaled(QtCore.QSize(self.volumeBarWidth,volumeBarHeight)))
			if i<self.volume:
				self.volumeBars[i].setPixmap(self.volumeBarPressed[i])
			else:
				self.volumeBars[i].setPixmap(self.volumeBarDepressed[i])
			self.volumeBars[i].resize(self.volumeBarWidth,volumeBarHeight)
			self.volumeBars[i].move(self.playerWidth+(2*i-10)*self.volumeBarWidth,
					self.gap+self.progressBarHeight+self.iconHeight-volumeBarHeight)
		self.progressBar=QtGui.QLabel(self.label)
		self.progressBar.setPixmap(progressBarPic)
		self.progressBar.resize(self.playerWidth-20-self.iconWidth*4,self.progressBarHeight)
		self.progressBar.move(10,self.gap/2)
		self.progressCircle=QtGui.QLabel(self.label)
		self.progressCircle.setPixmap(progressCirclePic)
		self.progressCircle.resize(self.progressBarHeight*2,self.progressBarHeight*2)
		self.progressCircle.move(10,self.gap/2-self.progressBarHeight/2)
		self.progressText=QtGui.QLabel(self.label)
		self.progressText.setFont(QtGui.QFont('Ubuntu Mono',12))
		self.progressText.resize(self.iconWidth*4,self.progressBarHeight*2)
		self.progressText.move(self.playerWidth-10-self.iconWidth*4,self.gap/2-self.progressBarHeight/2)
		self.progressText.setText("00:00:00/00:00:00")
		self.clock = QtCore.QTimer()
		self.clock.timeout.connect(self.updateClock)

		self.commands={"play":"p","pause":"p","stop":"q","volup":"+","voldown":"-",
					"seekLeft":"^[[D","seekRight":"^[[C","seekUp":"^[[A","seekDown":"^[[B"}
		self.options={'AudioMode':['local','hdmi'],'ScaleToScreen':['False','True']}
		self.buttons[1].mouseReleaseEvent=self.chooseFile
		self.buttons[3].mouseReleaseEvent=self.playVideo
		self.buttons[5].mouseReleaseEvent=self.pauseVideo
		self.buttons[7].mouseReleaseEvent=self.stopVideo
		self.buttons[9].mouseReleaseEvent=lambda e: self.chooseSettings(self.options)
		self.volumeBars[0].mouseReleaseEvent=lambda e: self.setVolume(1)
		self.volumeBars[1].mouseReleaseEvent=lambda e: self.setVolume(2)
		self.volumeBars[2].mouseReleaseEvent=lambda e: self.setVolume(3)
		self.volumeBars[3].mouseReleaseEvent=lambda e: self.setVolume(4)
		self.volumeBars[4].mouseReleaseEvent=lambda e: self.setVolume(5)
		self.progressBar.mouseReleaseEvent=self.setSeek
		

	def chooseFile(self,e):
		self.buttons[0].setPixmap(self.buttonPressedPic)
		self.app.processEvents()
		self.stopVideo()
		global mediaLocation
		self.file=str(QtGui.QFileDialog.getOpenFileName(self,"Select a media file",mediaLocation,"Music/Video (*.mp3 *.mp4)"))
		self.buttons[0].setPixmap(self.buttonDepressedPic)
		if self.file=='':
			return
		self.buttons[2].setPixmap(self.buttonPressedPic)
		self.buttons[4].setPixmap(self.buttonDepressedPic)
		self.buttons[6].setPixmap(self.buttonDepressedPic)
		self.app.processEvents()
		mediaLocation=self.file
		s=subprocess.check_output(['/usr/bin/omxplayer','-i',self.file],stderr=subprocess.STDOUT)
		for line in s.split('\n'):
			l=line.lstrip()
			if l.startswith('Duration: '):
				self.duration=int(l[10:12])*3600+int(l[13:15])*60+int(l[16:18])
			elif not l.find('Video: ')==-1:
				resolution=l.split(',')[2].split(' ')[1]
				ind=resolution.find('x')
				self.videoWidth=int(resolution[0:ind])
				self.videoHeight=int(resolution[ind+1:])
		self.progressText.setText("00:00:00/"+self.getClockString(self.duration))
		if self.videoWidth==0: #sound file
			self.process=subprocess.Popen(['/usr/bin/omxplayer','-o',settings['AudioMode'],
				self.file],stdin=subprocess.PIPE)
		else: #video file
			if settings['ScaleToScreen']=='True':
				position=str(self.geometry().left())+' '+str(self.geometry().top())+' '+str(self.geometry().left()+self.playerWidth)+' '+str(self.geometry().top()+self.playerHeight)
			else:
				newWidth=min(self.playerWidth,self.videoWidth)
				newHeight=min(self.playerHeight,self.videoHeight)
				position=str(self.geometry().left()+(self.playerWidth-newWidth)/2)+' '+\
							str(self.geometry().top()+(self.playerHeight-newHeight)/2)+' '+\
							str(self.geometry().left()+(self.playerWidth-newWidth)/2+newWidth)+' '+\
							str(self.geometry().top()+(self.playerHeight-newHeight)/2+newHeight)
			self.process=subprocess.Popen(['/usr/bin/omxplayer','-o',settings['AudioMode'],
				'--win',position,self.file],stdin=subprocess.PIPE)
		QtCore.QThread.sleep(2) #wait for video to start
		self.clock.start(1000)
		oldVolume=self.volume
		self.volume=3
		self.setVolume(oldVolume)

	def controlPlayer(self,type):
		if self.process is not None and self.process.poll() is None:
			self.process.stdin.write(self.commands[type])

	def updateClock(self):
		if self.process is not None and self.process.poll() is None:
			self.timeElapsed+=1
			#progress=10+(self.playerWidth-20-self.iconWidth*4-self.progressBarHeight*2)*self.timeElapsed/self.duration
			progress=10+self.progressBar.size().width()*self.timeElapsed/self.duration
			self.progressCircle.move(progress,self.gap/2-self.progressBarHeight/2)
			self.progressText.setText(str(self.getClockString(self.timeElapsed))+
				str(self.progressText.text())[8:])
		else:
			self.stopVideo()

	def getClockString(self,n):
		return str(n/3600).zfill(2)+':'+str((n%3600)/60).zfill(2)+':'+str(n%60).zfill(2)

	def playVideo(self,e):
		if self.process is not None and self.process.poll() is None and not self.clock.isActive():
			self.clock.start(1000)
			self.controlPlayer('play')
			self.buttons[2].setPixmap(self.buttonPressedPic)
			self.buttons[4].setPixmap(self.buttonDepressedPic)
			self.buttons[6].setPixmap(self.buttonDepressedPic)

	def pauseVideo(self,e):
		if self.clock.isActive():
			self.clock.stop()
			self.controlPlayer('pause')
			self.buttons[2].setPixmap(self.buttonDepressedPic)
			self.buttons[4].setPixmap(self.buttonPressedPic)
			self.buttons[6].setPixmap(self.buttonDepressedPic)

	def stopVideo(self,e=None):
		self.clock.stop()
		self.progressText.setText("00:00:00/00:00:00")
		self.progressCircle.move(10,self.gap/2-self.progressBarHeight/2)
		if self.process is not None and self.process.poll() is None:
			self.process.stdin.write('q')
		self.duration=0
		self.videoWidth=0
		self.videoHeight=0
		self.timeElapsed=0
		self.process=None
		self.buttons[2].setPixmap(self.buttonDepressedPic)
		self.buttons[4].setPixmap(self.buttonDepressedPic)
		self.buttons[6].setPixmap(self.buttonPressedPic)

	def chooseSettings(self,choices):
		global settings
		self.stopVideo()
		self.buttons[8].setPixmap(self.buttonPressedPic)
		self.app.processEvents()
		for k in choices:
			v,ok=QtGui.QInputDialog.getItem(self,'',
				k+' (Currently '+settings[k]+')',choices[k],0,False)
			if ok:
				settings[k]=str(v)
		self.buttons[8].setPixmap(self.buttonDepressedPic)

	def saveSettings(self):
		settingsString="settings={"
		for k in settings:
			settingsString+="'"+k+"':'"+settings[k]+"',"
		settingsString+='}\n'
		mediaLocationString="mediaLocation='"+mediaLocation+"'\n"
		f=open('MediaPlayer.py','r')
		buffr=''
		for line in f:
			if line.startswith('settings={'):
				buffr+=settingsString
			elif line.startswith('mediaLocation='):
				buffr+=mediaLocationString
			else:
				buffr+=line
		f.close()
		f=open('MediaPlayer.py','w')
		f.write(buffr)
		f.close()

	def setVolume(self,v):
		for i in range(0,5):
			if i<v:
				self.volumeBars[i].setPixmap(self.volumeBarPressed[i])
			else:
				self.volumeBars[i].setPixmap(self.volumeBarDepressed[i])
		self.app.processEvents()
		if self.process is not None and self.process.poll() is None:
			command='volup'
			if v<self.volume:
				command='voldown'
			for i in range(0,abs(v-self.volume)*2):
				QtCore.QTimer.singleShot(i*50,lambda: self.controlPlayer(command))
		self.volume=v

	def setSeek(self,e):
		if self.process is not None and self.process.poll() is None:
			oldTime=self.timeElapsed
			self.timeElapsed=e.pos().x()*self.duration/self.progressBar.size().width()
			diff = (self.timeElapsed-oldTime)/30 #only increments of 30s
			#if diff==0: #mininum increment
				#diff=1 if self.timeElapsed>oldTime else -1
			self.timeElapsed=oldTime+diff*30
			progress=10+self.progressBar.size().width()*self.timeElapsed/self.duration
			self.progressCircle.move(progress,self.gap/2-self.progressBarHeight/2)
			self.progressText.setText(str(self.getClockString(self.timeElapsed))+
				str(self.progressText.text())[8:])
			self.app.processEvents()
			roughSeek='seekUp'
			if self.timeElapsed<oldTime:
				roughSeek='seekDown'
			cmds=[]
			for i in range(abs(oldTime-self.timeElapsed)/600):
				cmds.append(lambda: self.controlPlayer(roughSeek))
			fineSeek='seekRight'
			if self.timeElapsed<oldTime:
				fineSeek='seekLeft'
			for i in range(abs(oldTime-self.timeElapsed)%600/30):
				cmds.append(lambda: self.controlPlayer(fineSeek))
			for i in range(len(cmds)):
				QtCore.QTimer.singleShot(i*50,cmds[i])

	def closeEvent(self,e):
		self.saveSettings()
		if self.process is not None and self.process.poll() is None:
			self.process.stdin.write('q')
			self.process.terminate()
		e.accept()


if __name__=='__main__':
	app = QtGui.QApplication([])
	width=800
	height=100
	playerheight=800
	iconSize=50
	progressBarHeight=10
	volumeBarWidth=15
	bgPic=QtGui.QPixmap(QtCore.QString('mediaplayer/panel.png')).scaled(QtCore.QSize(width,height))
	buttonDepressedPic=QtGui.QPixmap(QtCore.QString('mediaplayer/depressed.png')).scaled(QtCore.QSize(iconSize,iconSize))
	buttonPressedPic=QtGui.QPixmap(QtCore.QString('mediaplayer/pressed.png')).scaled(QtCore.QSize(iconSize,iconSize))
	newPic=QtGui.QPixmap(QtCore.QString('mediaplayer/new.png')).scaled(QtCore.QSize(iconSize,iconSize))
	playPic=QtGui.QPixmap(QtCore.QString('mediaplayer/play.png')).scaled(QtCore.QSize(iconSize,iconSize))
	pausePic=QtGui.QPixmap(QtCore.QString('mediaplayer/pause.png')).scaled(QtCore.QSize(iconSize,iconSize))
	stopPic=QtGui.QPixmap(QtCore.QString('mediaplayer/stop.png')).scaled(QtCore.QSize(iconSize,iconSize))
	settingsPic=QtGui.QPixmap(QtCore.QString('mediaplayer/settings.png')).scaled(QtCore.QSize(iconSize,iconSize))
	progressBarPic=QtGui.QPixmap(QtCore.QString('mediaplayer/depressed.png')).scaled(QtCore.QSize(width-20-iconSize*2,progressBarHeight))
	progressCirclePic=QtGui.QPixmap(QtCore.QString('mediaplayer/circle.png')).scaled(QtCore.QSize(progressBarHeight*2,progressBarHeight*2))
	mp = MediaPlayer(
		app, (width,height,iconSize,iconSize,playerheight,progressBarHeight,volumeBarWidth),
		(buttonDepressedPic,buttonPressedPic,(newPic,playPic,pausePic,stopPic,settingsPic),
			bgPic,progressBarPic,progressCirclePic),
	)
	mp.show()
	app.exec_()