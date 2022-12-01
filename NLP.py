import html2text, json, string, requests, plotly
import pandas as pd
import plotly.express as px

from flask import render_template
from langcodes import Language
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords

"""Render message as an apology to user."""
def apology(message, code=400, optional=''):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", optional=optional,top=code, bottom=escape(message)), code


def check_language(lang):
    supported_languages = stopwords.fileids()
    full_name = Language.make(language=lang).display_name()
    full_name = full_name.lower()
    if full_name in supported_languages:
        return full_name
    else:
        return 1


'''Create a dictionary of words and frequency distribution'''
def create_freq_dic():
    with open("jsons/words_ns.json", 'r') as fp:
        words_ns = json.load(fp)
    freq_distribution = FreqDist(words_ns)
    freq_d = dict(freq_distribution)
    return freq_d


'''Create a list of words without stopwords'''
def create_ns_list(words, supp_lang):
    stop_words = set(stopwords.words(supp_lang))
    words_ns = [w for w in words if not w.lower() in stop_words]
    return words_ns


'''Create a list of paragraphs'''
def create_paragraph_list(st):
    ans = remove_punctuation(st)
    return ans.split('\n\n')


'''Create a list of sentences'''
def create_sentence_list(st):
    st = remove_punctuation(st, '.')
    return sent_tokenize(st)


'''Create a list of words'''
def create_word_list(st):
    st = remove_punctuation(st)
    return word_tokenize(st)


'''Create a filtered dictionary'''
def filter_dict(freq_d, ranked_list):
    filtered_d = {}
    for word in ranked_list:
        filtered_d[word] = freq_d[word]
    return filtered_d


'''Clean text from Gutenberg infos'''
def first_clean(text):
    with open('original.txt', 'w+') as original, open('cleaned.txt', 'w') as cleaned:

        # Write text into tmp file
        for char in text:
            original.write(char)
        original.seek(0)

        # Find start and end of text
        for i, line in enumerate(original):
            if ("*** START OF" or "***START OF") in line:
                start = i
            elif ("*** END OF" or "***END OF") in line:
                end = i
        original.seek(0)

        # Lines starting with these chars will be avoided
        char_to_avoid = ['#', '*', '!', '_']

        # Write cleaned text into cleaned.txt
        for j, row in enumerate(original):
            if j > start and j < end:
                if not any(row.startswith(x) for x in char_to_avoid):
                    cleaned.write(row)
        original.seek(0)
    return 'cleaned.txt'


def get_cover_url(folder_link, id):
    # Go to image file
    id_h = (id + '-h')
    link_to_test = folder_link + '/' + id_h + '/' "images/cover.jpg"
    # e.g.: 6/7/8/2/67824/67824-h/68283-h/images/cover.jpg

    # Ensure link is working 
    response = requests.get(link_to_test)
    if response.status_code == 200:
        return link_to_test
    else:
        return "https://www.gutenberg.org/gutenberg/pg-logo-129x80.png"


'''Get link to folder of ID'''
def get_link_to_folder(id):

    # Use a mirror as multiple requests to the original site will let me get blocked
    head_link = 'http://eremita.di.uminho.pt/gutenberg/'

    # URL is bookid[0]/[1]..until the second-last, and then the whole ID again
    middle_link = ''
    for i in id[:-1]:  # e.g. 67824
        middle_link = middle_link + str(i) + '/'  # e.g.: 6/7/8/2/
    middle_link = middle_link + id  # e.g.: 6/7/8/2/67824
    folder_link = head_link + middle_link
    return folder_link

'''
# Get an htm
def get_htm(folder_link, id):

    # Go to the htm file
    id_h = (id + '-h')
    link_to_test = folder_link + '/' + id_h + '/' + id_h + '.htm'
    # e.g.: 6/7/8/2/67824/67824-h/68283-h/68283-h.htm

    # Ensure link is working 
    htm = requests.get(link_to_test)
    if htm.status_code == 200:
        htm = htm.text
        return htm
    else:
        return apology("Could not open file", 400)

'''

'''Get text file from gutenberg project'''
def get_text_from_htm(folder_link, id):

    # Go to the htm file
    id_h = (id + '-h')
    link_to_test = folder_link + '/' + id_h + '/' + id_h + '.htm'
    # e.g.: 6/7/8/2/67824/67824-h/68283-h/68283-h.htm

    # Ensure link is working 
    response = requests.get(link_to_test)
    if response.status_code == 200:
        response = response.text
        text = html2text.html2text(response)
        return text
    else:
        return 404
        

'''Create graphic of words withouts stopwords'''
def graphic_bar(dict_ns):
    # Put the dictionary into a DataFrame
    df = pd.DataFrame.from_dict(dict_ns, orient='index', columns=['count']).iloc[0:30]

    # Create a graphic bar with plotly
    fig = px.bar(df, y='count',color='count')
    fig.update_layout({
        "paper_bgcolor":'rgba(0,0,0,0)',
        "plot_bgcolor":'rgba(0,0,0,0)',
        "font_color":"white",
        "title":"30 most frequent words",
        "xaxis_title":"Words (stopwords have been omitted)",
        "yaxis_title":"Count",
        })
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON



'''Remove punctuation from text'''
def remove_punctuation(st, exception=''):  # Default exception is 'nothing' 
    punctuation = string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    punctuation = punctuation.replace(exception, '')  # handle exception if there is any
    for c in st:
        if c in punctuation:  
            st = st.replace(c, '')
    return st


'''Save lists into json files'''
def save_json_files(words, sentences, paragraphs, words_ns):
    with open("jsons/words.json", 'w') as fp:
        json.dump(words, fp, sort_keys=True, indent=4)
    with open("jsons/sentences.json", 'w') as fp:
        json.dump(sentences, fp, sort_keys=True, indent=4)
    with open("jsons/paragraphs.json", 'w') as fp:
        json.dump(paragraphs, fp, sort_keys=True, indent=4)
    with open("jsons/words_ns.json", 'w') as fp:
        json.dump(words_ns, fp, sort_keys=True, indent=4)
    return
