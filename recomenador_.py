# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 11:22:12 2022

@author: Anna
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import random 

books_df = pd.read_csv('C:/Users/Anna/Desktop/projecte_gestio_llibres/Books.csv')
ratings_df = pd.read_csv('C:/Users/Anna/Desktop/projecte_gestio_llibres/Ratings.csv')
users_df = pd.read_csv('C:/Users/Anna/Desktop/projecte_gestio_llibres/Users.csv')

#Creem columna de generes(aleatoriament)
ll_genere= ['aventuras', 'ciencia-ficción','hadas','gótica','policíaca','paranormal', 'distópica', 'fantástica', 'terror', 'misterio', 'romantica', 'histórica','infantil']
books_df['genere'] = random.choices(ll_genere , k=len(books_df))

                                  
#JUNTAR TODOS LOS DATASETS:
books_data = books_df.merge(ratings_df, on = "ISBN")
books_data.head()

#ELIMINAR LAS FILAS CON ALGUN NAN
books_data.dropna(inplace=True)


#USUARI AMB EL QUE TREBALLAREM:
USER_8=books_data[books_data['User-ID']==11676]

USER_8=USER_8[['Book-Title', 'Book-Rating', 'ISBN']]


#Filtrar a los usuarios que han visto películas que la entrada ha visto y almacenarlas 
userSubset = books_data[books_data['ISBN'].isin(USER_8['ISBN'].tolist())]
#Groupby crea varios sub dataframes de datos donde todos tienen el mismo valor en la columna especificada #como parámetro 
userSubsetGroup = userSubset.groupby(['User-ID'])
userSubsetGroup = sorted(userSubsetGroup, key=lambda x: len(x[1]), reverse=True)
userSubsetGroup = userSubsetGroup[1:100]

llista_posibles_llibres = pd.DataFrame(columns=['Book-Title', 'User-ID', 'ISBN'])

if len(userSubsetGroup)!=0:

    
    pearsonCorrelationDict = {}
    #Para cada grupo de usuarios de nuestro subconjunto 
    for ID, other in userSubsetGroup:
        
        othersBooks= other.sort_values(by='ISBN')
        usuariBooks= USER_8.sort_values(by='ISBN')
        
       
        temp_df = usuariBooks[usuariBooks['ISBN'].isin(othersBooks['ISBN'].tolist())]
        
        
        
        tempRatingList = temp_df['Book-Rating'].tolist()
        
        
        
        tempGroupList = othersBooks['Book-Rating'].tolist()
        
        
        
        data_corr = {'tempGroupList': tempGroupList,'tempRatingList': tempRatingList}
        
        pd_corr = pd.DataFrame(data_corr)
        
        r = pd_corr.corr(method="pearson")["tempRatingList"]["tempGroupList"]
        
    
        if math.isnan(r) == True:
            r = 0
        pearsonCorrelationDict[ID] = r
        
        
    #Convertimos el diccionario a un dataframe:         
    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
    pearsonDF.columns = ['Correlació']
    pearsonDF['User-ID'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))
    pearsonDF.head()
    
    
    
    pearsonDF = pearsonDF[pearsonDF['Correlació']>0]
    if len(pearsonDF)>5:
        pearsonDF = pearsonDF[0:5]
        
        
    
    long= len(pearsonDF)
    
    
    if long!=0:
        operacio= 5//long
    
        
    
        for book in pearsonDF['User-ID']:
            
            USER_OTHER = books_data[books_data['User-ID']==book]
            
            # els llibres que no tenen en comú:
            USER_OTHER = USER_OTHER[~USER_OTHER['ISBN'].isin(USER_8['ISBN'].tolist())]
            USER_OTHER = USER_OTHER[~USER_OTHER['ISBN'].isin(llista_posibles_llibres['ISBN'])]
            USER_OTHER = USER_OTHER.sort_values(by='Book-Rating')
            nou_llibre = USER_OTHER[['ISBN', 'User-ID','Book-Title']][0:operacio]
            llista_posibles_llibres = pd.concat([llista_posibles_llibres, nou_llibre])
            #llista_posibles_llibres = np.unique(llista_posibles_llibres['ISBN'])
            
            
            
    
    else:
             
        groupByBooks = books_data.groupby('ISBN',as_index=False)['Book-Rating'].mean()
        groupByBooks = groupByBooks.sort_values(by='Book-Rating', ascending= False)
        llista_posibles_llibres = groupByBooks[0:5]
        
else:
             
        groupByBooks = books_data.groupby('ISBN',as_index=False)['Book-Rating'].mean()
        groupByBooks = groupByBooks.sort_values(by='Book-Rating', ascending= False)
        llista_posibles_llibres= groupByBooks[0:5]
        
print(llista_posibles_llibres)
        
    
        
    
    
        
    
        
        
        
        












