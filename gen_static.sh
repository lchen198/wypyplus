#!/bin/sh

# This tool turns on the read-only mode and dumps the entire site using
# wget. Before running the script, you should launch the site at
# http://127.0.0.1:8000
# 
# python3 -m http.server --cgi 8000
echo "Please make sure the site is available at http://127.0.0.1:8000"
sleep 2

# Set the edit veriable to an empty string to turn on read-only mode.
mv cgi-bin/wypyplus.py cgi-bin/wypyplus_bak.py
sed -e "s|edit='[^']*';|edit='';|" cgi-bin/wypyplus_bak.py > cgi-bin/wypyplus.py
chmod +x cgi-bin/wypyplus.py
wget --recursive \
    --page-requisites \
    --html-extension \
    --convert-links\
    --no-parent http://127.0.0.1:8000/cgi-bin/wypyplus.py
mv cgi-bin/wypyplus_bak.py cgi-bin/wypyplus.py

# Generate an index page
cat << EOF > 127.0.0.1:8000/index.html
<meta http-equiv="Refresh" content="0; url='cgi-bin/wypyplus.py.html'" />
EOF
mv 127.0.0.1:8000 gen_site
echo "Done. Output site to the ./gen_site directory."

