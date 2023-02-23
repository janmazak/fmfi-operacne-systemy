#!/bin/sh
echo "<html><body><table>"
echo "<tr><td>Testcase</td><td>Name</td><td>Run #1 (real/user/sys)</td><td>Run #2 (real/user/sys)</td><td>Run#3 (real/user/sys)</td></tr>"
sed -re 's#\d27\[0;31m([^\t]+)\d27\[00m#<span style="color: red">\1</span>#g' |
sed -re 's#\d27\[0;32m([^\t]+)\d27\[00m#<span style="color: green">\1</span>#g' |
sed -re "s/\d27\[00m//g" -e "s/\d27\[0;[0-9]+m//g" | sed -re 's#(\w+)\W+(\w+)[\t ]+(.+)\t(.+)\t(.+)\t#<tr><td>\1</td><td>\2</td><td>\3</td><td>\4</td><td>\5</td></tr>\n#g'

echo "</body></html></table>"

