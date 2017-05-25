import numpy as np
import pandas as pd


keywords = pd.read_csv('keywords.csv', index_col=None)
filename = 'data/0423-0523.csv'


def getTrans(CSV):
    trans = pd.read_csv(CSV)
    trans.columns = ['date', 'amount', '*', '-', 'description']

    # Clean Data
    del trans['*']
    del trans['-']
    trans['date'] = pd.to_datetime(trans.date)
    trans.set_index('date', inplace=True)
    trans.description = trans.description.replace(r'PURCHASE AUTHORIZED ON [0-9]{2}/[0-9]{2}', '', regex=True)

    # Append new columns
    trans['category'] = None
    trans['subcategory'] = None
    trans['keyword'] = None
    return trans


def getcats():
    cat = input('Category: ')
    sub = input('Subcategory: ')
    key = input('Keyword: ')
    print('\n')
    return (key, cat, sub)


def analyzeTrans(trans):
    global keywords
    for i in range(len(trans)):
        match = ''
        for j, key in enumerate(keywords['keyword']):
            if key.lower() in trans['description'][i].lower():
                assert match == '', "MULTIPLE KEYWORD MATCH: ('{0}', '{1}')".format(match, key)
                trans['category'][i] = keywords.ix[j]['category']
                trans['subcategory'][i] = keywords.ix[j]['subcategory']
                trans['keyword'][i] = keywords.ix[j]['keyword']
                match = key
        if match:
            continue
        else:
            print(trans.ix[i], '\n')
            key, cat, sub = getcats()
            NewKey = pd.Series({'category': cat, 'subcategory': sub, 'keyword': key})
            keywords = keywords.append(NewKey, ignore_index=True)
            keywords.sort_values(['category', 'subcategory', 'keyword'], inplace=True)
            keywords.to_csv('keywords.csv', index=False)

            trans['category'][i] = cat
            trans['subcategory'][i] = sub


def filtercat(df, cat, column='category'):
    return df[df[column] == cat]


trans = getTrans(filename)
analyzeTrans(trans)
exps = trans[trans['amount'] < 0]

groups = dict()
groups['cats'] = trans.groupby('category')
groups['subcats'] = trans.groupby(['category', 'subcategory'])
groups['keys'] = trans.groupby(['category', 'subcategory', 'keyword'])


verbose = False
if verbose:
    print('\n\n')
    print('~~~ Total Expenses ~~~\n{:.2f}\n\n'.format(exps['amount'].sum()))
    print('~~~ Category Sums ~~~\n{}\n\n'.format(groups['cats'].sum()))
    print('~~~ Subcategory Sums ~~~\n{}\n'.format(groups['subcats'].sum()))


pricey = exps[exps['amount'] < -50]
food = filtercat(exps, 'Food')
other = filtercat(exps, 'Other')
entertainment = filtercat(exps, 'Entertainment')
monthly = filtercat(exps, 'Monthly')
deposits = filtercat(trans, 'Deposit')
