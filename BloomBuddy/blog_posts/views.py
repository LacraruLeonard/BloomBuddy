from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from BloomBuddy import db
from BloomBuddy.models import BlogPost, Comment
from BloomBuddy.blog_posts.forms import BlogPostForm, CommentForm
from flask import abort
from sqlalchemy import or_

blog_posts = Blueprint('blog_posts', __name__)


# Create


@blog_posts.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():
        blog_post = BlogPost(title=form.title.data, text=form.text.data, user_id=current_user.id)
        db.session.add(blog_post)
        db.session.commit()
        flash('Blog Post Created')
        return redirect(url_for('core.index'))
    return render_template('create_post.html', form=form)


# Blog post(Read and Add Comments)


# @blog_posts.route('/<int:blog_post_id>', methods=['GET', 'POST'])
# def blog_post(blog_post_id):
#  blog_post = BlogPost.query.get_or_404(blog_post_id)
#  form = CommentForm()
#  comments = blog_post.comments.order_by(Comment.timestamp.desc()).all()
#  if form.validate_on_submit():
#     comment = Comment(text=form.text.data, post=blog_post, user_id=current_user.id)
#      db.session.add(comment)
#     db.session.commit()
#     flash('Your comment has been added to the post', 'success')
#    return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
# return render_template('blog_post.html', title=blog_post.title, date=blog_post.date, post=blog_post, form=form, comments=comments)

@blog_posts.route('/<int:blog_post_id>', methods=['GET', 'POST'])
def blog_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    form = CommentForm()
    comments = blog_post.comments.order_by(Comment.timestamp.asc()).all()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id')
        if parent_id:
            parent_comment = Comment.query.get_or_404(parent_id)
            reply = Comment(text=form.text.data, post_id=blog_post_id, users_id=current_user.id)
            parent_comment.replies.append(reply)
            flash('Your reply has been added to the comment', 'success')
        else:
            comment = Comment(text=form.text.data, post_id=blog_post_id, users_id=current_user.id)
            db.session.add(comment)
            flash('Your comment has been added to the post', 'success')
        db.session.commit()
        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))
    return render_template('blog_post.html', title=blog_post.title, date=blog_post.date, post=blog_post, form=form,
                           comments=comments)


# Delete Comment


@blog_posts.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.users_id != current_user.id:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted', 'success')
    return redirect(url_for('blog_posts.blog_post', blog_post_id=comment.post_id))


# Update


@blog_posts.route('/<int:blog_post_id>/update', methods=['GET', 'POST'])
@login_required
def update(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    form = BlogPostForm()
    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.text = form.text.data
        db.session.commit()
        flash('Blog Post Updated')
        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post.id))

    elif request.method == 'GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text
    return render_template('create_post.html', title='Updating', form=form)


# Delete


@blog_posts.route('/<int:blog_post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(blog_post_id):
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog Post Deleted')
    return redirect(url_for('core.index'))


# Search


@blog_posts.route('/search')
def search():
    query = request.args.get('q')
    if query is not None:
        blog_posts = BlogPost.query.filter(or_(BlogPost.title.contains(query), BlogPost.text.contains(query))).all()
    else:
        blog_posts = []
    return render_template('search.html', blog_posts=blog_posts)


# Reply


@blog_posts.route('/<int:blog_post_id>/reply', methods=['POST'])
@login_required
def add_reply(blog_post_id):
    form = CommentForm()
    blog_post = BlogPost.query.get_or_404(blog_post_id)
    comments = blog_post.comments.order_by(Comment.timestamp.desc()).all()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id')
        parent_comment = Comment.query.get_or_404(parent_id)
        reply = Comment(text=form.text.data, post_id=blog_post_id, user_id=current_user.id)
        parent_comment.replies.append(reply)
        db.session.commit()
        flash('Your reply has been added to the comment', 'success')
        return redirect(url_for('blog_posts.blog_post', blog_post_id=blog_post_id))
    return render_template('blog_post.html', title=blog_post.title, date=blog_post.date, post=blog_post, form=form,
                           comments=comments)
