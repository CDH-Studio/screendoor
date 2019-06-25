from screendoor_app.settings import NLP_MODEL
from .whenextraction import get_identified_dates

def iterate_through_dep_tree(sent):
    experience = ''
    constructing_verb_phrase = False
    prev_token = sent[0] #initialize the previous token to the first token
    next_token_index = 1
    next_token = None
    for leaf in sent:
        if leaf.dep_ == 'nsubj' and (leaf.pos_ == 'NOUN' or leaf.pos_ == 'PROPN'):
            return ''
        # Only begin if the root is a verb
        # If we're looking at a date, we've overstepped into the when_extraction
        # Break
        # if leaf in dates:
        #     return ''

        # Find the subject the root verb is referring to
        subject = None

        if (next_token_index) < len(sent):
            next_token = sent[next_token_index]

        subject_list = [x for x in leaf.children if x.dep_ == 'nsubj'
                            or x.dep_ == 'nsubjpass']


        # If one is found, grab it (will always be first+only element)
        if not subject_list == []:
            subject = subject_list[0]

        # ensures that any verb referring to themselves is taken, no matter
        # what else (I was..., I did..., I created....)
        if not subject is None:
            if subject.text == 'I':
                constructing_verb_phrase = True


        if (leaf.pos_ == 'VERB' and not leaf.text == 'was' or leaf.text == 'has' and not (leaf.dep_ == 'relcl' or leaf.dep_ =='xcomp')):
            if not subject is None:
                # Ensure that the subject is referring to the applicant or
                # a suitable alternative (NEEDS ITERATION)
                if subject.pos_ == 'PRON' and not subject.text == 'It':
                    constructing_verb_phrase = True
            # Note: if no subject is found, it is implied that the applicant
            # refers to themselves anyway (ie. bullet points)
            else:
                head_list = [x for x in leaf.head.children if x.dep_ == 'det']
                if head_list == []:
                    constructing_verb_phrase= True

        # Once a valid start to a verb phrase (representing an applicants
        # explanation of their experience, the rest of the phrase should be
        # taken, ending either when the answer extends too long, or goes to
        # another idea.
        if constructing_verb_phrase:
            # Ensures that any composite verb is not lost (ie. was teaching)
            if ((prev_token.dep_ == 'aux' or prev_token.dep_ == 'auxpass')
                    and not prev_token.text in experience):
                experience += ' ' + prev_token.text

            # Checks if the sentence should trail off (gone too long),
            # by checking for commas and ands under specific circumstances
            if leaf.text == ',' or leaf.text == ';':
                if (not leaf.head == prev_token and
                        not len(list(leaf.head.children)) <= 1) and(not leaf.dep_ == 'prep' or next_token.dep_ == 'conj'):
                    experience += "...¿"
                    constructing_verb_phrase = False
                    continue

            # if (leaf.text == 'that'):
            #     experience += "..."
            #     break

            # Helps in the formatting of spaces, but will need to be revisited.
            if leaf.text == '.' or leaf.pos_ == 'PUNCT' or prev_token.text == "(" or experience == '' or leaf.text == ')':
                experience += leaf.text
            else:
                experience += ' ' + leaf.text
        prev_token = leaf
        next_token_index+=1
    return experience.split('¿')



def extract_how(text):
    doc = NLP_MODEL(text.replace('\n', ' '))
    dates = get_identified_dates(doc)
    experience_list = []
    for sent in doc.sents:
        experience = iterate_through_dep_tree(sent)

        if not experience == []:
            for exp in experience:
                experience_list.append(exp)

    return experience_list
