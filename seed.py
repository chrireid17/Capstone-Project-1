from charset_normalizer import api
from app import db
import requests
from models import Drink

db.drop_all()
db.create_all()

letters = 'abcdefghijklmnopqrstvwyz'

for letter in letters:
    resp = requests.get(
        'http://www.thecocktaildb.com/api/json/v1/1/search.php?',
        params={'f':letter}
    )

    drinks = resp.json()

    for d in drinks['drinks']:
        name = d['strDrink']
        instructions = d['strInstructions']
        api_id = int(d['idDrink'])
        img_url = d['strDrinkThumb']
        ingredients = []
        measurements = []
        for i in range(15, 0, -1):
            if d[f'strIngredient{i}']:
                ingredients.append(d[f'strIngredient{i}'])
            if d[f'strMeasure{i}']:
                measurements.append(d[f'strMeasure{i}'])
                

        drink = Drink(name=name, instructions=instructions, api_id=api_id, ingredients=ingredients, measurements=measurements, img_url=img_url)

        db.session.add(drink)
        db.session.commit()
