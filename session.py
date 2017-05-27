import pandas as pd
import string
import os


try:
    keywords = pd.read_csv('keywords.csv', index_col=None)
except FileNotFoundError:
    keywords = pd.DataFrame({'category': [], 'subcategory': [], 'keyword': []})

filename = 'data/0423-0523.csv'

categories = pd.unique(keywords['category'].str.title())


def getTrans(CSV):
    """ Loads, cleans, and returns trasaction DataFrame.

    This function is heavily customized to the format of the CSV file
    of transactions downloadable from the Wells Fargo website.
    """
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
    trans['class'] = None
    return trans


def getSubs(cat: "category"):
    cat = cat.lower()
    mask = keywords['category'] == cat
    return pd.unique(keywords[mask]['subcategory'].str.title())


def menu(field: "name of field to prompt user for",
         i: "current index of transaction DB",
         seq: "sequence to map to letters" = None):

    os.system('clear')
    print('Date: {}'.format(trans.index[i]),
          'Description: {}'.format(trans.ix[i]['description']),
          'Amount: {}'.format(trans.ix[i]['amount']),
          sep='\n',
          end='\n\n')
    print("Select a {}".format(field.title()), end='')

    if seq is None:
        print(' ', end='')
        mapping = []
    else:
        mapping = dict(zip(string.ascii_uppercase, seq))
        print('\n\n')
        for key, item in mapping.items():
            print(key, ': ', item, sep='')
        print()
    user_input = input('>>> ')
    os.system('clear')
    if user_input in mapping:
        return mapping[user_input].lower()
    elif len(user_input) > 1:
        return user_input.lower()


def analyzeTrans(trans):
    global keywords
    for i in range(len(trans)):
        match = ''
        index = trans.index[i]
        for j, key in enumerate(keywords['keyword']):
            if key in trans.ix[i, 'description'].lower():
                assert match == '', "MULTIPLE KEYWORD MATCH: ('{0}', '{1}')".format(match, key)
                trans.loc[index, 'category'] = keywords.ix[j]['category'].title()
                trans.loc[index, 'subcategory'] = keywords.ix[j]['subcategory'].title()
                trans.loc[index, 'class'] = keywords.ix[j]['keyword'].title()
                match = key
        if match:
            continue
        else:
            print(trans.ix[i], '\n')
            cat = menu('category', i, categories)
            sub = menu('subcategory', i, getSubs(cat))
            key = menu('keyword', i)
            NewKey = pd.Series({'category': cat, 'subcategory': sub, 'keyword': key})
            keywords = keywords.append(NewKey, ignore_index=True)
            keywords.sort_values(['category', 'subcategory', 'keyword'], inplace=True)
            keywords.to_csv('keywords.csv', index=False)

            trans.loc[index, 'category'] = cat.title()
            trans.loc[index, 'subcategory'] = sub.title()
            trans.loc[index, 'class'] = key.title()


def filtercat(df, cat, column='category'):
    return df[df[column] == cat]


trans = getTrans(filename)
analyzeTrans(trans)
exps = trans[trans['amount'] < 0]

groups = dict()
groups['cats'] = trans.groupby('category')
groups['subcats'] = trans.groupby(['category', 'subcategory'])
groups['keys'] = trans.groupby(['category', 'subcategory', 'class'])


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
