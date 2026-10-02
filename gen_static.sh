#!/bin/sh

# This tool turns on the read-only mode and dumps the entire site using
# wget. Before running the script, you should launch the site at
# http://127.0.0.1:8000
# 
# python3 wypyplus.py
echo "Please make sure the site is available at http://127.0.0.1:8000"
sleep 2

# Set the edit veriable to an empty string to turn on read-only mode.
# Restart the server after this so it picks up the change.
mv wypyplus.py wypyplus_bak.py
sed -e "s|'WyPyPlus','✎'|'WyPyPlus',''|" wypyplus_bak.py > wypyplus.py
echo "Restart 'python3 wypyplus.py' now, then press Enter."
read _
wget --recursive \
    --page-requisites \
    --html-extension \
    --convert-links\
    --no-parent http://127.0.0.1:8000/wypyplus.py
mv wypyplus_bak.py wypyplus.py

# Generate an index page
cat << EOF2 > 127.0.0.1:8000/index.html
<meta http-equiv="Refresh" content="0; url='wypyplus.py.html'" />
EOF2
mv 127.0.0.1:8000 gen_site
echo "Done. Output site to the ./gen_site directory."
