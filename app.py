from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime as dt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dtbs.db'#connect to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ===== МОДЕЛЬ =====
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    intro = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=dt.utcnow)

    def __repr__(self):
        return f'<Article {self.id}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nick = db.Column(db.String(50), nullable = False, unique = True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.nick}>'


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    warning = None  # Для сообщения об ошибке
    if request.method == "POST":
        nick = request.form['nick']
        email = request.form['email']
        password = request.form['password']

        user = User(nick=nick, email=email, password=password)

        try:
            db.session.add(user)
            db.session.commit()
            articles = Article.query.order_by(Article.date.desc()).all()
            return render_template("index.html", articles=articles)
        except IntegrityError:
            db.session.rollback()  # Откат транзакции
            warning = "User with name or email already exists"
        except Exception as e:
            db.session.rollback()
            warning = f"Error: {e}"

    return render_template("sign_up.html", warning=warning)



@app.route('/')
def login():
    return render_template("login.html")
@app.route('/home')
def main():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("index.html", articles=articles)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/create-article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/home')
        except:
            return "Ошибка при добавлении статьи"
    else:
        return render_template("create_article.html")

@app.route('/delete-article/<int:id>', methods=['POST'])
def delete_article(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/home')
    except:
        return "Ошибка при удалении статьи"

@app.route('/change-article/<int:id>', methods=['GET', 'POST'])
def change_article(id):
    article = Article.query.get_or_404(id)

    if request.method == "POST":
        # Получаем новые данные из формы
        article.title = request.form['title']
        article.text = request.form['text']

        try:
            db.session.commit()  # Сохраняем изменения в БД
            return redirect(f'/posts/{article.id}')  # Возвращаемся на страницу статьи
        except:
            return "Ошибка при изменении статьи"

    return render_template("change_article.html", article=article)



@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get_or_404(id)
    return render_template("post_detail.html", article=article)


# ===== СТАРТ =====
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
