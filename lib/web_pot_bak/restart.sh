ps -ef | grep "python api.py 10123"  | grep -v grep | awk '{print $2}' | xargs kill -9
#nohup python api.py 10123 &
python api.py 10123 &

