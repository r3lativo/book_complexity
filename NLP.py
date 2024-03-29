import html2text, json, string, requests, plotly, nltk, os
import pandas as pd
import plotly.express as px
from flask import render_template
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords


# Add nltk path
nltk.data.path.append('nltk_data')


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


'''Ensure language is supported by the tokenizer'''
def check_language_manually(lang):
    supported_languages = ['ar', 'az', 'eu', 'bn', 'ca', 'zh', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'el', 'he', 'hinglish', 'hu', 'id', 'it', 'kk', 'ne', 'no', 'pt', 'ro', 'ru', 'sl', 'es', 'sv', 'tg', 'tr']
    full_name = ['arabic', 'azerbaijani', 'basque', 'bengali', 'catalan', 'chinese', 'danish', 'dutch', 'english', 'finnish', 'french', 'german', 'greek', 'hebrew', 'hinglish', 'hungarian', 'indonesian', 'italian', 'kazakh', 'nepali', 'norwegian', 'portuguese', 'romanian', 'russian', 'slovene', 'spanish', 'swedish', 'tajik', 'turkish']
    res = {supported_languages[i]: full_name[i] for i in range(len(supported_languages))}
    if lang in res:
        return res[lang]
    else:
        return 1
        

'''Create graphic of words withouts stopwords'''
def create_bar_graph(dict_ns):
    # Put the dictionary into a DataFrame
    df = pd.DataFrame.from_dict(dict_ns, orient='index', columns=['count']).iloc[0:30]

    # Create a graphic bar with plotly
    fig = px.bar(df, y='count',color='count')
    fig.update_layout({
        "paper_bgcolor":'rgba(0,0,0,0)',  # transparent
        "plot_bgcolor":'rgba(0,0,0,0)',  # transparent
        "font_color":"white",
        "title":"30 most frequent words",
        "xaxis_title":"Words (stopwords have been omitted)",
        "yaxis_title":"Count",
        })
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON



'''Create a dictionary of words and frequency distribution'''
def create_freq_dic():
    with open("jsons/words_ns.json", 'r') as fp:
        words_ns = json.load(fp)
    freq_distribution = FreqDist(words_ns)
    freq_d = dict(freq_distribution)
    return freq_d


'''Create a list of words without stopwords and save as json'''
def create_ns_list(words, supp_lang):
    stop_words = set(stopwords.words(supp_lang))
    words_ns = [w for w in words if not w.lower() in stop_words]
    with open("jsons/words_ns.json", 'w') as fp:
        json.dump(words_ns, fp, sort_keys=True, indent=4)
    return words_ns


'''Create a list of paragraphs and save as json'''
def create_paragraph_list(text):
    ans = remove_punctuation(text)
    paragraphs = ans.split('\n\n')
    with open("jsons/paragraphs.json", 'w') as fp:
        json.dump(paragraphs, fp, sort_keys=True, indent=4)
    return paragraphs


'''Create a list of sentences and save as json'''
def create_sentence_list(text):
    text = remove_punctuation(text, '.')
    sentences = sent_tokenize(text)
    with open("jsons/sentences.json", 'w') as fp:
        json.dump(sentences, fp, sort_keys=True, indent=4)
    return sentences


'''Create a list of words and save as json'''
def create_word_list(text):
    text = remove_punctuation(text)
    words = word_tokenize(text)
    with open("jsons/words.json", 'w') as fp:
        json.dump(words, fp, sort_keys=True, indent=4)
    return words


def delete_temp_files():
    if os.path.exists("original.txt"):
        os.remove("original.txt")
    if os.path.exists("cleaned.txt"):
        os.remove("cleaned.txt")
    if os.path.exists("jsons/paragraphs.json"):
        os.remove("jsons/paragraphs.json")
    if os.path.exists("jsons/sentences.json"):
        os.remove("jsons/sentences.json")
    if os.path.exists("jsons/words.json"):
        os.remove("jsons/words.json")
    if os.path.exists("jsons/words_ns.json"):
        os.remove("jsons/words_ns.json")
    return


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


'''Get cover url'''
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


'''Get link to htm of gutenberg project book'''
def get_link_to_htm(folder_link, id):
    # Go to the htm file
    id_h = (id + '-h')
    link_to_test = folder_link + '/' + id_h + '/' + id_h + '.htm'
    # e.g.: 6/7/8/2/67824/67824-h/68283-h/68283-h.htm

    # Ensure link is working 
    response = requests.get(link_to_test)
    if response.status_code == 200:
        return link_to_test
    else:
        return 404


'''Convert link into text'''
def get_text_from_htm(htm_link):
    # Ensure link is working 
    response = requests.get(htm_link).text
    text = html2text.html2text(response)
    return text


'''Remove punctuation from text'''
def remove_punctuation(text, exception=''):  # Default exception is 'nothing' 
    punctuation = string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    punctuation = punctuation.replace(exception, '')  # handle exception if there is any
    for c in text:
        if c in punctuation:  
            text = text.replace(c, '')
    return text
