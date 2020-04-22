"""
main.py
Main app
"""

import os
from urllib.parse import urlencode

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, current_user
from google.cloud import language
from titlecase import titlecase

from init_app import app, db
from oauth.google_oauth import blueprint as google_blueprint
from oauth.github_oauth import blueprint as github_blueprint
from models import Category, ContentTag, DemogTag, Post, User, Position
from summarizer import summarizer

category_dict = {}
try:
    categories = Category.query.all()
    for category in categories:
        category_dict[category.label] = [ctag.label for ctag in category.ctags]

    demog_tags = [demog.label for demog in DemogTag.query.all()]
    sample = Post.query.first().dict()
except:
    demog_tags = []
    sample = None

blueprint = Blueprint("auth", __name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

@app.context_processor
def utility_processor():
    def format_url(dict):
        for key, values in dict.items():
            dict[key] = [value.lower() for value in list(values)]
        return urlencode(dict, doseq=True)
    return dict(format_url=format_url)


@app.route('/')
def home():
    return render_template('index.html',
                           categories=category_dict)


@app.route('/contribute', methods=['GET'])
@app.route('/contribute/', methods=['GET'])
def contribute():
    return render_template('contribute.html',
                           categories=category_dict,
                           demographics=demog_tags,
                           sample=sample,
                           roles=3)


@app.route('/contribute', methods=['POST'])
@app.route('/contribute/', methods=['POST'])
def contribute_post():
    stripped_ctags = [tag.split(' - ',1)[1] for tag in request.form.getlist('ctags')]
    current_user.dtags = DemogTag.query.filter(DemogTag.label.in_(request.form.getlist('dtags'))).all()
    new_post = Post(
            author=current_user,
            category=Category.query.filter(Category.label == request.form.get('category')).first(),
            ctags=ContentTag.query.filter(ContentTag.label.in_(stripped_ctags)).all(),
            q_name=request.form.get('q_name'),
            q_about=request.form.get('q_about'),
            q_interest=request.form.get('q_interest'),
            q_challenges=request.form.get('q_challenges'),
            q_change=request.form.get('q_change'),
            q_helpful=request.form.get('q_helpful'),
            q_other=request.form.get('q_other')
        )
    for r in range(3):
        role, org = request.form.get('role' + str(r)), request.form.get('org' + str(r))
        if not (role == '' and org == ''):
            check_pos = Position.query.filter(Position.title==role, Position.org==org)
            try:
                pos = check_pos.first()
                pos.users.append(current_user)
                pos.posts.append(new_post)
            except:
                Position(title=role, org=org, users=[current_user], posts=[new_post])
    db.session.add(new_post)

    db.session.commit()
    flash('Thank you for your contribution!')
    return render_template('contribute.html',
                           categories=category_dict,
                           demographics=demog_tags,
                           sample=sample,
                           roles=3)


@app.route('/content/', methods=['GET', 'POST'])
def content():
    params = {}
    content = Post.query
    for key in ['all', 'c', 'ct', 'dt',
                'q_about', 'q_interest', 'q_challenges', 'q_change', 'q_helpful', 'q_other',
                'sort']:
        if 'q_' in key:
            params[key] = request.args.getlist(key)
        else:
            params[key] = [titlecase(tag) for tag in request.args.getlist(key)]
        if key == 'all' and len(params[key]) > 0:
            if params[key][0] in category_dict.keys():
                content = content.filter(Post.category.has(label=params[key][0]))
                params['c'] = params[key]
                params['ct'] = []
            else:
                content = content.join(Post.ctags).\
                    filter(Post.ctags.any(ContentTag.label.in_(params[key])))
                params['ct'] = params[key]
                for cat, cat_tags in category_dict.items():
                    if params[key][0] in cat_tags:
                        params['c'] = [cat]
                        break
            params['dt'] = []
            break
        elif len(params[key]) > 0:
            if key == 'c':
                content = content.filter(Post.category.has(label=params[key][0]))
            if key == 'ct':
                content = content.join(Post.ctags).\
                    filter(Post.ctags.any(ContentTag.label.in_(params[key])))
                if len(params['c']) == 0:
                    params['c'] = [content.first().category.label]
            if key == 'dt':
                content = content.join(Post.author).\
                    filter(User.dtags.any(DemogTag.label.in_(params[key])))
            if 'q_' in key:
                content = content.filter(getattr(Post, key).contains(params[key][0]))
            if key == 'sort':
                if params[key][0].lower() == 'date_old':
                    content = content.order_by(Post.time)
                    content = content.all()
                elif params[key][0].lower() == 'date_new':
                    content = content.order_by(Post.time.desc())
                    content = content.all()
                else:
                    content = content.all()
                    content = sorted(content, key=lambda x: getattr(x, 'sort_' + params[key][0].lower()), reverse=True)
    if len(params['sort']) == 0:
        content = content.all()
    active_cat = params['c'][0] if len(params['c']) > 0 else ''
    return render_template('content.html',
                           categories=category_dict,
                           active_category=active_cat,
                           active_ctags=params['ct'],
                           active_dtags=params['dt'],
                           content=content)


@app.route('/summary/', methods=['GET', 'POST'])
def summary():
    client = language.LanguageServiceClient()
    params = {}
    content = Post.query
    for key in ['c', 'ct']:
        params[key] = [titlecase(tag) for tag in request.args.getlist(key)]
        if len(params[key]) > 0:
            if key == 'c':
                content = content.filter(Post.category.has(label=params[key][0]))
            if key == 'ct':
                content = content.join(Post.ctags).\
                    filter(Post.ctags.any(ContentTag.label.in_(params[key])))
                if len(params['c']) == 0:
                    params['c'] = [content.first().category.label]
    active_cat = params['c'][0] if len(params['c']) > 0 else ''
    summary = summarizer(content.all(), client)
    return render_template('summary.html',
                           categories=category_dict,
                           active_category=active_cat,
                           active_ctags=params['ct'],
                           summary=summary)


@app.route('/react/<int:post_id>/<action>')
@login_required
def reaction(post_id, action):
    current_user.react_post(action, post_id)
    db.session.commit()
    return redirect(request.referrer)


@blueprint.route("/login/", methods=("GET", "POST"))
def login():
    return render_template("login.html", categories=category_dict)


@blueprint.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/<path:path>', methods=['GET', 'POST'])
@app.route('/<path:path>/', methods=['GET', 'POST'])
def render(path):
    return render_template(path + '.html',
                           categories=category_dict)


app.register_blueprint(google_blueprint, url_prefix="/join/")
app.register_blueprint(github_blueprint, url_prefix="/join/")
app.register_blueprint(blueprint)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)