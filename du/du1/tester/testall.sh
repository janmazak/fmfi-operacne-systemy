LOGNAME=`date -Iseconds`
./runtest.sh | tee $LOGNAME
./tohtml.sh < $LOGNAME > results1.html

