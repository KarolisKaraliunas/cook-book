import os
import math
from flask import Flask, render_template, redirect, url_for, request, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'online cookbook'
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", 'mongodb://localhost')
app.config['SECRET_KEY'] = os.urandom(24) 
mongo = PyMongo(app)




""" Login page """
@app.route('/')
def index():
    return render_template("index.html")


""" Sign in tab active """
@app.route('/signin')
def signin():
    signin = True
    return render_template("index.html", signin=signin)


""" Sign up tab active """
@app.route('/signup')
def signup():
    signin = False
    return render_template("index.html", signin=signin)    


""" Check data submitted via Registration form """
@app.route('/register', methods=['POST'])
def register():
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password = request.form.get('password')
    registered = users.find_one({
        'username': {'$regex': username, '$options': 'i'}
    })
    
    if registered is None:
        users.insert_one({
            'username': username,
            'fullname': fullname,
            'password': password,
            'upvoted_recipes':[],
            'fav_recipes': []
        })
        success = True
        return render_template('index.html', success=success)
        
    success = False    
    return render_template('index.html', success=success)
        
        
""" Check data submitted via Login form """
@app.route('/logout', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    registered = users.find_one({
        'username': {'$regex': username, '$options': 'i'}, 
        'password': password
    })
    
    if registered is not None:
        session['username'] = username
        login = True
        return redirect(url_for('all_recipes', num=1))
        
    login = False    
    return render_template('index.html', login=login)


""" Redirects guest users to website home page """
@app.route('/guest_user')
def guest_user():
    return redirect(url_for('all_recipes', num=1))


""" Logout a user by removing username from session """
@app.route('/login')
def logout():
    session.clear()
    return render_template('index.html')


""" My recipes page """
@app.route('/my_recipes/<username>/page:<num>')
def my_recipes(username, num):
    
    if username is not None:
        my_recipes = recipes.find({
            'recipe_author_name': {'$regex': username, '$options': 'i'}
        }).sort([('upvotes', -1)])
        total_my_recipes = my_recipes.count()
        
    total_pages = range(1, math.ceil(total_my_recipes/8) + 1)
    skip_num = 8 * (int(num) - 1)
    recipes_per_page = my_recipes.skip(skip_num).limit(8).sort([("upvotes", -1)])
    
    if total_my_recipes <= 8:
        page_count = total_my_recipes
    elif (skip_num + 8) <= total_my_recipes:
        page_count = skip_num + 8
    else:
        page_count = total_my_recipes 
    return render_template("myrecipes.html", recipes=recipes.find(), dishes=dishes.find(), 
                    cuisines=cuisines.find(), allergens=allergens.find(), my_recipes=my_recipes, 
                    users=users.find(), total_pages=total_pages, num=num, skip_num=skip_num, 
                    page_count=page_count, total_my_recipes=total_my_recipes,
                    recipes_per_page=recipes_per_page)    


""" Add favourite recipes page """
@app.route('/add_fav_recipes/<username>/<recipe_id>/<title>')
def add_fav_recipe(username, recipe_id, title):
    if username is not None:
        users.update(
            {'username': {'$regex': username, '$options': 'i'}}, 
            {'$push': {'fav_recipes': [recipe_id, title]}}
            )
        recipes.update(
            {'_id': ObjectId(recipe_id)}, 
            {'$push': {'fav_by_users': username.lower()}})
        return redirect(request.referrer)


""" Remove favourite recipes page """
@app.route('/remove_fav_recipes/<username>/<recipe_id>/<title>')
def remove_fav_recipe(username, recipe_id, title):
    if username is not None:
        users.update(
            {'username':{'$regex': username, '$options': 'i'}}, 
            {'$pull': {'fav_recipes': [recipe_id, title]}})
        recipes.update(
            {'_id': ObjectId(recipe_id)}, 
            {'$pull': {'fav_by_users': {'$regex': username, '$options': 'i'}}})
        return redirect(request.referrer)       


""" Favourite recipes page """
@app.route('/fav_recipes/<username>/page:<num>')
def fav_recipes(username, num):
    this_user=users.find_one({
        'username': {'$regex': username, '$options': 'i'}
    })
    fav_recipe_count = len(this_user['fav_recipes']) 
    fav_recipes = recipes.find({
        'fav_by_users': username.lower()
        
    })
    total_pages = range(1, math.ceil(fav_recipe_count/8) + 1)
    skip_num = 8 * (int(num)-1)
    recipes_per_page = fav_recipes.skip(skip_num).limit(8).sort([("upvotes", -1)])
    
    if fav_recipe_count <= 8:
        page_count = fav_recipe_count
    elif (skip_num + 8) <= fav_recipe_count:
        page_count = skip_num + 8
    else:
        page_count = fav_recipe_count
    return render_template("favrecipes.html", recipes=recipes.find(), 
            dishes=dishes.find(), cuisines=cuisines.find(), fav_recipe_count=fav_recipe_count,
            total_pages=total_pages, num=num, skip_num=skip_num, page_count=page_count, 
            users=users.find(), allergens=allergens.find(), this_user=this_user, 
            recipes_per_page=recipes_per_page)    
    

""" Home page displaying all uploaded recipes """
@app.route('/all_recipes/page:<num>')
def all_recipes(num):
    total_recipes=recipes.find().count()
    total_pages = range(1, math.ceil(total_recipes/8) + 1)
    skip_num = 8 * (int(num)-1)
    recipes_per_page = recipes.find().skip(skip_num).limit(8).sort([("upvotes", -1)])
    
    if total_recipes <= 8:
        page_count = total_recipes
    elif (skip_num + 8) <= total_recipes:
        page_count = skip_num + 8
    else:
        page_count = total_recipes
    return render_template("home.html", recipes=recipes.find(),
            dishes=dishes.find(), cuisines=cuisines.find(), users=users.find(), 
            allergens=allergens.find(), total_pages=total_pages, skip_num=skip_num, 
            num=num, page_count=page_count, recipes_per_page=recipes_per_page, 
            total_recipes=total_recipes)


""" Displays detail view of a recipe """    
@app.route('/the_recipe/<recipe_id>/<recipe_title>')
def the_recipe(recipe_id, recipe_title):
    return render_template("recipe.html", cuisines=cuisines.find(),  
            allergens=allergens.find(), users=users.find(), dishes=dishes.find(),
            recipe=recipes.find_one({'_id': ObjectId(recipe_id),
            'recipe_title': recipe_title}))


""" Display form to add a recipe """ 
@app.route('/add_recipe')
def add_recipe():
    return render_template("addrecipe.html", cuisines=cuisines.find(), 
            dishes=dishes.find(), recipes=recipes.find(), users=users.find(), 
            allergens=allergens.find())


""" Display form to edit the recipe """
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    return render_template('editrecipe.html', cuisines=cuisines.find(), 
            dishes=dishes.find(), allergens=allergens.find(), users=users.find(),
            recipe=recipes.find_one({"_id": ObjectId(recipe_id)}))


""" Send form data to update recipe in MongoDB """
@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    recipes.update( {'_id': ObjectId(recipe_id)},
        { 
            '$set':{
                'recipe_author_name': session['username'],
                'recipe_title':request.form.get('recipe_title'),
                'recipe_short_description':request.form.get('recipe_short_description'),
                'recipe_image_url': request.form.get('recipe_image_url'),
                'cuisine_name': request.form.get('cuisine_name'),
                'dish_type':request.form.get('dish_type'),
                'allergen_name':request.form.getlist('allergen_name'),
                'recipe_prep_time':request.form.get('recipe_prep_time'),
                'recipe_cook_time':request.form.get('recipe_cook_time'),
                'total_time':request.form.get('total_time'),
                'recipe_serves':request.form.get('recipe_serves'),
                'recipe_ingredients':request.form.getlist('ingred'),
                'recipe_steps':request.form.getlist('steps')
            }
        })
    return redirect(url_for('my_recipes', username=session['username'], num=1))
  
  
""" Insert new recipe to recipes collection in MongoDB """   
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    doc = {'recipe_author_name': session['username'], 
          "upvotes": 0, 
          "upvoted_by_users":[]
    }
    data = request.form.items()
    all_ingred = request.form.getlist('ingred')
    all_steps = request.form.getlist('steps')
    all_allergens = request.form.getlist("allergen_name")
   
    for k, v in data: 
        if k == "ingred":
            doc["recipe_ingredients"]=all_ingred
        elif k == "steps":
            doc["recipe_steps"]=all_steps
        elif k == "allergen_name":
            doc["allergen_name"] = all_allergens
        else:
            doc[k]= v  

    new_recipe = doc
    recipes.insert_one(new_recipe)
    return redirect(url_for('my_recipes', username=session['username'], num=1))


""" Removes a recipe from MongoDB """
@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('my_recipes', username= session['username'], num=1)) 


