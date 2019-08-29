#!/bin/bash
 
from="qing@biomarker.com.cn"
to="xiayh@biomarker.com.cn,wuq@biomarker.com.cn"
subject=$1;
body=$2;
mail -s "$subject" -r "$from" -S smtp="smtp://smtp.263.net:465" \
                              -S smtp-auth=login \
                              -S smtp-auth-user="qing@biomarker.com.cn" \
                              -S smtp-auth-password="GQin123" \
                              -S sendwait \
                              "$to" <<< "$body"
