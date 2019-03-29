import sys,io
reload(sys)
#sys.setdefaultencoding('utf-8')

#测试一下这个md文件中不能有gbk的编码文字，必须都得是unicode的，否则报错
print sys.getdefaultencoding()
filename = "../stories.md"
with io.open(filename, "r") as f:
     lines = f.readlines()
     print "done"
