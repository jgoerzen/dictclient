doc:
	PYTHONPATH=`pwd` pydoc2.2 dictclient > dictclient.txt
	PYTHONPATH=`pwd` pydoc2.2 -w dictclient

clean:
	-rm -f `find . -name "*~"`
	-rm -f `find . -name "*.pyc"`
