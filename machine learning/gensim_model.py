import pandas as pd
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import pymorphy2
nltk.download('punkt')
from gensim.models import Word2Vec
import numpy as np
from gensim.models.doc2vec import Doc2Vec

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

class GensimModel:
    subcategory_name = 'Подкатегория продукции'
    category_sheet = 'Список разделов из ЕП РФ (коды)'
    d2v_model_fname = 'doc2vec_model.pt'
    data_name = 'Общее наименование продукции'

    def __init__(self, path_to_excel):
        self.d2v_model =  Doc2Vec.load(self.d2v_model_fname)

        self.category_df = pd.read_excel(path_to_excel, sheet_name=self.category_sheet)
        categories = []
        for index, row in self.category_df.iterrows():
            categories.append(row[self.subcategory_name])
        
        categories = [make_sent_good(sent) for sent in categories]
        self.category_vec = [self.get_sent_vector(sent) for sent in categories]


    def get_sent_vector(self, sent):
        return self.d2v_model.infer_vector(sent)

    def get_similarity(self, sent):
        vec = self.get_sent_vector(make_sent_good(sent))
        similarity = []
        for i in range(len(self.category_vec)):
            u = vec / np.sum(vec)
            v = self.category_vec[i] / np.sum(self.category_vec[i])
            cosine_similarity = np.sum((v - u)**2)
            similarity.append(cosine_similarity)
        return np.array(similarity)
        
    def predict_single(self, sent):
        similarity = self.get_similarity(sent)
        
        i_min = similarity.argmin()
        similarity /= np.sum(similarity)
        return {'category_num': self.category_df.loc[i_min, 'Раздел ЕП РФ (Код)'],
                'category_name': self.category_df.loc[i_min, 'Категория продукции'],
                'subcategory_num': self.category_df.loc[i_min, 'Раздел ЕП РФ (Код из ФГИС ФСА для подкатегории продукции)'],
                'subcategory_name': self.category_df.loc[i_min, 'Подкатегория продукции'],
                'confidence': 1 - similarity[i_min]
        }

    def predict_df(self, df):
        categories_num = []
        categories_name = []
        subcategories_num = []
        subcategories_name = []
        confidences = []
        for index, row in df.iterrows():
            res = self.predict_single(row[self.data_name])
            categories_num.append(res['category_num'])
            categories_name.append(res['category_name'])
            subcategories_num.append(res['subcategory_num'])
            subcategories_name.append(res['subcategory_name'])
            confidences.append(res['confidence']*100)
        
        new_df = df.copy()
        new_df['Раздел ЕП РФ (Код)'] = categories_num
        new_df['Категория продукции'] = categories_name
        new_df['Раздел ЕП РФ (Код из ФГИС ФСА для подкатегории продукции)'] = subcategories_num
        new_df['Подкатегория продукции'] = subcategories_name
        new_df['Степень уверенности'] = confidences
        return new_df
        

if __name__ == "__main__":
    # s = 'Посуда столовая и кухонная из коррозионностойкой стали для взрослых: термосы, термокружки, термобутылки, термостаканы,'
    m = GensimModel('profsa/Реестр деклараций ПОСУДА ЕП РФ без 4000-8500.xlsx')
    # r = m.predict_single(s)
    # for k, v in r.items():
    #     print(k, v)

    df = pd.read_excel('profsa/Реестр деклараций ПОСУДА ЕП РФ без 4000-8500.xlsx')
    print(df.head())
    res = m.predict_df(df.head())
    res.to_excel('res.xls', index=False)
    

