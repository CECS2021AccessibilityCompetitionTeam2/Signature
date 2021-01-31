import os
import subprocess
import stanza
import time

stanza.download("en")
nlp = stanza.Pipeline('en', processors='tokenize,mwt,pos,lemma,depparse', use_gpu=True, pos_batch_size=3000)# Build the pipeline, specify part-of-speech processor's batch size

def parse(text):
    # Process text input
    doc = nlp(text)  # Run the pipeline on text input


    for sentence in doc.sentences:

        translation = translate(sentence)

        result = []
        for word in translation[0]:
            result.append((word['text'].lower(), word['lemma'].lower()))
        print("\nResult: ", result, "\n")

        # display(translation)

    return doc


def wordToDictionary(word):
    dictionary = {
        'index': word.id,
        'governor': word.head,
        'text': word.text.lower(),
        'lemma': word.lemma.lower(),
        'upos': word.upos,
        'xpos': word.xpos,
        'dependency_relation': word.deprel,
        'feats': word.feats,
        'children': []
    }
    return dictionary


def getMeta(sentence):
    # sentence.print_dependencies()
    englishStruct = {}
    aslStruct = {
        'rootElements': [],
        'UPOS': {
            'ADJ': [], 'ADP': [], 'ADV': [], 'AUX': [], 'CCONJ': [], 'DET': [], 'INTJ': [], 'NOUN': [], 'NUM': [],
            'PART': [], 'PRON': [], 'PROPN': [], 'PUNCT': [], 'SCONJ': [], 'SYM': [], 'VERB': [], 'X': []
        }
    }
    reordered = []
    # aslStruct["rootElements"] = []

    # Make a list of all tokenized words. This step might be unnecessary.
    words = []
    for token in sentence.tokens:
        for word in token.words:

            # print(word.index, word.governor, word.text, word.lemma, word.upos,
            #       word.dependency_relation)  # , word.feats)
            # # Insert as dict
            # words.append(wordToDictionary(word))
            # Insertion sort
            j = len(words)
            for i, w in enumerate(words):
                if word.head <= w['governor']:
                    continue
                else:
                    j = i
                    break
            # Convert to Python native structure when inserting.
            words.insert(j, wordToDictionary(word))
    # # Python sort for converted words
    # words.sort(key=attrgetter('governor', 'age')) # , reverse=True
    # words.sort(key=words.__getitem__) # , reverse=True
    reordered = words

    # Deprecated aslStruct code...
    # While there exist words that haven't been added to the tree.
    # englishStruct['root'] = wordToDictionary(words[0])
    #     # Create list of words for each UPOS
    #     aslStruct['UPOS'][word.upos].append(word)
    #
    # # Sort each UPOS list
    # # print(aslStruct['UPOS'])
    # for upos, uposList in aslStruct['UPOS'].items():
    #   # print(upos, uposList)
    #   uposList.sort(key=attrgetter('governor'))
    #   print(upos, uposList)

    # Identify Root Elements
    # for word in token.words:
    # if word.dependency_relation == "root":
    # aslStruct["rootElements"].append(word)
    # Get related elements
    # Ident topics & comments

    # print("\n", aslStruct, "\n")
    return reordered


def getLemmaSequence(meta):
    tone = ""
    translation = []
    for word in meta:
        # Remove blacklisted words
        if (word['text'].lower(), word['lemma'].lower()) not in (
        ('is', 'be'), ('the', 'the'), ('of', 'the'), ('is', 'are'), ('by', 'by'), (',', ','), (';', ';'), (':'), (':')):

            # Get Tone: get the sentence's tone from the punctuation
            if word['upos'] == 'PUNCT':
                if word['lemma'] == "?":
                    tone = "?"
                elif word['lemma'] == "!":
                    tone = "!"
                else:
                    tone = ""
                continue

            # Remove symbols and the unknown
            elif word['upos'] == 'SYM' or word['upos'] == 'X':
                continue

            # Remove particles
            if word['upos'] == 'PART':
                continue

            # Convert proper nouns to finger spell
            elif word['upos'] == 'PROPN':
                fingerSpell = []
                for letter in word['text'].lower():

                    spell = {}
                    spell['text'] = letter
                    spell['lemma'] = letter
                    # Add fingerspell as individual lemmas
                    fingerSpell.append(spell)



            # Numbers
            elif word['upos'] == 'NUM':
                translation.append(word)


            # Interjections usually use alternative or special set of signs
            elif word['upos'] == 'CCONJ':
                translation.append(word)

            # Interjections usually use alternative or special set of signs
            elif word['upos'] == 'SCONJ':
                if (word['text'].lower(), word['lemma'].lower() not in (('that', 'that'))):
                    translation.append(word)

            # Interjections usually use alternative or special set of signs
            elif word['upos'] == 'INTJ':
                translation.append(word)

            # Adpositions could modify nouns
            elif word['upos'] == 'ADP':
                # translation.append(word)
                pass

            # Determinants modify noun intensity
            elif word['upos'] == 'DET':
                pass

            # Adjectives modify nouns and verbs
            elif word['upos'] == 'ADJ':
                translation.append(word)
                # pass

            # Pronouns
            elif word['upos'] == 'PRON':
                translation.append(word)

            # Nouns
            elif word['upos'] == 'NOUN':
                translation.append(word)

            # Adverbs modify verbs, leave for wh questions
            elif word['upos'] == 'ADV':
                translation.append(word)

            elif word['upos'] == 'AUX':
                pass

            # Verbs
            elif word['upos'] == 'VERB':
                translation.append(word)

    # translation = tree
    return (translation, tone)


def translate(parse):
    meta = getMeta(parse)
    translation = getLemmaSequence(meta)
    return translation


def display(translation):
    folder = os.getcwd()
    filePrefix = folder + "/videos/"
    # Alter ASL lemmas to match sign's file names.
    # In production, these paths would be stored at the dictionary's database.
    files = [filePrefix + word['text'].lower() + "_.mp4" for word in translation[0]]
    # Run video sequence using the MLT Multimedia Framework
    print("Running command: ", ["melt"] + files)
    process = subprocess.Popen(["melt"] + files + [filePrefix + "black.mp4"], stdout=subprocess.PIPE)
    result = process.communicate()


def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line



def main():


    # tests = [
    #     "Where is the bathroom?",
    #      "What is your name?",
    #      "Bring your computer!",
    #      "It's lunch time!",
    #      "Small dogs are cute",
    #      "Dogs are cute because are small.",
    #      "My name is Javier.",
    #      "Search in a binary tree is big Oh of log n"
    #     ]
    #
    # for text in tests:
    #     print("Text to process: ", text, "\n")
    #     parse(text)

    logfile = open("transcript.md", "r")
    loglines = follow(logfile)
    for line in loglines:
        parse(line)

if __name__ == "__main__":
    main()