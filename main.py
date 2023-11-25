from fastapi import FastAPI  # Importo las librerias que utilizare
import pandas as pd
import uvicorn
import numpy as np
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Lectura de todos los CSV
play_genre = pd.read_csv('PlayTimeGenre.csv', low_memory=False)
user_genre= pd.read_csv('UserForGenre.csv', low_memory=False)
user_recommend= pd.read_csv('UsersRecommend.csv', low_memory=False)
juegos_no_recom= pd.read_csv('UsersNotRecommend.csv', low_memory=False)
df_sentimiento_analisis= pd.read_csv('sentiment_analysis.csv', low_memory=False)



#Funcion PlayTimeGenre, devuelve el año con más horas jugadas para dicho género.

@app.get("/genero/{genres}")
def PlayTimeGenre(genres):
    df_filtered = play_genre[play_genre['genres'] == genres]

    if df_filtered.empty:
        return {"message": f"No se encontraron datos para el género {genres}"}

    max_playtime_index = df_filtered['playtime_forever'].idxmax()

    # Obtener el año y las horas jugadas
    max_playtime_year = df_filtered.loc[max_playtime_index, 'release_date']
    max_playtime_hours = df_filtered.loc[max_playtime_index, 'playtime_forever']

    return {
        f"Genero con más horas jugadas {genres}": {
            "Año": str(max_playtime_year),
            "Horas": max_playtime_hours
        }
    }

if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True) #Corró la función
    
    
# Funcion UserForGenre, devuelve el usuario que acumula más horas jugadas para el género dado
# y una lista de la acumulación de horas jugadas por año.

@app.get("/usuario/{genres}")

def UserForGenre(genres: str):
    '''Función que devuelve al usuario con más horas jugadas por genero y año'''

    df_filtered = user_genre[user_genre['genres'] == genres]

    df_filtered = df_filtered[df_filtered['release_date'].str.match(r'\d{4}-\d{2}-\d{2}', na=False)]

    df_filtered['release_date'] = pd.to_datetime(df_filtered['release_date'], format='%Y-%m-%d')
    
    user_year_playtime = df_filtered.groupby(['user_id', df_filtered['release_date'].dt.year])['playtime_forever'].sum().reset_index()

    max_user = user_year_playtime.groupby('user_id')['playtime_forever'].sum().idxmax()

    df_max_user = user_year_playtime[user_year_playtime['user_id'] == max_user]

    max_user_year_playtime = df_max_user.groupby('release_date')['playtime_forever'].sum()

    max_user_year_playtime_list = [{"Año": year, "Horas": hours} for year, hours in zip(max_user_year_playtime.index, max_user_year_playtime)]

    return {
        f"Usuario con más horas jugadas para {genres}": max_user,
        "Horas jugadas": max_user_year_playtime_list
    }

#Funcion UsersRecommend, Devuelve el top 3 de juegos MÁS recomendados por usuarios para el año dado.

@app.get("/year")

def UsersRecommend(year: int):
    '''Devuelve los 3 juegos más recomendados por usuarios 
        para el año dado por un usuario específico.'''

    filtered_reviews = user_recommend[(user_recommend['release_date'].str.contains(str(year), regex=False, na=False)) & (user_recommend['recommend'] == True)]

    top_games = (
        filtered_reviews['title']
        .value_counts()
        .head(3)
        .reset_index()
        .rename(columns={'index': 'title', 'title': 'count'})
    )

    top_3_games_list = [{f"Puesto {i+1}: {game}": count} for i, (game, count) in top_games.iterrows()]

    return top_3_games_list

if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)
    
    
#Funcion UsersWorstDeveloper, Devuelve el top 3 de desarrolladoras con juegos MENOS recomendados por usuarios para el año dado

@app.get("/year")

def UsersWorstDeveloper(year: int):
    '''Devuelve los juegos Menos recomendados por usuarios para el año dado.'''

    filtered_reviews = juegos_no_recom[(juegos_no_recom['release_date'].str.contains(str(year), regex=False, na=False)) & (juegos_no_recom['recommend'] == False)]

    less_rated_games = (
        filtered_reviews['title']
        .value_counts()
        .head(3)
        .reset_index()
        .rename(columns={'index': 'title', 'title': 'count'})
    )

    less_3_games_list = [{f"Puesto {i+1}: {game}": count} for i, (game, count) in less_rated_games.iterrows()]

    return less_3_games_list


if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)
    
    
#Función sentiment_analysis, según la empresa desarrolladora, se devuelve un diccionario 
#con el nombre de la desarrolladora como llave y una lista con la cantidad total de registros
#de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento como valor.

@app.get("/year")

def sentiment_analysis(year):
    '''
    Función que devuelve la cantidad de registros de reseñas de usuarios 
    categorizados con un análisis de sentimiento para un anio de lanzamiento específico. 
    '''
    df_filtrado = df_sentimiento_analisis[df_sentimiento_analisis['release_date'].str.startswith(str(year))]

    sentiment_counts = df_filtrado['sentiment_analysis'].value_counts()

    result_dict = {"Negative": 0, "Neutral": 0, "Positive": 0}
    
    for index, count in sentiment_counts.items():
        if index == 0:
            result_dict["Negative"] = count
        elif index == 1:
            result_dict["Neutral"] = count
        elif index == 2:
            result_dict["Positive"] = count

    return result_dict


if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload=True)
    

    



# Ejecutar el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)