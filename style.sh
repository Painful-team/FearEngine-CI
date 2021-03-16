python /fear-engine-CI/style.py 

if [ $? -ne 0 ]; then
	echo "Your code style is shit, bro"
	exit 1
else
	echo "Your code is fucking style, bro"
fi
