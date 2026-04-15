help:
	just -l

# install dinit service (user scope)
install:
	cp kwallet_auto_unlock ~/.config/dinit.d/

# enable dinit service (user scope)
enable:
	dinit enable kwallet_auto_unlock

# install and enable service
setup: install enable

# use clevis to generate password.cred
generate_password password="":
	@clevis encrypt tpm2 '{}' <<< "{{ password }}" > password.cred

run:
	python unlock.py

clean:
	rm -rf __pycache__