""" Displays all cuisines in MongoDB """
@app.route('/all_cuisines')
def all_cuisines():
    all_cuisines=[]
    for cuisine in cuisines.find():
        cuisine_count = recipes.find({'cuisine_name': cuisine['cuisine_name']}).count()
        all_cuisines.append({cuisine['cuisine_name'] : cuisine_count})
    return render_template("allcuisines.html", cuisines=cuisines.find(), dishes=dishes.find(), 
           recipes=recipes.find(), users=users.find(), allergens=allergens.find(),
            all_cuisines=all_cuisines)


""" Displays form to add new cuisine """
@app.route('/add_cuisine')
def add_cuisine():
    return render_template("addcuisine.html", cuisines=cuisines.find(), 
            dishes=dishes.find(), users=users.find(), allergens=allergens.find())


""" Adds new cuisine to MongoDB """
@app.route('/insert_cuisine', methods=['POST'])
def insert_cuisine():
    the_cuisine = request.form.get('cuisine_name')
    if cuisines.find_one({
        'cuisine_name': {'$regex': the_cuisine, '$options': 'i'}
    }) is None:
        new_cuisine = {'cuisine_name': the_cuisine}
        cuisines.insert_one(new_cuisine)
        return redirect(url_for('all_cuisines'))
    else: 
        new_cuisine = False
        return render_template('addcuisine.html', new_cuisine=new_cuisine,
                cuisines=cuisines.find(), dishes=dishes.find(), users=users.find(), 
                allergens=allergens.find())
 
 
