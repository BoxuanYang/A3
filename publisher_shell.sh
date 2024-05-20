# 循环运行 publisher.py，传递参数从 1 到 5
for i in {1..5}
do
   echo "i is $i"
   python3 publisher.py $i &
done

