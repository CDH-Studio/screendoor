from screendoor_app.settings import NLP_MODEL

# takes in a sentence, and returns what the applicant claims to have done,
# if anything.
def iterate_through_dep_tree(sent):
    experience = ''
    constructing_verb_phrase = False
    prev_token = sent[0] #initialize the previous token to the first token
    for leaf in sent:
        # Only begin if the root is a verb
        if leaf.dep_ == 'ROOT' and leaf.pos_ == 'VERB':
            subject = None

            # Find the subject the root verb is referring to
            subject_list = [x for x in leaf.children if x.dep_ == 'nsubj'
                            or x.dep_ == 'nsubjpass']

            # If one is found, grab it (will always be first+only element)
            if not subject_list == []:
                subject = subject_list[0]

            if not subject is None:
                # Ensure that the subject is referring to the applicant or
                # a suitable alternative (NEEDS ITERATION)
                if subject.pos_ == 'PRON' and not subject.text == 'It':
                    constructing_verb_phrase = True
            # Note: if no subject is found, it is implied that the applicant
            # refers to themselves anyway (ie. bullet points)
            else:
                constructing_verb_phrase= True
        # Once a valid start to a verb phrase (representing an applicants
        # explanation of their experience, the rest of the phrase should be
        # taken, ending either when the answer extends too long, or goes to
        # another idea.
        if constructing_verb_phrase:
            # Ensures that any composite verb is not lost (ie. was teaching)
            if prev_token.dep_ == 'aux' and \
                    not (prev_token.text in experience):
                experience += ' ' + prev_token.text

            # Checks if the sentence should trail off (gone too long),
            # by checking for commas and ands under specific circumstances
            if leaf.text == ',' or leaf.text == 'and':
                if (not leaf.head == prev_token and
                        not len(list(leaf.head.children)) <= 1):
                    experience += "..."
                    break
            # Helps in the formatting of spaces, but will need to be revisited.
            if leaf.pos_ == 'PUNCT':
                experience += leaf.text
            else:
                experience += ' ' + leaf.text
        prev_token = leaf
    return experience



def extract_how(text):
    doc = NLP_MODEL(text.replace('\n', ' '))

    experience_list = []
    for sent in doc.sents:
        experience = iterate_through_dep_tree(sent)
        if not experience == '':
            experience_list.append(experience)
    print(experience_list)
