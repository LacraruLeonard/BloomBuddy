from flask import render_template, request, Blueprint
from BloomBuddy.models import BlogPost

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return render_template('home.html')


@core.route('/blogs')
def index():
    page = request.args.get('page', 1, type=int)
    blog_posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', blog_posts=blog_posts, current_url=request.path)


@core.route('/info')
def info():
    return render_template('info.html')
