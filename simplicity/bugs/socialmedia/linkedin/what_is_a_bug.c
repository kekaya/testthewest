#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

//
// Aus der Reihe "Elefanten aus Mücken zu machen".
// Ich liebe es, Elefanten aus Mücken zu machen.
// 
//
// Diskussion über bugs auf Linkedin:
// https://www.linkedin.com/feed/update/urn:li:activity:7418230606125236224?commentUrn=urn%3Ali%3Acomment%3A%28activity%3A7418230606125236224%2C7418565629609361408%29&dashCommentUrn=urn%3Ali%3Afsd_comment%3A%287418565629609361408%2Curn%3Ali%3Aactivity%3A7418230606125236224%29
// Was ist ein Bug? 
// Teilen durch Null. 
// 
//
/*
  Manifest:
  ---------
    * auf der shell ausgeführt
      bash 
          bash --version
          GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)
      uname -a 
          Linux <computername> 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
          --> Ja, Win 11 mit WSL. Nächstens mit Linux --> linuxmint-22.3-xfce-64bit.iso . Könnt ich auch als WSL container machen. 
              aber doch dann lieber Linux native ... 
      g++ --version
        g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
      g++ -M what_is_a_bug.c
        what_is_a_bug.o: what_is_a_bug.c /usr/include/stdc-predef.h \
         /usr/include/stdio.h \
         /usr/include/x86_64-linux-gnu/bits/libc-header-start.h \
         /usr/include/features.h /usr/include/features-time64.h \
         /usr/include/x86_64-linux-gnu/bits/wordsize.h \
         /usr/include/x86_64-linux-gnu/bits/timesize.h \
         /usr/include/x86_64-linux-gnu/sys/cdefs.h \
         /usr/include/x86_64-linux-gnu/bits/long-double.h \
         /usr/include/x86_64-linux-gnu/gnu/stubs.h \
         /usr/include/x86_64-linux-gnu/gnu/stubs-64.h \
         /usr/lib/gcc/x86_64-linux-gnu/13/include/stddef.h \
         /usr/lib/gcc/x86_64-linux-gnu/13/include/stdarg.h \
         /usr/include/x86_64-linux-gnu/bits/types.h \
         /usr/include/x86_64-linux-gnu/bits/typesizes.h \
         /usr/include/x86_64-linux-gnu/bits/time64.h \
         /usr/include/x86_64-linux-gnu/bits/types/__fpos_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/__mbstate_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/__fpos64_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/__FILE.h \
         /usr/include/x86_64-linux-gnu/bits/types/FILE.h \
         /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h \
         /usr/include/x86_64-linux-gnu/bits/types/cookie_io_functions_t.h \
         /usr/include/x86_64-linux-gnu/bits/stdio_lim.h \
         /usr/include/x86_64-linux-gnu/bits/floatn.h \
         /usr/include/x86_64-linux-gnu/bits/floatn-common.h \
         /usr/lib/gcc/x86_64-linux-gnu/13/include/stdint.h /usr/include/stdint.h \
         /usr/include/x86_64-linux-gnu/bits/wchar.h \
         /usr/include/x86_64-linux-gnu/bits/stdint-intn.h \
         /usr/include/x86_64-linux-gnu/bits/stdint-uintn.h \
         /usr/include/x86_64-linux-gnu/bits/stdint-least.h \
         /usr/include/c++/13/stdlib.h /usr/include/c++/13/cstdlib \
         /usr/include/x86_64-linux-gnu/c++/13/bits/c++config.h \
         /usr/include/x86_64-linux-gnu/c++/13/bits/os_defines.h \
         /usr/include/x86_64-linux-gnu/c++/13/bits/cpu_defines.h \
         /usr/include/c++/13/pstl/pstl_config.h /usr/include/stdlib.h \
         /usr/include/x86_64-linux-gnu/bits/waitflags.h \
         /usr/include/x86_64-linux-gnu/bits/waitstatus.h \
         /usr/include/x86_64-linux-gnu/bits/types/locale_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/__locale_t.h \
         /usr/include/x86_64-linux-gnu/sys/types.h \
         /usr/include/x86_64-linux-gnu/bits/types/clock_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/clockid_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/time_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/timer_t.h /usr/include/endian.h \
         /usr/include/x86_64-linux-gnu/bits/endian.h \
         /usr/include/x86_64-linux-gnu/bits/endianness.h \
         /usr/include/x86_64-linux-gnu/bits/byteswap.h \
         /usr/include/x86_64-linux-gnu/bits/uintn-identity.h \
         /usr/include/x86_64-linux-gnu/sys/select.h \
         /usr/include/x86_64-linux-gnu/bits/select.h \
         /usr/include/x86_64-linux-gnu/bits/types/sigset_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/__sigset_t.h \
         /usr/include/x86_64-linux-gnu/bits/types/struct_timeval.h \
         /usr/include/x86_64-linux-gnu/bits/types/struct_timespec.h \
         /usr/include/x86_64-linux-gnu/bits/pthreadtypes.h \
         /usr/include/x86_64-linux-gnu/bits/thread-shared-types.h \
         /usr/include/x86_64-linux-gnu/bits/pthreadtypes-arch.h \
         /usr/include/x86_64-linux-gnu/bits/atomic_wide_counter.h \
         /usr/include/x86_64-linux-gnu/bits/struct_mutex.h \
         /usr/include/x86_64-linux-gnu/bits/struct_rwlock.h /usr/include/alloca.h \
         /usr/include/x86_64-linux-gnu/bits/stdlib-float.h \
         /usr/include/c++/13/bits/std_abs.h
      ...keine Ahnung, wozu ich dieses Manifest noch brauch. 
      Schadet nicht.
    * bau das hier :
        g++ what_is_a_bug.c -o what_is_a_bug
      ...  und führ das aus, die ganze Zeile
      ./what_is_a_bug; awk -v ret=$(echo $?) '$2~ /^RUECKGABE_/{r[$3] = $2}END{print ret " ("r[ret]")"}'  what_is_a_bug.c
*/

