# When adding new columns to some models, first do a 'make save'
# then add you new columns, and do a 'make load'
#
# 'make pull' use save and load to work around new models columns coming from
# the git repository
#
pull:
	make save
	git pull --rebase
	make load

save:
	python manage.py dumpdata saml auth >saved.json

load:
	-rm -f authentic.db
	python manage.py syncdb --noinput
	python manage.py loaddata saved
	rm saved.json
