install:
	ln -s $(PWD)/fan.py /usr/local/bin/fan.py
	cp fan.service /etc/systemd/system/fan.service
