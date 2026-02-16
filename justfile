all:
	just -l

# install systemd service(user scope)
install:
	cp kwallet_auto_unlock.service ~/.config/systemd/user/
	systemctl --user daemon-reload
	systemctl --user enable --now kwallet_auto_unlock.service

# use systemd-creds to generate password.cred
generate_password password="":
	@echo -n "{{ password }}" | systemd-creds encrypt --user - password.cred

run:
	python unlock.py

clean:
	rm -rf __pycache__
