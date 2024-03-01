from ieml.syntax import Sentence, Clause
from ieml.dictionary import term
from ieml.syntax import Morpheme, Word
from ieml.syntax.terms import SyntaxTerm


def get_test_word_instance():
    morpheme_subst = Morpheme(map(SyntaxTerm, [term("a.i.-"), term("i.i.-")]))
    morpheme_attr = Morpheme(map(SyntaxTerm, [term("E:A:T:."), term("E:S:.wa.-"),term("E:S:.o.-")]))
    return Word(morpheme_subst, morpheme_attr)

def get_test_morpheme_instance():
    morpheme = Morpheme(map(SyntaxTerm, [term("E:A:T:."), term("E:S:.wa.-"),term("E:S:.o.-")]))
    return morpheme

def get_words_list():
    #this list is already sorted
    terms_list = [term("E:A:T:."), term("E:.S:.wa.-"), term("E:.-S:.o.-t.-'"), term("a.i.-"), term("i.i.-"),  term("u.M:M:.-")]

    # a small yield to check the word before returning it :-°
    for t in terms_list:
        word_obj = Word(Morpheme(SyntaxTerm(t)))
        yield word_obj

def get_test_sentence():
    a, b, c, d, e, f = tuple(get_words_list())
    clause_a, clause_b, clause_c, clause_d = Clause(a,b,f), Clause(a,c,f), Clause(b,d,f), Clause(b,e,f)
    sentence = Sentence([clause_b, clause_a, clause_d, clause_c])
    return sentence

