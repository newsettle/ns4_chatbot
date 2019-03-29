# -*- coding: UTF-8 -*-
import sys,io,os
from mitie import *
from collections import defaultdict

reload(sys)
sys.setdefaultencoding('utf-8')


#此代码参考：https://github.com/mit-nlp/MITIE/blob/master/examples/python/ner.py
#sys.path.append(parent + '/../../mitielib')
sys.path.append('../MITIE/mitielib')

print("loading NER model...")
ner = named_entity_extractor('../model/default/latest/entity_extractor.dat')
print("\nTags output by this NER model:", ner.get_possible_ner_tags())

# Load a text file and convert it into a list of words.
tokens = tokenize("我们 公司 的 名字 叫 北京 舒望网络 科技 有限公司")
print("Tokenized input:", tokens)

entities = ner.extract_entities(tokens,mitie.total_word_feature_extractor("../data/total_word_feature_extractor_zh.dat"))
print("\nEntities found:", entities)
print("\nNumber of entities detected:", len(entities))

for e in entities:
    range = e[0]
    tag = e[1]
    score = e[2]
    score_text = "{:0.3f}".format(score)
    entity_text = " ".join(tokens[i].decode() for i in range)
    print("   Score: " + score_text + ": " + tag + ": " + entity_text)