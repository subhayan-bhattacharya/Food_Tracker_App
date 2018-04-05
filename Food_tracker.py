from flask import Flask,render_template,g,request
from datetime import datetime
from collections import defaultdict
from database import get_db

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'This is a secret key'

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/',methods=["GET","POST"])
def index():
    db = get_db()
    if request.method == "POST":
        entered_date = request.form["date"]
        formated_entered_date = datetime.strptime(entered_date,'%Y-%m-%d')
        final_database_date = datetime.strftime(formated_entered_date,'%Y%m%d')
        db.execute("insert into log_date (entry_date) values (?)",[final_database_date])
        db.commit()

    cur = db.execute('select * from log_date order by entry_date DESC ')
    results = cur.fetchall()
    pretty_results = []
    dates = []

    for i in results:
        single_date = {}
        curr = db.execute('''select protein,carbohydrates,fat,calories 
                              from food where id in 
                              (select food_id from food_date where log_date_id = 
                              (select id from log_date where entry_date = ?))''',[i['entry_date']])

        food_results = curr.fetchall()
        total = defaultdict(int)
        for food in food_results:
            total['protein'] = total['protein'] + food['protein']
            total['carbohydrates'] = total['carbohydrates'] + food['carbohydrates']
            total['fat'] = total['fat'] + food['fat']
            total['calories'] = total['calories'] + food['calories']

        d = datetime.strptime(str(i['entry_date']),'%Y%m%d')
        single_date['pretty_entry_date'] = datetime.strftime(d,'%B %d, %Y')
        single_date['entry_date'] = i['entry_date']
        single_date['totals'] = total
        pretty_results.append(single_date)

    return render_template('home.html',results=pretty_results)

@app.route('/view/<date>',methods=["POST","GET"])
def view(date):
    db = get_db()
    cur = db.execute("select id,entry_date from log_date where entry_date = ?", [date])
    log_results = cur.fetchone()

    if request.method == "POST":
        food_selected = request.form["food-select"]
        log_date_id = log_results['id']
        db.execute("insert into food_date(food_id,log_date_id) values(?,?)", [food_selected,log_date_id])
        db.commit()

    d = datetime.strptime(str(log_results['entry_date']),'%Y%m%d')
    pretty_date = datetime.strftime(d,'%B %d, %Y')
    cur = db.execute("select id,name from food")
    food_items = cur.fetchall()

    food_details = []
    log_cur = db.execute('''select name,protein,carbohydrates,fat,calories 
                            from food where id in 
                            (select food_id from food_date where log_date_id = 
                            (select id from log_date where entry_date = ?))''',[date])
    food_details = log_cur.fetchall()
    total = defaultdict(int)
    for r in food_details:
        total['protein'] = total['protein'] + r['protein']
        total['carbohydrates'] = total['carbohydrates'] + r['carbohydrates']
        total['calories'] = total['calories'] + r['calories']
        total['fat'] = total['fat'] + r['fat']
    return render_template('day.html',date=pretty_date,food_items=food_items,passed_date=date,food_details=food_details,total=total)


@app.route('/add_food',methods=["GET","POST"])
def add_food():
    db = get_db()
    if request.method == "POST":
        name = request.form["food-name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form["carbohydrates"])
        fat = int(request.form["fat"])
        calories = protein * 4 + carbohydrates * 4 + fat * 9
        db.execute("insert into food(name,protein,carbohydrates,fat,calories) values(?,?,?,?,?)",[name,protein,
        carbohydrates,fat,calories])
        db.commit()
        #return "<h1>Food successfully added </h1>"

    cur = db.execute('select name,protein,carbohydrates,fat,calories from food')
    results = cur.fetchall()
    return render_template('add_food.html',results=results)

if __name__ == "__main__":
    app.run(port=5040)