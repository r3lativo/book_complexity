import NLP, random
from flask import Flask, render_template, request
from cs50 import SQL


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///catalog.db")


'''Main page'''
@app.route("/")
def index():
    return render_template("index.html")


'''Analysis page'''
@app.route("/analysis")
def analysis():

    # Get Book ID
    id = request.args.get('id', None)

    info = db.execute("SELECT title, authors, language FROM catalog WHERE id = ? AND type = 'Text'", id)
    title = info[0]['title']
    author = info[0]['authors']
    lang = info[0]['language']

    # Check whether the language is supported
    supp_lang = NLP.check_language_manually(lang)
    if supp_lang == 1:
        return NLP.apology("Language not supported :(", 400, 'Try with another book!')

    # Get link to the htm
    folder_link = NLP.get_link_to_folder(id)
    htm_link = NLP.get_link_to_htm(folder_link, id)
    if htm_link == 404:
        return NLP.apology("File not found", 404, 'Try with another book!')

    # Convert htm to text
    gutenberg_text = NLP.get_text_from_htm(htm_link)

    # Clean text from Gutenberg things
    cleaned_file = NLP.first_clean(gutenberg_text)

    # Open file and create data to show
    with open(cleaned_file) as file:
        text = file.read()
        words = NLP.create_word_list(text)
        # sentences = NLP.create_sentence_list(text)
        # paragraphs = NLP.create_paragraph_list(text)
        words_ns = NLP.create_ns_list(words, supp_lang)

    # Get cover, if exists
    # cover = NLP.get_cover_url(folder_link, id)

    # Create a frequency dictionary based on WORDS WITHOUT STOP (words_ns)
    freq_d_ns = NLP.create_freq_dic()
    ranked_list_ns = sorted(freq_d_ns, key=freq_d_ns.get, reverse=True)
    dict_ns = NLP.filter_dict(freq_d_ns, ranked_list_ns)
    
    # Create graphic of words withouts stopwords
    graphJSON = NLP.create_bar_graph(dict_ns)

    # Some counts to show
    words_ns_count = len(words_ns)
    # s_count = len(sentences)
    # p_count = len(paragraphs)

    NLP.delete_temp_files()
        
    return render_template("analysis.html", graphJSON=graphJSON, title=title, author=author, words_ns_count=words_ns_count, folder_link=folder_link) #s_count=s_count, p_count=p_count, cover=cover, 


'''Contact page'''
@app.route("/contact")
def contact():
    return render_template("contact.html")


'''Random book page'''
@app.route("/r_book")
def r_book():

    # Select IDs of texts
    text_ids = db.execute("SELECT id FROM catalog WHERE type = 'Text'")
    cleaned_ids = []
    for i in text_ids:
        cleaned_ids.append(i['id'])

    # Pick a random text to show
    r_id = random.choice(cleaned_ids)
    r_info = db.execute("SELECT title, authors FROM catalog WHERE id = ?", r_id)

    # Extract infos
    title = r_info[0]['title']
    author = r_info[0]['authors']

    # Get the htm file
    folder_link = NLP.get_link_to_folder(r_id)
    htm_link = NLP.get_link_to_htm(folder_link, r_id)

    return render_template("r_book.html", htm_link= htm_link, title=title, author=author)


'''Search page'''
@app.route("/search", methods = ["GET", "POST"])
def search():
    # Options permitted
    options = ['title', 'authors', 'id']

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Retrieve user input
        filter = request.form.get("filter")
        query = request.form.get("query")

        # Ensure symbol or shares are not missing
        if not filter:
            return NLP.apology("missing option", 400)
        elif not query:
            return NLP.apology("missing query", 400)

        # Ensure user owns that shares
        if filter not in options:
            return NLP.apology("option unauthorized", 400)

        # Search and get info
        all = db.execute("SELECT * FROM catalog WHERE "+filter+" LIKE ? AND type = 'Text' ORDER BY authors LIMIT 30", '%'+query+'%')

        # If the query doesn't give anything back
        if len(all) == 0:
            return NLP.apology("No corresponding item :(", 404, "Search again")

        # Store information
        authors, ids, languages, titles = [], [], [], []
        for i in all:
            authors.append(i['authors'])
            ids.append(i['id']) 
            titles.append(i['title'])
            languages.append(i['language'])

        # Store folder links to show
        folder_links = []
        for id in ids:
            folder_links.append(NLP.get_link_to_folder(id))
        
        return render_template("results.html", titles=titles, ids=ids, authors=authors, languages=languages, folder_links=folder_links, all=all)

    else:
        return render_template("search.html", options=options)
    
