import requests

from tqdm import tqdm
import time
import pandas as pd
from sqlalchemy import create_engine,Table, Column, Text, MetaData, DateTime, Index, Integer
from sqlalchemy.dialects.mysql import VARCHAR
my_conn = create_engine("mysql+mysqldb://root:")

headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56"}## Defining headers to avoid errors

def main():
    try:
        response = requests.get('https://api.github.com/repos/apache/hadoop/contributors?per_page=100')
        contributors = response.json()
        time.sleep(5)
        
        keys_list = ["login", "id", "location", "email", "hireable", "bio", "twitter_username", "public_repos", 
                    "public_gists", "followers", "following", "created_at"]
        contributors_list = []
        for contributor in tqdm(contributors):
            user = {}
            response_user= requests.get(contributor['url'])
            time.sleep(10)
            user_response = response_user.json()
            for key in keys_list:
                user[key] = user_response[key]
            contributors_list.append(user)
        pd.set_option("display.max_columns",50)
        df_user = pd.DataFrame(contributors_list)
        print(df_user)

        existing_databases = my_conn.execute("SHOW DATABASES;")
        existing_databases = [d[0] for d in existing_databases]

        # Create database if not exists
        if "webscraping_api" not in existing_databases:
            my_conn.execute("CREATE DATABASE webscraping_api") 

        my_conn.execute("USE webscraping_api")    

        existing_tables = my_conn.execute("SHOW TABLES;")
        existing_tables = [d[0] for d in existing_tables]

        if "apache_api_contributors" not in existing_tables:
            meta_contributors = MetaData()

            contributors_sql = Table(
                    'apache_api_contributors', meta_contributors, 
                    Column('login', VARCHAR(256)), 
                    Column('id', Integer,primary_key = True), 
                    Column('location', VARCHAR(256)), 
                    Column('email', VARCHAR(256)),
                    Column('hireable', VARCHAR(256)), 
                    Column('bio', Text),
                    Column('twitter_username', VARCHAR(256)), 
                    Column('public_repos', Integer),
                    Column('public_gists', Integer), 
                    Column('followers', Integer),
                    Column('following', Integer),
                    Column('created_at', DateTime)
                    )   
            Index('ix_mytable_login', contributors_sql.c.login, mysql_length=256)
            Index('ix_mytable_location', contributors_sql.c.location, mysql_length=256)
            Index('ix_mytable_hireable', contributors_sql.c.hireable, mysql_length=256)
        
            meta_contributors.create_all(my_conn)
        
        my_database = create_engine("mysql+mysqldb://root:sqlking1611@localhost/webscraping_api")
        df_user['created_at'] = df_user['created_at'].values.astype('datetime64[us]')

        df_user.to_csv("test_data.csv")
        df_user.to_sql(name='apache_api_contributors', con=my_database, if_exists = 'append', index=False)
    
    except Exception as ex:
        print('error: ' + str(ex))

if __name__ == '__main__':
    main()

