#!/bin/sh
ROOT_DIR=/usr/share/nginx/html

# Replace env vars in files served by NGINX
for file in $ROOT_DIR/assets/*.js* $ROOT_DIR/index.html;
do
  sed -i 's|NEXT_PUBLIC_TELLER_APPLICATION_ID_PLACEHOLDER|'${TELLER_APPLICATION_ID}'|g' $file
done
