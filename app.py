from argparse import ONE_OR_MORE
from flask import Flask,render_template,request,g
import db
import datetime
app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    dbob=db.get_db()
    if request.method == 'POST':
        
        date=request.form["date"]
        dt=datetime.datetime.strptime(date,"%Y-%m-%d")
        db_date=datetime.datetime.strftime(dt,"%Y%m%d")
        dbob.execute("insert into log_date (entry_date) values (?)",[db_date])
        dbob.commit()
    cur=dbob.execute("select log_date.entry_date,sum(food.protein) as protein,sum(food.carbohydrates) as carb,sum(food.fat) as fat,sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id=log_date.id left join food on food.id=food_date.food_id group by log_date.id order by log_date.entry_date")
    results=cur.fetchall()
    date_result=[]
    for i in results:
        temp={}
        temp["entry_date"]=i["entry_date"]
        temp["protein"]=i["protein"]
        temp["carbohydrates"]=i["carb"]
        temp["fat"]=i["fat"]
        temp["calories"]=i["calories"]
        d=datetime.datetime.strptime(str(i["entry_date"]),"%Y%m%d")
        temp["pretty_date"]=datetime.datetime.strftime(d,'%B %d, %Y')
        date_result.append(temp)
    return render_template("home.html",results=date_result)

@app.route('/view/<date>',methods=['GET', 'POST'])
def view(date):
    dbob=db.get_db()
   
    cur=dbob.execute("select * from log_date  where entry_date=?",[date])
    date_result=cur.fetchone()
    if request.method == 'POST':
        dbob.execute("insert into food_date (food_id,log_date_id) values(?,?)",[request.form['food-select'],date_result["id"]])
        dbob.commit()
    
    d=date_result["entry_date"]
    d=datetime.datetime.strptime(str(d),"%Y%m%d")
    pretty_date=datetime.datetime.strftime(d,"%B %d, %Y")
    food_cur=dbob.execute("select * from food")
    food_results=food_cur.fetchall()
    totals={}
    totals["protein"]=0
    totals["carbohydrates"]=0
    totals["fat"]=0
    totals["calories"]=0
    for food in food_results:
        totals["protein"]+=food["protein"]
        totals["carbohydrates"]+=food["carbohydrates"]
        totals["fat"]+=food["fat"]
        totals["calories"]+=food["calories"]
        
    log_cur=dbob.execute("select food.name,food.protein,food.carbohydrates,food.fat,food.calories from log_date join food_date on food_date.log_date_id=log_date.id join food on food.id=food_date.food_id where log_date.entry_date=?",[date])
    log_results=log_cur.fetchall()
    
    return render_template("day.html",entry_date=date_result["entry_date"],pretty_date=pretty_date,totals=totals,food_results=food_results,log_results=log_results)

@app.route('/food',methods=['GET', 'POST'])
def food():
    dbob=db.get_db()
    if request.method == 'POST':
        food_name=request.form["food_name"]
        protein=int(request.form["protein"])
        carbo=int(request.form["carbo"])
        fat=int(request.form["fat"])
        calories=protein*4+carbo*4+fat*9
        
        
        dbob.execute('insert into food(name,protein,carbohydrates,fat,calories) values(?,?,?,?,?)',\
            [food_name,protein,carbo,fat,calories])
        dbob.commit()
    cur=dbob.execute("select * from food")
    results=cur.fetchall()
      
    return render_template("add_food.html",results=results)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g,'sqlite_db'):
        g.sqlite_db.close()



if __name__ == '__main__':
    app.run(debug=True)