#!/bin/bash
SDIR=src
SOURCES=$(cd $SDIR; ls *.c)
BIN=bin
TMPFILE=/tmp/data_os_homework1_runtest
OUTFILE=/tmp/out_os_homework1_runtest
RESFILE=/tmp/res_os_homework1_runtest
LIMIT_TIME=1

set +m
#set -o xtrace

function red_echo() {
echo -ne "\e[0;31m"
echo $@
echo -ne "\e[00m"
}

function green_echo() {
echo -ne "\e[0;32m"
echo -n $@
echo -ne "\e[00m"
}

function slow() {
	sudo cpupower --cpu 0,1,2,3 frequency-set -u 800000
}

function fast() {
	sudo cpupower --cpu 0,1,2,3 frequency-set -u 3200000
}


function compile() {
	echo -n "Compiling"
	for i in $SOURCES; do
		SRC=$SDIR/$i
		DST=$BIN/${i%.c}
		if [ $SRC -nt $DST ]; then
			gcc -std=c99 -Werror=implicit-function-declaration -g $SRC -pthread -o $DST 2>&1 | tee errors/${i%.c}.txt
			echo -n "+"
		else
			echo -n "."
		fi
	done;
	echo
}

function launch() {
		(/usr/bin/time -f "%e %U %S" $@ <$TMPFILE 3>&1 1>&2 2>&3 >$OUTFILE 2>$RESFILE) &
		RESPID=$!
		
		( sleep $LIMIT_TIME; kill -9 `pgrep -P $RESPID` $RESPID  >/dev/null 2>&1) &
		KILLPID=$!
		disown $KILLPID

		wait $RESPID 2>/dev/null
		ret=$?
		
		pkill -INT  -P $KILLPID  >/dev/null 2>&1
		pkill -QUIT -P $KILLPID  >/dev/null 2>&1
		pkill -KILL -P $KILLPID  >/dev/null 2>&1

		return $ret
}

function result() {
	infile=$1
	outfile=$2
	resfile=$3
	retval=$4

	res=$(cat $RESFILE)
	
	diff -b $infile $outfile >/dev/null
	dif=$?
	
	if [ $retval -ne 0 ]; then
		if [ $retval -eq 137 ]; then
			red_echo -n "Time limit exceeded";
		elif [ $retval -eq 139 ]; then
			red_echo -n "Segmentation fault";
		else
			red_echo -n "FAIL ($retval)";
		fi;
	else
		if [ $dif -ne 0 ]; then
			orig=$(ls -s --block-size=1 $infile |cut -d" " -f 1)
			new=$(ls -s --block-size=1 $outfile |cut -d" " -f 1)
			red_echo -n "Wrong answer ($orig,$new)";
		else
			green_echo -e "${res}";
		fi
	fi

}

function run_test() {
	size=$1; shift
	run_only=$@  # list of all the additional args
	rm -f $TMPFILE
	touch $TMPFILE

	# for size > 0, generate data
	if [ x$size != x0 ]; then dd if=/dev/urandom of=$TMPFILE bs=$size count=1 iflag=fullblock; fi

	# if names specified, run only those
	if [ x$run_only != x ]; then
		run="$run_only"
		disableCache=1
	else
		run="$(ls -1 $BIN/*)"
		disableCache=0
	fi;
	
	for i in $run; do
		if ! [[ $i == $BIN/* ]]; then executable=$BIN/$i; else executable=$i; fi
		name=$(basename ${i})
		CACHED=cache/${name}-${size}.cache
		if [ $disableCache ] || [ ! -f $CACHED ] || [ $i -nt $CACHED ]; then
			(
			echo -ne "${size}\t$(printf "%16s" ${name})\t"
			
			for n in {1..3}; do
				rm -f $OUTFILE
				launch $executable
				ret=$?
				
				echo -n $(result $TMPFILE $OUTFILE $RESFILE $ret)
				echo -ne "\t"
			done
			echo;
			) | tee $CACHED
		else
			cat $CACHED
		fi

	done
	rm -f $TMPFILE
}


date
echo "Running tests with deadline $LIMIT_TIME seconds"

rm -rf ./$BIN
mkdir -p ./$BIN ./cache ./errors

ONLY=$@
compile $ONLY

run_test 0 $ONLY
run_test 47 $ONLY
#run_test 100K $ONLY
#run_test 10M $ONLY
run_test 100M $ONLY
#run_test 500M $ONLY
#run_test 1000M $ONLY

rm -rf ./$BIN