""" Displays form to edit cuisine """    
@app.route('/edit_cuisine/<cuis_name>')
def edit_cuisine(cuis_name):
    cuisine=cuisines.find_one({'cuisine_name': cuis_name})
    return render_template('editcuisine.html', cuisines=cuisines.find(), 
            dishes=dishes.find(), users=users.find(), allergens=allergens.find(), 
            cuisine=cuisine)    


""" Send form data to update cuisine in MongoDB """ 
@app.route('/update_cuisine/<cuisine_id>', methods=["POST"])
def update_cuisine(cuisine_id):
    new_cuisine = request.form.get('cuisine_name')
    cuisine=cuisines.find_one({"_id": ObjectId(cuisine_id)})
    distinct_cuisines = recipes.distinct('cuisine_name')
    
    if new_cuisine == cuisine['cuisine_name']:
        return redirect(url_for('all_cuisines'))
    elif cuisine['cuisine_name'] in distinct_cuisines:
        edit_cuisine = False
        return render_template('editcuisine.html', edit_cuisine=edit_cuisine, 
                cuisines=cuisines.find(), dishes=dishes.find(), recipes=recipes.find(),
                users=users.find(), allergens=allergens.find(), cuisine=cuisine)
    else:
        cuisines.update(
            {'_id': ObjectId(cuisine_id)}, 
            {'cuisine_name': new_cuisine})
        return redirect(url_for('all_cuisines'))  


""" Removes a cuisine from MongoDB """
@app.route('/delete_cuisine/<cuis_name>')
def delete_cuisine(cuis_name):
    distinct_cuisines = recipes.distinct('cuisine_name')
    this_cuisine = cuisines.find_one({'cuisine_name': cuis_name})
    if this_cuisine['cuisine_name'] in distinct_cuisines:
        delete_cuisine = False
        return render_template('allcuisines.html', delete_cuisine=delete_cuisine, 
                dishes=dishes.find(), cuisines=cuisines.find(), users=users.find(),
                allergens=allergens.find())
    else: 
        cuisines.remove({'cuisine_name': cuis_name})
        return redirect(url_for('all_cuisines'))  
     
     
""" Displays all dishes existing in MongoDB """ 
@app.route('/all_dishes')
def all_dishes():
    all_dishes=[]
    for dish in dishes.find():
        dish_count = recipes.find({'dish_type': dish['dish_type']}).count()
        all_dishes.append({dish['dish_type'] : dish_count})
    return render_template("alldishes.html", cuisines=cuisines.find(), all_dishes=all_dishes,
            dishes=dishes.find(), users=users.find(), allergens=allergens.find())


""" Displays form to add a new dish """
@app.route('/add_dish')
def add_dish():
    return render_template("adddish.html", dishes=dishes.find(), 
            cuisines=cuisines.find(), users=users.find(), allergens=allergens.find())