/*
  Definitionen
*/
#define DO_NOT_USE_THIS_ILLEGAL_VALUE_IN_THE_DENOMINATOR_OF_A_DIVISON 0 // "Null" , was ist "Null"? 
                                                                        // An dieser Stelle will ich einwerfen, dass wir umdenken sollten
                                                                        // Einen Wert auf Null zu setzen, hat keinen qualitativen
                                                                        // sondern nur einen quantitativen Aspekt
                                                                        // Ist wie Bier trinken und kein Bier trinken.
                                                                        // Ist kein qualitativer Unterschied, kein Bier trinken
                                                                        // ist trotzdem Bier trinken. Halt Null Bier.
                                                                        // in der Praxis heißt "Teilen durch Null" dann immer nur was Theoretisches

#define NUMERATOR 10 // Zähler der Division braucht nicht konfigurierbar zu sein 

// Rückgabewerte
#define RUECKGABE_OK 0
#define RUECKGABE_KEIN_NENNER 1
#define RUECKGABE_FALSCHES_ZAHLENFORMAT 2

int main(int argc, char **argv){
  int32_t numerator = NUMERATOR; //Zähler einer Division. 
  int32_t denominator;
  int ret_arg;
  int ret;
  bool debug=false; // früher gab's den type bool in C nicht. Aber is ja schon lange her. 
                    // prompt "wann wurde type bool in c eingeführt?"
                    // --> da gefunden https://openbook.rheinwerk-verlag.de/c_von_a_bis_z/005_c_basisdatentypen_015.htm#mjea5fead98f181cf7573325643e428fa3
  
  // ich bau jetzt keine extra Funktion "usage()".
  // Ich pfusch jetzt quasi bewußt:
  if(argc<2){
    printf("Bedienung %s <Nenner für division : %d/Nenner> [bug durchlassen: 0, bug abfangen: 1]\n",argv[0],NUMERATOR);
    return RUECKGABE_KEIN_NENNER;
  }else{
    ret = sscanf(argv[1],"%d",&ret_arg);
    printf("Nenner: %d [%d]",atoi(argv[1]),ret);
    if(argc>2){

    }
  }
  
  
   
}

