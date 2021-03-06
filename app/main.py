from flask import Flask, render_template, request, redirect, url_for
import requests
from newsapi import NewsApiClient
import os
import dateutil.parser
import time

app = Flask(__name__)

newsapi = NewsApiClient(api_key=os.environ['NEWSKEY'])
p = 1
req = []
paging = False

@app.route('/')
def home():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404error.html'), 404

@app.route('/entertainment')
def entertainment():
    top_headlines = newsapi.get_top_headlines(
        category='entertainment', page_size=30, country='us', language='en')
    return render_template('entertainment.html', top_headlines=top_headlines['articles'])

@app.route('/tech')
def tech():
    top_headlines = newsapi.get_top_headlines(
        category='technology', page_size=30, country='us', language='en')
    return render_template('tech.html', top_headlines=top_headlines['articles'])

@app.route('/sports')
def sports():
    top_headlines = newsapi.get_top_headlines(
        category='sports', page_size=30, country='us', language='en')
    return render_template('sports.html', top_headlines=top_headlines['articles'])

@app.route('/nextpage', methods=['GET'])
def nextpage():
    global p
    global paging
    if(req != []):
        print(req)
        p += 1
        paging = True

    return redirect('/all')

@app.route('/prevpage', methods=['GET'])
def prevpage():
    global p
    global paging
    if(req != [] and p > 1):
        print(req)
        p -= 1
        paging = True
    return redirect('/all')

def pull_data(fromdate, todate, topicsearch, lang, sort_way, pcheck):
    global p
    results = 0
    articles = []
    if(fromdate == "" and todate == ""):
        all_articles = newsapi.get_everything(
            q=topicsearch, page_size=30, language=lang, sort_by=sort_way, page=p)
    elif(fromdate != "" and todate == ""):
        all_articles = newsapi.get_everything(q=topicsearch, language=lang, from_param=dateutil.parser.parse(fromdate).isoformat(), page_size=30, sort_by=sort_way, page=p)
    elif(fromdate == "" and todate != ""):
        all_articles = newsapi.get_everything(q=topicsearch, language=lang, to=dateutil.parser.parse(
            todate).isoformat(), page_size=30, sort_by=sort_way, page=p)
    else:
        all_articles = newsapi.get_everything(q=topicsearch, language=lang, from_param=dateutil.parser.parse(
            fromdate).isoformat(), to=dateutil.parser.parse(todate).isoformat(), page_size=30, sort_by=sort_way, page=p)
    results = all_articles['totalResults']
    articles = all_articles['articles']
    page = int(p)
    if(pcheck == "yes"):
        for article in articles:
            if "paywall" in requests.get(article['url']).text:
                print("paywall found for ", article['title'])
                article['paywall'] = 'yes'
    return [results, articles, page]

@app.route('/all', methods=['GET', 'POST'])
def entertainment_all():
    print('e all')
    global p
    global req
    global paging
    print(paging)
    if request.method == 'POST':
        p = 1
        req = [request.form['fromdate'], request.form['todate'], request.form['topicsearch'], request.form['lang'], request.form['sort'], request.form['paywallcheck']]
        print(req)
        data = pull_data(req[0], req[1], req[2], req[3], req[4], req[5])
        return render_template('all_articles.html', results=data[0], all_articles=data[1], page=data[2])
    elif paging:
        data = pull_data(req[0], req[1], req[2], req[3], req[4])
        return render_template('all_articles.html', results=data[0], all_articles=data[1], page=data[2])
    else:
        p = 1
        paging = False
        return render_template('all_articles.html', results=0, all_articles=[], page=p)




@app.context_processor
def date_processor():
    def format_date(datestamp):
        date = dateutil.parser.parse(datestamp)
        return "{} {}, {} at {}:{}".format(date.strftime("%B"), date.strftime("%d"), date.strftime("%Y"), date.strftime("%H"), date.strftime("%M"))
    return dict(format_date=format_date)

@app.context_processor
def content_processor():
    def format_content(content):
        if content == None:
            return "We couldn't get this article's content. Sorry!"
        return str(content)[0:200]
    return dict(format_content=format_content)