""" Adds a new dish to MongoDB """
@app.route('/insert_dish', methods=['POST'])
def insert_dish():
    the_dish = request.form.get('dish_type')
    if dishes.find_one({
        'dish_type': {'$regex': the_dish, '$options': 'i'}
    }) is None:
        new_dish = {'dish_type': the_dish}
        dishes.insert_one(new_dish)
        return redirect(url_for('all_dishes'))
    else: 
        new_dish = False
        return render_template('adddish.html', new_dish = new_dish, cuisines=cuisines.find(), 
                dishes=dishes.find(), users=users.find(), allergens=allergens.find())
 
 
""" Displays form to edit a dish """    
@app.route('/edit_dish/<dish_type>')
def edit_dish(dish_type):
    return render_template('editdish.html', dishes=dishes.find(), recipes=recipes.find(), 
            users=users.find(), cuisines=cuisines.find(), allergens=allergens.find(),
            dish = dishes.find_one({"dish_type": dish_type}), )    


""" Send form data to update the dish in MongoDB """ 
@app.route('/update_dish/<dish_id>', methods=["POST"])
def update_dish(dish_id):
    new_dish = request.form.get('dish_type')
    distinct_dishes = recipes.distinct('dish_type')
    dish = dishes.find_one({'_id': ObjectId(dish_id)})
    if new_dish == dish['dish_type']:
        return redirect(url_for('all_dishes'))
    elif dish['dish_type'] in distinct_dishes:
        edit_dish = False
        return render_template('editdish.html', edit_dish=edit_dish, dish=dish,
                cuisines=cuisines.find(), dishes=dishes.find(), recipes=recipes.find(),
                allergens=allergens.find(), users=users.find())
    else:
        dishes.update(
            {'_id': ObjectId(dish_id)}, 
            {'dish_type': request.form.get('dish_type')})
        return redirect(url_for('all_dishes'))  


""" Remove the dish in MongoDB """ 
@app.route('/delete_dish/<dish_type>')
def delete_dish(dish_type):
    distinct_dishes = recipes.distinct('dish_type')
    this_dish = dishes.find_one({'dish_type': dish_type})
    if this_dish['dish_type'] in distinct_dishes:
        delete_dish = False
        return render_template('alldishes.html', delete_dish=delete_dish, 
                cuisines=cuisines.find(), dishes=dishes.find(), recipes=recipes.find(),
                users=users.find(), allergens=allergens.find())
    else: 
        dishes.remove({'dish_type': dish_type})
        return redirect(url_for('all_dishes'))  


""" Search by Cuisine """  
@app.route('/search_cuisine/<cuisine_name>/page:<num>')
def search_cuisine(cuisine_name, num):
    cuisine_result = recipes.find({'cuisine_name': cuisine_name}).sort([("upvotes", -1)])
    cuisine_count = cuisine_result.count()
    total_pages = range(1, math.ceil(cuisine_count/8) + 1)
    skip_num = 8 * (int(num) - 1)
    recipes_per_page = cuisine_result.skip(skip_num).limit(8)
    
    if cuisine_count <= 8:
        page_count = cuisine_count
    elif (skip_num + 8) <= cuisine_count:
        page_count = skip_num + 8
    else:
        page_count = cuisine_count 
    return render_template('searchcuisine.html', recipes_per_page=recipes_per_page, 
            num=num, cuisine_name=cuisine_name,  skip_num=skip_num, total_pages=total_pages, 
            page_count=page_count, count=cuisine_count, cuisines=cuisines.find(), 
            dishes=dishes.find(), users=users.find(), allergens=allergens.find())


""" Search by dish types """
@app.route('/search_dish/<dish_type>/page:<num>')
def search_dish(dish_type, num):
    dish_result = recipes.find({'dish_type': dish_type}).sort([("upvotes", -1)])
    dish_count = dish_result.count()
    total_pages = range(1, math.ceil(dish_count/8) + 1)
    skip_num = 8 * (int(num) - 1)
    recipes_per_page = dish_result.skip(skip_num).limit(8)
    if dish_count <= 8:
        page_count = dish_count
    elif (skip_num + 8) <= dish_count:
        page_count = skip_num + 8
    else:
        page_count = dish_count
    return render_template('searchdish.html', dish_type=dish_type, num=num, 
            total_pages=total_pages, page_count=page_count, skip_num=skip_num, 
            recipes_per_page=recipes_per_page, count=dish_count, dishes=dishes.find(), 
            cuisines=cuisines.find(), users=users.find(), allergens=allergens.find()) 


