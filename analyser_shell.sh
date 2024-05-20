instancecounts=(1)
delays=(0 1)
qoses=(0 1)

python3 make.py

for instancecount in "${instancecounts[@]}"; do
   for publisher_qos in "${qoses[@]}"; do
      for delay in $"${delays[@]}"; do
         echo "Running analyser.py with parameters: $instancecount $publisher_qos $delay $publisher_qos"
         python3 analyser.py "$instancecount" "$publisher_qos" "$delay" "$publisher_qos"
      done
   done
done