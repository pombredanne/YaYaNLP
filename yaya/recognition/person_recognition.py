# coding=utf-8
from yaya.collection.dict import Attribute, Searcher
from yaya.collection.hmm import PersonTranMatrix
from yaya.common.nature import NATURE
from yaya.common.nr import NR
from yaya.config import Config
from yaya.dictionary.person_dict import PersonDict, NRPatternDict
from yaya.seg.viterbi import viterbi_template
from yaya.seg.wordnet import Vertex

__author__ = 'tony'

def recognition(vertexs, wordnet_optimum, wordnet_all):

    # 识别角色，并进行一次维特比
    tag_list = role_tag(vertexs)
    if Config.debug:
        sb = []
        for i, v in enumerate(vertexs):
            sb.append("[%s %s]" % (unicode(vertexs[i]), tag_list[i].nature))
        print u"人名角色观察:%s" % "".join(sb)
    tag_list = viterbi_template(tag_list, PersonTranMatrix().hmm)


    tag_str = [str(x) for x in tag_list]
    tag_str = ''.join(tag_str)

    #
    parse_pattern(tag_str, vertexs, None, None)

    search = Searcher(NRPatternDict().trie, tag_str)
    vertexs_offset = [0] * len(vertexs)
    offset = 0
    for i in range(1, len(vertexs) - 2):
        vertexs_offset[i] = offset
        offset += len(vertexs[i].real_word)
    while search.next():
        name_str = ""
        for i in range(search.begin, search.begin + len(search.value)):
            name_str += vertexs[i].real_word

        # 添加到词网内
        vertex = Vertex(name_str, attribute="nr 1")
        wordnet_optimum.add(vertexs_offset[search.begin + 1], vertex)
        # vertexs = viterbi(wordnet_optimum.vertexs)
        # return vertexs


def role_tag(word_seg_list):
    tag_index_list = []
    for vertex in word_seg_list:
        if vertex.nature == NATURE.nr.index and vertex.attribute.total_frequency <= 1000:
            if vertex.real_word.__len__() == 2:
                tag_index_list.append(Attribute("%s %s 1 %s 1" % (vertex.real_word, NR.X, NR.G), NR))
                continue
        index, value = PersonDict().trie.get(vertex.real_word)
        if value is None:
            value = Attribute([str(NR.A), PersonDict().matrix.get_total_freq(NR.A)], cls=NR)
        # else:
        #     if not isinstance(value, list):
        #         value = value.split()
        #     value = Attribute(value[1:], cls=NR)
        tag_index_list.append(value)
    return tag_index_list


def parse_pattern(tag_str, vertexs, wordnet_optimum, wordnet_all):
    new_tag_list = []
    new_vertexs = []
    for i, t in enumerate(tag_str):
        if t == str(NR.U):
            new_tag_list.append(str(NR.K))
            new_tag_list.append(str(NR.B))
            word_K = vertexs[i].real_word[:-1]
            word_B = vertexs[i].real_word[-1]
            new_vertexs.append(Vertex(word_K))
            new_vertexs.append(Vertex(word_B))
        elif t == str(NR.V):
            if tag_str[i - 1] == str(NR.B):
                new_tag_list.append(str(NR.E))
            else:
                new_tag_list.append(str(NR.D))
            new_tag_list.append(str(NR.L))
            word_ED = vertexs[i].real_word[:-1]
            word_L = vertexs[i].real_word[-1]
            new_vertexs.append(Vertex(word_ED))
            new_vertexs.append(Vertex(word_L))
        else:
            new_tag_list.append(t)
            new_vertexs.append(vertexs[i])
    vertexs = new_vertexs
    tag_str = "".join(new_tag_list)
