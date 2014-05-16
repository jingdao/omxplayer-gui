omxplayer-gui
=============

PyQt4 GUI for OMXPlayer (Raspberry Pi)

	Usage:
		python MediaPlayer.py

	Embedding in PyQt apps:
		
		from MediaPlayer import MediaPlayer
		mp=MediaPlayer(app,parent)
		mp.move(x,y)
		mp.resize(width,height)
		mp.show()
	

Dependencies
------------

- python
- PyQt4
- omxplayer (installed in /usr/bin/omxplayer)

Features
--------

- gui buttons for play/pause/stop and volume control
- custom settings for audio output and video scaling
- progress bar with time and ability to seek

Concepts
--------

- use Python subprocess module to start OMXPlayer process
- use process.stdin.write to pipe commands to OMXPlayer
- parse the output from omxplayer -i option to get duration and resolution
- use QtCore.QTimer.singleShot to queue commands
- use QtCore.QTimer object to time video progress