""" Search by authors """
@app.route('/search_author/<author_name>/page:<num>')
def search_author(author_name, num):
    author_result = recipes.find({'recipe_author_name': 
        {'$regex': author_name, '$options': 'i'}}).sort([("upvotes", -1)])
    author_count = author_result.count()
    total_pages = range(1, math.ceil(author_count/8) + 1)
    skip_num = 8 * (int(num) - 1)
    recipes_per_page = author_result.skip(skip_num).limit(8)
    
    if author_count <= 8:
        page_count = author_count
    elif (skip_num + 8) <= author_count:
        page_count = skip_num + 8
    else:
        page_count = author_count
    return render_template('searchauthor.html', total_pages=total_pages, 
            author_name=author_name, recipes_per_page=recipes_per_page, num=num, 
            skip_num=skip_num, page_count=page_count, count=author_count, 
            dishes=dishes.find(), cuisines=cuisines.find(), users=users.find(), 
            allergens=allergens.find())


""" Search by allergens """
@app.route('/search_allergen/<allergen_name>/page:<num>')
def search_allergen(allergen_name, num):
    allergen_result = recipes.find({'allergen_name':
        {'$not': {'$eq': allergen_name}}}).sort([("upvotes", -1)])
    allergen_count = allergen_result.count()
    total_pages = range(1, math.ceil(allergen_count/8) + 1)
    skip_num = 8 * (int(num)-1)
    recipes_per_page = allergen_result.skip(skip_num).limit(8)
    
    if allergen_count <= 8:
        page_count = allergen_count
    elif (skip_num + 8) <= allergen_count:
        page_count = skip_num + 8
    else:
        page_count = allergen_count
    return render_template('searchallergen.html', num=num, allergen_name=allergen_name, 
            total_pages = total_pages, skip_num=skip_num, page_count=page_count, 
            recipes_per_page=recipes_per_page, count=allergen_count, dishes=dishes.find(), 
            cuisines=cuisines.find(), users=users.find(), allergens=allergens.find())


""" Search by keyword """
@app.route('/search_keyword', methods=['POST'])
def insert_keyword():
    return redirect(url_for('search_keyword', num=1, keyword=request.form.get('keyword')) ) 
    
    
@app.route('/search_keyword/<keyword>/page:<num>')
def search_keyword(keyword, num):
    recipes.create_index([
         ("recipe_title", "text"),
         ("recipe_ingredients", "text"),
         ("cuisine_name", "text"),
         ("dish_type", "text"),
         ("recipe_author_name", "text")
       ])
    keyword_result = recipes.find({"$text": 
        {"$search": keyword}}).sort([("upvotes", -1)])
    keyword_count = keyword_result.count()
    total_pages = range(1, math.ceil(keyword_count/8) + 1)
    skip_num = 8 * (int(num)-1)
    recipes_per_page = keyword_result.skip(skip_num).limit(8)
    
    if keyword_count <= 8:
        page_count = keyword_count
    elif (skip_num + 8) <= keyword_count:
        page_count = skip_num + 8
    else:
        page_count = keyword_count
    return render_template('searchkeyword.html', total_pages=total_pages, num=num, 
            keyword=keyword, recipes_per_page=recipes_per_page, skip_num=skip_num, 
            page_count=page_count, count=keyword_count, dishes=dishes.find(), 
            cuisines=cuisines.find(), users=users.find(), allergens=allergens.find())


""" Function to upvote a recipe """
@app.route('/recipe_upvotes/<recipe_id>/<author>/<title>/<username>', methods=["GET", "POST"])
def recipe_upvotes(recipe_id, title, author, username):
    if users.find_one({'$and':[{'username': {'$regex': username, '$options': 'i'}},
        {'upvoted_recipes': (recipe_id, title)}]}) is None and author.lower() != username.lower():
        recipes.update(
            {'_id': ObjectId(recipe_id)},
            {
                '$push': {"upvoted_by_users": username.lower()},
                '$inc': {"upvotes": 1}
            })
        users.update(
            {'username': {'$regex': username, '$options': 'i'}},
            {'$push': {'upvoted_recipes': (recipe_id, title)}})
        
    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'), 
        port=int(os.environ.get('PORT')),
        debug=False)