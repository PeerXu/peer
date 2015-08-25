clean:
	find . -name "*.pyc" -delete
	find . -name "TAGS" -delete
	find . -name "cscope.*" -delete

sync:
	rsync -azP . cloud@10.12.31.1:~/sources/peer/

zip:
	rm -f peer.zip
	zip -r peer.zip .
	make sync

develop:
	python setup.py develop
