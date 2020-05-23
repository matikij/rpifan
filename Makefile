cur_dir := $(realpath .)

install:
	ln -s $(cur_dir)/fan.py /usr/local/bin/fan.py
	cp fan.service /etc/systemd/system/fan.service
uninstall:
	rm /usr/local/bin/fan.py /etc/systemd/system/fan.service
