#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 13:27:50 2019

@author: aravindjyothi
"""

from flask import Flask, render_template, request, jsonify
from SolrClient import SolrClient
import csv 
from bs4 import BeautifulSoup
solr = SolrClient('http://localhost:8983/solr/')


app = Flask(__name__)

from spellchecker import SpellChecker
spell = SpellChecker()
spell.word_frequency.load_text_file('./big.txt')

urlFileMap = {}
fileUrlMap = {}

with open('URLtoHTML_guardian_news.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        mapping = row[0]
        url = row[1]
        if url not in urlFileMap:
            urlFileMap[url] = mapping
        if mapping not in fileUrlMap:
            fileUrlMap[mapping] = url
    del urlFileMap['URL']
    del fileUrlMap['filename']

mapper_auto = {} 

def get_autocomplete(data):
    total = [] 
    data = data.lower() 
    split_data = data.split()
    if len(split_data) == 1:
        k = data
    if len(split_data) > 1:
        for i in range(len(split_data)-1):
            total.append(mapper_auto.get(split_data[i]))
        k = split_data[-1]
    res = solr.query('myexample',{
            'q': k
            }, request_handler='suggest')
    results = res.data['suggest']['suggest'][k]['suggestions']
    nos = res.data['suggest']['suggest'][k]['numFound']
    if nos != 0:
        lst = []
        for each in results:
            lst.append(each['term'])
        mapper_auto[k] = lst
        total.append(lst)
        slicer = [[['N/A'] for _ in range(len(total))] for _ in range(len(total[0]))]
        for i in range(len(total)):
            for j in range(len(total[0])):
                slicer[j][i] = total[i][j]
        return slicer
    else:
        return 0    

def snippet_generator(ident, q, desc):
    resultant_desc = '' 
    if q in desc:
        resultant_desc = desc 
    resp = open(ident, 'r',  encoding = "utf-8")
    content = resp.read()
    soup = BeautifulSoup(content, 'html.parser')
    p_tags = soup.find_all('p')
    lst = []
    for p in p_tags:
        lst.append(p.text)
    final_text = ' '.join(lst)
    snips = [sentence for sentence in final_text.split('.') if q in sentence]
    for snippet in snips:
        if q in snippet:
            resultant_desc += snippet
            if len(resultant_desc) >= 260:  
                return resultant_desc[:260] + '...' 
            else:
                return resultant_desc + '...' 
    if not resultant_desc: 
        return desc 

@app.route('/')
def index():
	return render_template('form.html')

@app.route('/process', methods=['POST'])
def process():
    query_from_ajax = request.form['query']
    radio_type = request.form['radio']
    if radio_type == 'pagerank':
            res = solr.query('myexample',{
            'q': query_from_ajax,
            'sort': 'pageRankFile desc'
            })
    else:
            res = solr.query('myexample',{
                'q': query_from_ajax
                })
    lst = []

    no_of_docs = res.data['response']['numFound']
    
    if no_of_docs == 0:
        spell_c = spell.correction(query_from_ajax)
        if spell_c == query_from_ajax:
            spell_c = 1
        return jsonify({'lst':lst, 'c':spell_c, 'n':no_of_docs})
    
    else:
        spell_c = spell.correction(query_from_ajax)
        if spell_c == query_from_ajax:
            spell_c = 1
        length = min(10, res.data['response']['numFound']) 
        for index in range(length):
            ident = res.data['response']['docs'][index]['id']
            url_q = res.data['response']['docs'][index]
            if url_q.get('description'):
                desc = res.data['response']['docs'][index]['description'][0]
            else:
                desc = ''
            if url_q.get('og_url'):
                url = res.data['response']['docs'][index]['og_url'][0]
            else:
                pieces = ident.split('/')
                file = pieces[-1]
                url = fileUrlMap.get(file)
            title = res.data['response']['docs'][index]['title'][0]
            snip = snippet_generator(ident, query_from_ajax, desc)
            if snip:
                lst.append((url, title, ident, snip + '...'))
            else:
                lst.append((url, title, ident, 'N/A'))
        return jsonify({'lst' : lst, 'c':spell_c, 'n':no_of_docs})

@app.route('/autocomplete', methods = ['POST'])
def autocomplete():
    if request.method == 'POST':
        data = request.get_json()
        to_suggest = data['d']
        if to_suggest[-1] != " ":
            suggestions = get_autocomplete(data['d'])
        else:
            suggestions = " " 
        print(suggestions)
        return jsonify({'sug':suggestions})
    
if __name__ == '__main__':
	app.run(debug=True)
    
    