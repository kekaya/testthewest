#!/bin/bash

C_PROG="what_is_a_bug.c"
OUTPUT_EXECUTABLE=$(basename $C_PROG .c)

function ausfuehr(){
 NENNER_=$1
 DEBUG_=$2
 echo -e "+++++++++++\nNenner \"$NENNER_\" , Debug  \"$DEBUG_\""
 ./$OUTPUT_EXECUTABLE $NENNER_ $DEBUG_ ;  awk -v ret=$(echo $?) '$2~ /^RUECKGABE_/{r[$3] = $2}END{print ret " ("r[ret]")"}'  what_is_a_bug.c
 echo "+++++++++++"
}

cmd="g++ $C_PROG -o $OUTPUT_EXECUTABLE"
$cmd
ret=$? 
if [ $ret -ne 0 ]
then
  echo -e "\n+++++++++++++++++++\nKommando\n$cmd\nfehlgeschlagen mit Rückgabewert $ret"
  exit $ret
else
  echo -e "Kommando\n$cmd\nOK : Ausführbare Datei\n $(ls -l $OUTPUT_EXECUTABLE)\n\n $(file $OUTPUT_EXECUTABLE)\n"
fi

DEBUG=""
NENNER=""

ausfuehr $NENNER $DEBUG

NENNER="1.1"
ausfuehr $NENNER $DEBUG

NENNER="1"
ausfuehr $NENNER $DEBUG








