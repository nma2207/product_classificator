import pandas as pd
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import pymorphy2
nltk.download('punkt')

import numpy as np
import fasttext


def make_sent_good(sent):
    
    #print(sent)
    tokens = word_tokenize(sent, language="russian")
    #print(tokens)
    filtered_tokens = []
    stop_words = stopwords.words("russian")
    for token in tokens:
        if token not in stop_words and token.isalpha():
#            parsed = morph.parse(token)
#            filtered_tokens.append(parsed[0].normal_form)
            filtered_tokens.append(token.lower())
    return filtered_tokens


class FastTextModel:
    subcategory_name = 'Раздел ЕП РФ (Код из ФГИС ФСА для подкатегории продукции)'
    category_sheet = 'Список разделов из ЕП РФ (коды)'
    model_fname = 'fast_text.pt'
    data_name = 'Общее наименование продукции'

    def __init__(self, path_to_excel):
        self.model = fasttext.load_model(self.model_fname)

        self.category_df = pd.read_excel(path_to_excel, sheet_name=self.category_sheet)
        self.categories = []
        for index, row in self.category_df.iterrows():
            self.categories.append(str(row[self.subcategory_name]))
        #print(self.categories)
    
    def predict_single(self, sent):
        #print(self.category_df)
        sent = make_sent_good(sent)
        
        pred = self.model.predict(' '.join(sent))
        proba = pred[1][0]
        label = pred[0][0][9:]
        #print(type(label))
        #print(type(self.categories[0]))
        if label not in self.categories:
            return {'category_num': 'Ошибка (Не подходит)',
                'category_name': 'Ошибка (Не подходит)',
                'subcategory_num': 'Ошибка (Не подходит)',
                'subcategory_name': 'Ошибка (Не подходит)',
                'confidence': 0
            }
        else:
            idx = self.categories.index(label)
            return {#'category_num': self.category_df.loc[idx, 'Раздел ЕП РФ (Код)'],
                #'category_name': self.category_df.loc[idx, 'Категория продукции'],
                'subcategory_num': self.category_df.loc[idx, 'Раздел ЕП РФ (Код из ФГИС ФСА для подкатегории продукции)'],
                'subcategory_name': self.category_df.loc[idx, 'Подкатегория продукции'],
                'confidence': proba
        }

    def predict_df(self, df):
        categories_num = []
        categories_name = []
        subcategories_num = []
        subcategories_name = []
        confidences = []
        for index, row in df.iterrows():
            res = self.predict_single(row[self.data_name])
            #categories_num.append(res['category_num'])
            #Wcategories_name.append(res['category_name'])
            subcategories_num.append(res['subcategory_num'])
            subcategories_name.append(res['subcategory_name'])
            confidences.append(res['confidence']*100)
        
        new_df = df.copy()
        new_df['Раздел ЕП РФ (Код)'] = ['I dont know',]*len(subcategories_name)
        new_df['Категория продукции'] = ['I dont know',]*len(subcategories_name)
        new_df['Раздел ЕП РФ (Код из ФГИС ФСА для подкатегории продукции)'] = subcategories_num
        new_df['Подкатегория продукции'] = subcategories_name
        new_df['Степень уверенности'] = confidences
        return new_df

if __name__ == "__main__":
    #m = FastTextModel('profsa/Реестр 327 тыс. деклараций ЕП РФ без 140000-200000.xlsx')

    #res = m.predict_single('Вода для инъекций буфус, растворитель для приготовления лекарственных форм для инъекций 5 мл, ампулы полимерные (10), пачки картонные')
    #print(res)
    #df = pd.read_excel('profsa/Реестр 327 тыс. деклараций ЕП РФ без 140000-200000.xlsx')

    #res = m.predict_df(df.head())
    #print(res)
    #res.to_excel('res.xls', index=False)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("f1") #дано
    parser.add_argument("f2") #завтра скинут
    parser.add_argument("f3") #вывод csv
    args = parser.parse_args()

    m = FastTextModel(args.f1)
    #df = pd.read_csv(args.f2)
    df =  pd.read_excel(args.f2)
    res = m.predict_df(df)
    res.to_csv(args.f3, index=False, sep='|')