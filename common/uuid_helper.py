#-*- coding:utf-8 -*-

import json

def gen_uuid():
	file_path = "./../.cache/alarm.uuid"
	uuid = 0
	with open(file_path, 'r+') as f:
		line = f.readline()
		if line:
			uuid = int(line)+1;
		else:
			uuid = 0;
	with open(file_path, 'w+') as f:
		f.write(str(uuid))
	return uuid

if __name__ == "__main__":
	print(gen_uuid())
