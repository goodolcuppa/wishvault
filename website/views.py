from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for, session
from flask_login import login_required, current_user
from .models import Item, Category
from . import db
import json
from bs4 import BeautifulSoup
import requests

views = Blueprint("views", __name__)

@views.route('/', methods=["GET", "POST"])
@login_required
def home():
    items = current_user.items

    filters = [category.name for category in Category.query.all()]
    filter = request.args.get("filter")
    if filter:
        items = [item for item in items if str(filter) in [category.name for category in item.categories]]

    page = request.args.get("page", 1, type=int)
    page_size = 8
    start = (page - 1) * page_size
    end = start + page_size
    pages = (len(items) + page_size - 1) // page_size
    page_items = items[start:end]
    
    return render_template(
        "home.html",
        user=current_user,
        items=page_items,
        page=page,
        pages=pages,
        filter=filter,
        filters=filters
    )

@views.route("/add-item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        price = request.form.get("price")
        category_names = request.form.get("categories").split(",")

        if len(item_name) < 1:
            flash("Item name must be set.", category="error")
        elif not price.replace(".", "", 1).isdigit():
            flash("Price must be a valid number.", category="error")
        else:
            item = Item.query.filter_by(name=item_name).first()
            if item:
                flash("Item already exists.", category="error")
            else:
                new_item = Item(name=item_name, price=price, user_id=current_user.id)
                db.session.add(new_item)
                item = new_item
                flash("Item added.", category="success")

            for category_name in category_names:
                if category_name != "":
                    category = Category.query.filter_by(name=category_name).first()
                    if category:
                        print(f"{category_name} already exists.")
                    else:
                        print(f"{category_name} must first be created.")
                        new_category = Category(name=category_name)
                        db.session.add(new_category)
                        category = new_category
                    item.categories.append(category)

            db.session.commit()
            return redirect(url_for("views.home"))
            
    return render_template(
        "add_item.html", 
        user=current_user,
        item_url=session["item_url"] if "item_url" in session else "",
        item_name=session["item_name"] if "item_name" in session else "",
        item_price=session["item_price"] if "item_price" in session else ""
    )

@views.route("/delete-item", methods=["POST"])
def delete_item():
    if request.method == "POST":
        item = json.loads(request.data)
        id = item["itemId"]
        item = Item.query.get(id)
        if item:
            if item.user_id == current_user.id:
                db.session.delete(item)
                db.session.commit()
                flash("Item deleted.", category="success")
            else:
                flash("You do not own this item.", category="error")
        else:
            flash("Item does not exist.", category="error")

        return jsonify({})

@views.route("/find-item", methods=["POST"])
def find_item():
    if request.method == "POST":
        data = json.loads(request.data)
        url = data["url"]

        if len(url) < 1:
            flash("URL must be set.", category="error")
        else:
            try:
                result = requests.get(url)
                doc = BeautifulSoup(result.text, "html.parser")

                item_name = doc.find("h1")
                prices = doc.find_all(text="£") + doc.find_all(text="$")
                price = prices[0].parent.find("strong") if prices else None

                print("Scraping web...")

                session["item_url"] = url
                session["item_name"] = "balls"
                session["item_price"] = 3
            except:
                flash("Invalid URL.", category="error")

            return redirect(url_for("views.add_item"))
        
        return jsonify({})

@views.route("/edit-item", methods=["GET", "POST"])
def edit_item():
    if request.method == "POST":
        item_id = request.args.get("id")
        item_name = request.form.get("item_name")
        price = request.form.get("price")
        url = request.form.get("url")
        categories = request.form.get("categories").split(",")

        item = Item.query.get(int(item_id))
        if item:
            if item.user_id == current_user.id:
                item.name = item_name
                item.price = price
                item.url = url

                for category_name in categories:
                    if category_name not in [category.name for category in item.categories] and category_name != "":
                        category = Category.query.filter_by(name=category_name).first()
                        if category:
                            print(f"{category_name} already exists.")
                        else:
                            print(f"{category_name} must first be created.")
                            new_category = Category(name=category_name)
                            db.session.add(new_category)
                            category = new_category
                        item.categories.append(category)

                for category in item.categories:
                    if category.name not in categories:
                        item.categories.remove(category)

                db.session.commit()
                flash("Item updated.", category="success")
                return redirect(url_for('views.home'))
            else:
                flash("You do not own this item.", category="error")
        else:
            flash("Item does not exist.", category="error")

    item_id = request.args.get("id")
    item = Item.query.get(item_id)
    return render_template("edit_item.html", user=current_user, item=item)
