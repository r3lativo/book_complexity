# Book complexity
#### Video Demo:  <https://youtu.be/RTX6woiCIGM>
#### Description:
The aim of my project was to fulfill CS50 requirements while dipping my toes in NLP, as I want to dive into thata field.

The project is divided in two .py files: app.py and NLP.py.

##### app.py stores the main web app:
it's where flask and SQL are mainly used.
There are five routes:

###### "/", the home page
Here I simply explain the project to users via html layout and invite them to try it out

###### "/analysis", where the magic happens.
Analysis takes a little to load: it stores the info on the book, checks whether the language of the book is supported by the tokenizer and the proceeds to download the book, clean it and analyse its components.
The language support check is essential as the data shown is based on the words in the book minus the stopwords of that language, e.g.: 'the', 'a', 'if', etc.
Once that is assured, it proceeds to download the book from the htm file with html2text: if it doesn't exist it will return an apology.
Finally it comes the interesting part: I noticed that each book of the Project Gutenberg starts and ends with some specific tags, namely "START OF {{title}}" and same for the end. I exploited this feature to make a first clean of the book.
At this point, with only the actual content of the book left, it parses it more efficiently utilising the nltk component for python. In this way the program creates a list of words, of sentences, of paragraphs... to furtherly analyse and present to the final user.
For a better analysis I decided to study and use .json files: this let me create dictionaries of words and frequency in the book.
Finally, the program converts the dictionary into a dataframe that can be translated into a bar chart via plotly.

###### "/contact",
a simple page to let others contact me


###### "/r_book",
where I would like to directly embedd a random book from the Gutenberg Project into my site, and let users read it straightforwardedly.

###### "/search", where the user makes is or her search.
the search starts by choosing what one wants to search: whether for a title, author or ID in the Project Gutenberg catalog. If the search returns no item, the user is redirected to an apology message (taken from pset9) and invited to search again. Else if the search is successful, the site shows the first ten elements ordered by author.
I would have liked to present more data and/or let user choose how to order it, but it was too hard for me as I wanted to focus more on the content extracted by the book once it is found.
From the results, one can go to the book page in the Gutenberg Project (the mirror in Portugal) or analyse it.
    

##### NLP.py, where all the other functions live
Here there are a plenty of function for a lot of uses:
I took apology from the pset9;
there are a lot of functions to create lists of words, sentences;
some gather data from internet, like a cover book or the book itself;
another functions create the graphic bars table.

##### Design
I chose a dark theme as I use it whenever possible, it feels more simple.
I chose orange as the color theme because it's soft and it doesn't have any bad perception related to it in the majority of cultures around the world. 

##### Final thoughts
This project is far from being perfect, but it mainly accomplishes what I want, that is gather info from books and present them to the final user.
I struggled the most trying to implement features that still are out of reach for me, but I learned to stick with simple but functional features.
The main issueas are, I believe, the insufficient query search and the load times - but I know that these are minor issues that can be improved once I have a better grasp of Web-apps in general.

Thank you, CS50.