echo 测试["{\"q\":\"$1\"}"]的意图：
curl -XPOST localhost:5000/parse -d "{\"q\":\"$1\",\"model\":\"latest\"}" 