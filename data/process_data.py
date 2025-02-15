import sys
import pandas as pd
import numpy as np
import sqlite3
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Load data, merge message with categories, and return as dataframe
    Input:
        messages_filepath: File path of messages data
        categories_filepath: File path of categories data
    Output:
        df: Merged dataset from messages and categories
    '''
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    
    # merge datasets
    df = messages.merge(categories, left_on='id', right_on='id',
          suffixes=('_left', '_right'))
    
    return df


def clean_data(df):
    '''
    Clean df data, create categorical data, and drop duplicates
    Input:
        df: Merged dataset from messages and categories
    Output:
        df: Cleaned dataset
    '''
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(";", expand = True)
    
    # select the first row of the categories dataframe
    row = categories.iloc[0,:]
    category_colnames = row.apply(lambda x: x[:-2])
    
    # rename the columns of `categories`
    categories.columns = category_colnames
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x: x[-1])
    
        # convert column from string to numeric
        categories[column] = categories[column].apply(lambda x: 1 if int(x)>0 else 0)

        
    # drop the original categories column from `df`
    df.drop(['categories'], axis=1, inplace= True)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    
    # drop duplicates
    df.drop_duplicates(inplace=True)
    
    # fillna with 0 for datatype of numbers, indicating this message is not of this category
    # fillna with '.' for other datatypes
    df=df.apply(lambda x: x.fillna(0) if x.dtype.kind in 'biufc' else x.fillna('.'))

    
    return df
    
    


def save_data(df, database_filename):
    '''
    Save df into sqlite db
    Input:
        df: cleaned dataset
        database_filename: database name, e.g. DisasterMessages.db
    Output: 
        A SQLite database
    '''
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('DisasterMessages', engine, index=False, if_exists='replace')


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()