python /usr/src/app/style.py 

if [ $? -ne 0 ]; then
	echo "Сode style is good"
	exit 1
else
	echo "Code style is bad"
fi
