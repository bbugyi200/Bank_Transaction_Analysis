import numpy as np
import pandas as pd


keywords = pd.read_csv('keywords.csv', index_col=None)
filename = '0423-0523.csv'


def getTrans(CSV):
    trans = pd.read_csv(CSV)
    trans.columns = ['date', 'amount', '*', '-', 'description']
    trans.description = trans.description.replace(r'PURCHASE AUTHORIZED ON [0-9]{2}/[0-9]{2}', '', regex=True)
    del trans['*']
    del trans['-']
    trans['category'] = None
    trans['subcategory'] = None
    return trans


def getcats():
    cat = input('category: ')
    sub = input('subcategory: ')
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


def sumamount(df):
    return df['amount'].sum()


def filtercat(df, cat, column='category'):
    return df[df[column] == cat]


trans = getTrans(filename)
analyzeTrans(trans)
exps = trans[trans['amount'] < 0]

cats_group = trans.groupby('category')
subcats_group = trans.groupby(['category', 'subcategory'])

print('\n\n')
print('~~~ Total Expenses ~~~\n{:.2f}\n\n'.format(exps['amount'].sum()))
print('~~~ Category Sums ~~~\n{}\n\n'.format(cats_group.sum()))
print('~~~ Subcategory Sums ~~~\n{}\n'.format(subcats_group.sum()))

pricey = exps[exps['amount'] < -50]
food = filtercat(exps, 'Food')
other = filtercat(exps, 'Other')
entertainment = filtercat(exps, 'Entertainment')
monthly = filtercat(exps, 'Monthly')
deposits = filtercat(trans, 'Deposit')

categories = pd.unique(trans['category'])

# Sums = pd.Series(np.zeros(len(categories)), index=categories)
# for cat in Sums.index:
#     Sums[cat] = sumamount(trans[trans['category'] == cat])

# counts = pd.value_counts(exps['category'])
