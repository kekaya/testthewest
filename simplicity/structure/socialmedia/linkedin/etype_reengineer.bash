#!/bin/bash

#
# if you are looking for the ethertypes assigned to different L3 protocols, 
# you might want to look at the wireshark definitions in wireshark upstream
# I am taking the one indicated in https://www.wireshark.org/docs/wsdg_html_chunked/ChSrcUpdating.html 
#
# so you clone and you do 
#   git clone https://gitlab.com/wireshark/wireshark.git
#   cd wireshark
#   git rev-parse  HEAD
#   (shows 2a30bc0d96ec74ff4a75b4ae047acd29427686a2)
#   cd epan        # ref [1]
#  
#   so now, what happens ? 
#   Looking to https://www.ietf.org/archive/id/draft-thain-ipv8-00.html , 
#   you have quite some lines of text describing a new internet protocol version 
#   after IPv4 (I assume "v4" means "internet protocol version 4". Just wondering where v1 to 3 are . Was there a version 0 BTW? )
#   and IPv6 (I assume "v6" means "internet protocol version 6". Where is version 5 ? Not at all sure about the version numbering scheme. 
#   maybe. "v4" relates to 4 bytes of IP address ID . but then why has "v6" not initially be "v8" as it has 8 bytes of IP address. Whatever.
#   If somebody wonders why I feel like an extraterrestrian, that's a good illustration why)
#   anyway , that's details about earthling fuzziness...
#
#   and now I guess that this new version of internet protocol (v8) is basing on a L2 protcol identifier.
#   As far as I now, earthlings have somewhat agreed to put them here first https://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers.xhtml
# 
#   OK, checking...
#     2048        0800            513           1001          Internet Protocol version 4     [RFC9542]
#                                                              (IPv4)
#     34525       86DD            -             -             Internet Protocol version 6     [RFC9542]
#                                                              (IPv6)
# 
# so now , where is v8 ? 
# 
#  how would you want to test that if you haven't even agreed on how you can see if IP v8 traffic is on the wire ? 
#     
#  whatever...
#
#   so now you are in ref [1] (see above)
# 
#

if [ $# -lt 1 ]
then
  echo "usage $0 <etypes.h file from wireshark upstream> [CSV file as output]"
  exit 1
fi

ETYPES_H=$1
C_FILE="/tmp/etypes.c"
EXEC="/tmp/etypes"

GIT_REMOTE=$(git remote -v | awk '{print $2;exit}')
GIT_COMMIT=$(git rev-parse HEAD )
#
# go to the folder where etypes.h is located
#
cd $(dirname $ETYPES_H)

awk -v remote=$GIT_REMOTE  -v commit=$GIT_COMMIT -v cfile=$C_FILE 'BEGIN{
       GET_VALUE="define statement"
       CONDITIONAL_DEFINE="conditionality for if statement"
       g_etype_prefix["#define"] = GET_VALUE
       g_etype_prefix["#ifndef"] = CONDITIONAL_DEFINE
     }
     #
     # 2nd token in the header file ~ /^ETHERTYPE/
     #
     $2 ~ /^ETHERTYPE/{
        #
        # so the three tokens are prefix (precompiler hash ), ethertype define, (hex) value of ethertype
        #
        tmp_val = $3;
        tmp_etype = $2;
        tmp_prefix = $1;
        #
        # print out what you find
        #
        print "precompiler prefix : \""tmp_prefix "\" , ethertype define name \"" tmp_etype "\", value (hex):  \""tmp_val"\""
        g_found[tmp_etype]++;
        #
        # header file integrity check
        #
        if(g_etype_prefix[tmp_prefix] == GET_VALUE){
          if(g_etype_define_reverse[tmp_val]){
            error = error "ERROR line " NR ": etype " tmp_etype " value "tmp_val" already assigned for " g_etype_define_reverse[tmp_val]
          }
          g_etype_define[tmp_etype] = tmp_val;
          g_etype_define_reverse[tmp_val] =  tmp_etype;
        }
        #
        # precompiler hash integrity check
        #
        if(!g_etype_prefix[tmp_prefix]){
           error = error "ERROR line " NR ": prefix " tmp_prefix " for "tmp_etype" unsupported\n"
        }else{
          g_etype_check[tmp_etype,tmp_prefix]++;
        }
     }
     END{
       #
       # print integrity check error
       #
       print "\n++++++++++++++++++\nERROR:\n"error "\n+++++++\nEND error"
       print "#include <stdio.h>\n\nint main(int argc, char **argv){\n\n" >cfile
       print "printf(\"remote:;"remote"\\n\");" >cfile
       print "printf(\"commit:;"commit"\\n\\n\");" >cfile
       print "printf(\"etype define;etype val (dec);etype val(hex)\\n\");" >cfile

       for(i in g_etype_define){
         print "printf(\""i";%d;0x%04x\\n\","g_etype_define[i]","g_etype_define[i]");" >cfile
       }
       print "\nreturn 0;\n}" >cfile
     }' $ETYPES_H

echo "C file " $C_FILE


g++ $C_FILE -o $EXEC

if [ $# -gt 1 ]
then
  $EXEC >$2
  echo "CSV file written to " $2
fi





