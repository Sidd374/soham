from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import pytz
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__,
            static_url_path='',
            static_folder='Soham/static')

app.secret_key = "374375376"
app.permanent_session_lifetime = timedelta(days=1)
app.static_folder = 'static'

app.config["MYSQL_HOST"] = "43.225.54.56"
app.config["MYSQL_USER"] = "sohamgu4_ngma"
app.config["MYSQL_PASSWORD"] = "ngmaMysql*123"
app.config["MYSQL_DB"] = "sohamgu4_ngma_db"

db = MySQL(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='soham.mail.noreply@gmail.com',
    MAIL_PASSWORD='Soham123!'
)

send_email = Mail(app)

serial = URLSafeTimedSerializer('374375376')
serial2 = URLSafeTimedSerializer('377378379')


@app.route('/login', methods=['POST', 'GET'])
def index():
    if "user" in session:
        return redirect(url_for('homepage'))

    # if request.method == 'POST':
    if 'username' in request.form and 'password' in request.form:

        username = request.form.get('username')
        password = request.form.get('password')

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s ",
                       (username, username))
        info = cursor.fetchone()

        if info is not None:
            if check_password_hash(info['user_pass'], password) and info['user_confirmed'] == 0 and (
                    info['user_email'] == username or info['user_login'] == username):
                return "Please confirm your email."

            elif check_password_hash(info['user_pass'], password) and (
                    info['user_email'] == username or info['user_login'] == username):
                session['user'] = info['user_login']
                session['display_name'] = info['display_name']
                session['user_id'] = info['ID']

                return redirect(url_for('homepage'))

            else:
                return "Invalid credentials"

        return "User not found"

    return render_template("SohamLogIn.html")


@app.route('/', methods=['POST', 'GET'])
def reg():
    if "username" in request.form and "email" in request.form and "password" in request.form and "displayname" in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        display_name = request.form['displayname']
        time_code = datetime.now()
        password_hashed = generate_password_hash(password, "pbkdf2:sha256", salt_length=8)

        if username is not None and email is not None and password is not None and display_name is not None:

            check_email_login = db.connection.cursor(MySQLdb.cursors.DictCursor)
            check_email_login.execute("SELECT * FROM ngma2_users WHERE user_email=%s or user_login=%s",
                                      (email, username))
            info = check_email_login.fetchone()

            if info is not None:
                return "Username or email address is already in use."

            token = serial.dumps(email, salt='email_confirm')

            msg = Message('Confirm your So-ham Account', sender='sohamnoreply@gmail.com', recipients=[email])
            confirm_link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Hi {},\r\n\nClick this link to confirm your email: {} .\r\n\nIf this action was not performed ' \
                       'by ' \
                       'you, please ignore this email.'.format(display_name, confirm_link)
            send_email.send(msg)

            register_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            register_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_users(user_login, user_pass, user_email, display_name, "
                "user_registered,user_confirmed) VALUES(%s,%s,%s,%s,%s,%s)",
                (username, password_hashed, email, display_name, time_code, 0))

            db.connection.commit()

        return 'A confirmation email has been sent to your email. Make sure to check your spam folder as well.'

    return render_template("index.html")


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serial.loads(token, salt='email_confirm', max_age=3600)

        confirm_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        # Cursor executes the SQL statement and returns a tuple
        confirm_cursor.execute("UPDATE ngma2_users SET user_confirmed=%s WHERE user_email=%s", (1, email))
        db.connection.commit()

    except SignatureExpired:
        return 'Token expired.'

    return 'Your email has been confirmed! You can log in now.'


@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot():
    if "email" in request.form:
        email = request.form["email"]
        token = serial2.dumps(email, salt='forgot_password')

        msg = Message('Change your So-ham password', sender='sohamnoreply@gmail.com', recipients=[email])
        change_pw_link = url_for('enter_password', token=token, _external=True)
        msg.body = 'Change your password using the following link {} .\r\n\nIf this action was not performed by you, ' \
                   'please ignore this email.'.format(change_pw_link)
        send_email.send(msg)

        return "A mail has been sent to your email. Please click on it and follow the instructions given. Make sure " \
               "to check your spam folder as well. "

    return render_template("forgot_password.html")


@app.route('/enter_password/<token>', methods=['POST', 'GET'])
def enter_password(token):
    try:
        email = serial2.loads(token, salt='forgot_password', max_age=3600)

        if request.method == "POST":
            if 'password' in request.form:
                password = request.form['password']
                cursor4 = db.connection.cursor(MySQLdb.cursors.DictCursor)

                cursor4.execute("UPDATE ngma2_users SET user_pass=%s WHERE user_email=%s", (password, email))
                db.connection.commit()
                return 'Your password has been changed.'

        #     else:
        #         return render_template("new_pw.html")
        #
        # return render_template("new_pw.html")

    except SignatureExpired:
        return 'Token expired.'


@app.route('/submit_post', methods=['POST', 'GET'])
def submit_post():
    if "user" in session:
        if 'post_content' in request.form:
            # Upload it first, then:-
            post_title = request.form['post_title']
            post_content = request.form['post_content']
            comment_status = 'open'
            ping_status = 'closed'
            utc = pytz.utc
            post_date = datetime.now()
            post_date_gmt = datetime.now(tz=utc)
            extension = "image/jpeg"
            guid = "..."
            username = session['user']
            post_author = session['user_id']

            # get_author = db.connection.cursor(MySQLdb.cursors.DictCursor)
            # get_author.execute("SELECT * FROM ngma2_users WHERE user_login=%s", (username))
            # info = get_author.fetchone()
            # post_author = info['ID']

            post_db = db.connection.cursor(MySQLdb.cursors.DictCursor)
            post_db.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_posts(post_author, post_date, post_date_gmt, post_content, post_title, post_modified, post_modified_gmt, guid, post_mime_type, ping_status, comment_status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (post_author, post_date, post_date_gmt, post_content, post_title, post_date, post_date_gmt, guid,
                 extension, ping_status, comment_status))

            db.connection.commit()

            return render_template("submitForm.html", user=session['user'])

    return render_template("submitForm.html", user=session['user'])


@app.route('/like/<author_id>/<post_id>', methods=['POST', 'GET'])
def like(author_id, post_id):
    if 'user' in session:

        like_check_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        like_check_cursor.execute("SELECT * FROM ngma2_exc_votes WHERE (post_id=%s AND user_id=%s)",
                                  (post_id, session['user_id']))
        liked = like_check_cursor.fetchone()

        if liked is None:
            like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            like_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_votes(author_id, post_id, user_id, status) VALUES(%s,%s,%s,%s)",
                (author_id, post_id, session['user_id'], '1'))
            db.connection.commit()

        elif liked['status'] == 1:
            unlike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            unlike_cursor.execute("UPDATE ngma2_exc_votes SET status=%s WHERE user_id=%s AND post_id=%s",
                                  (0, session['user_id'], post_id))
            db.connection.commit()

        else:
            relike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            relike_cursor.execute(
                "UPDATE ngma2_exc_votes SET status=%s WHERE (user_id=%s AND post_id=%s)",
                (1, session['user_id'], post_id))
            db.connection.commit()

        return redirect(url_for('homepage'))
    else:
        return "Please log in!"


@app.route('/upload', methods=['POST', 'GET'])
def uploader():
    if 'user' in session:
        if request.method == 'POST':
            file = request.files['file']


@app.route('/homepage')
def homepage():
    # if 'user' in session:
    home_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    home_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_status=%s AND post_parent=%s AND guid IS NOT NULL) ORDER BY post_date DESC LIMIT 30",
        ('publish', '0'))

    posts = home_cursor.fetchall()

    for one_post in posts:
        author_current = one_post['post_author']
        author_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        author_cursor.execute("SELECT display_name FROM ngma2_users WHERE ID=%s", [author_current])
        author_str = author_cursor.fetchone()
        one_post['post_author_name'] = author_str['display_name']
        author_cursor.close()

        pp_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        pp_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
            (author_current, 'inherit', '0'))
        profile_pic = pp_cursor.fetchone()
        if profile_pic is not None:
            one_post['pp_link'] = profile_pic['guid']
        else:
            one_post['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
        pp_cursor.close()

        post_id = one_post['ID']
        like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        like_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)",
                            ([post_id], '1'))
        post_likes = like_cursor.fetchone()
        one_post['likes'] = post_likes['total']
        like_cursor.close()

        post_id = one_post['ID']
        home_photo_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        home_photo_cursor.execute("SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)", (post_id,'attachment'))
        display_photo = home_photo_cursor.fetchone()
        # one_post['guid'] = display_photo['guid']

        view_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        view_cursor.execute("SELECT * FROM ngma2_postmeta WHERE(post_id=%s AND meta_key=%s)",(post_id,'_exc_views_count'))
        view_count = view_cursor.fetchone()
        one_post['views'] = view_count['meta_value']

        if display_photo is not None:
            one_post['guid'] = display_photo['guid']
        else:
            one_post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"

    if posts is not None:
        return render_template("homePage.html", posts=posts)
    else:
        return "No posts to display."


@app.route('/post/<post_id>')
def post(post_id):
    post_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    post_cursor.execute("SELECT * FROM ngma2_posts WHERE ID= %s", [post_id])
    post_page = post_cursor.fetchone()

    author_current = post_page['post_author']
    post_author_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    post_author_cursor.execute("SELECT display_name FROM ngma2_users WHERE ID=%s", [author_current])
    author_name = post_author_cursor.fetchone()
    post_page['display_name'] = author_name['display_name']
    post_author_cursor.close()

    post_follow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    post_follow_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_status=%s)",
        ([author_current], '1'))
    post_profile_followers = post_follow_cursor.fetchone()
    post_page['follows'] = post_profile_followers['total']

    child_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    child_cursor.execute("SELECT * FROM ngma2_posts WHERE post_parent = %s", [post_id])
    child_posts = child_cursor.fetchone()

    comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    comment_cursor.execute("SELECT * FROM ngma2_comments WHERE comment_post_ID=%s", [post_id])
    post_comments = comment_cursor.fetchall()

    return render_template("artDescription.html", post_comments=post_comments, post_page=post_page,
                           post_children=child_posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if "email" in request.form:
        email = request.form['email']
        name = request.form['name']
        subject = request.form['subject']
        message = request.form['message']
        receiver = "soham.ngma@gmail.com"

        if email is not None and name is not None and subject is not None and message is not None:

            msg = Message(subject, sender='sohamnoreply@gmail.com', recipients=[receiver])
            msg.body = 'Sender email: {}\r\nName: {}\r\nMessage:{}'.format(email, name, message)
            send_email.send(msg)

            return "Email has been sent."

        else:
            return "Please fill all details correctly."

    return render_template("contact.html")


# @app.route('/blog', methods=['POST', 'GET'])
# def blog():
#     comment_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
#     comment_cursor.execute("SELECT * FROM ngma2_comments WHERE comment_post_ID=%s",(comment_post_id))
#
#     obj = comment_cursor.fetchall()
#     return render_template("blog.html",obj = obj)


@app.route('/museum')
def museum():
    return render_template("museumCorner.html")


@app.route('/theme/<theme_id>')
def theme(theme_id):
    theme_posts_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    theme_posts_cursor.execute("SELECT * FROM ngma2_themes WHERE ID=%s", [theme_id])
    theme_post = theme_posts_cursor.fetchone()

    list(theme_post['post_content'])

    theme_comments_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    theme_comments_cursor.execute("SELECT * FROM ngma2_theme_comments WHERE comment_post_ID=%s", [theme_id])
    theme_comments = theme_comments_cursor.fetchall()

    for comment in theme_comments:
        author_id_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        em = comment['comment_author_email']
        author_id_cursor.execute("SELECT * FROM ngma2_users WHERE user_email=%s", [em])
        author_details = author_id_cursor.fetchone()
        author_current = author_details['ID']

        comment_pp_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        comment_pp_cursor.execute(
            "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
            (author_current, 'inherit', '0'))
        profile_pic = comment_pp_cursor.fetchone()
        if profile_pic is not None:
            comment['pp_link'] = profile_pic['guid']
        else:
            comment['pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
        comment_pp_cursor.close()

    return render_template("theme.html", theme_post=theme_post, theme_comments=theme_comments)


@app.route('/events')
def events():
    return render_template("events.html")


@app.route('/exhibitions')
def exhibitions():
    return render_template("exhibitions.html")


@app.route('/livestream')
def livestream():
    return render_template("livestream.html")


@app.route('/hall')
def hall():
    hall_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    hall_cursor.execute("SELECT * FROM ngma2_hall")
    hall_posts = hall_cursor.fetchall()

    return render_template("HallOfFame.html", hall_posts=hall_posts)


@app.route('/profile/<user_id>')
def profile(user_id):

    profile_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    profile_cursor.execute("SELECT * FROM ngma2_users WHERE ID= %s", [user_id])
    profile_details = profile_cursor.fetchone()

    profile_picture_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    profile_picture_cursor.execute("SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)", (user_id, 'inherit', '0'))
    profile_pic = profile_picture_cursor.fetchone()

    if profile_pic['guid'] is not None:
        profile_details['pp_link'] = profile_pic['guid']
    else:
        profile_details['pp_link']= "https://so-ham.in/wp-content/uploads/2021/09/61_5315.jpg"

    like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    like_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (author_id=%s AND status=%s)",
                        ([user_id], '1'))
    profile_likes = like_cursor.fetchone()
    profile_details['likes'] = profile_likes['total']

    follow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    follow_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_status=%s)",
        ([user_id], '1'))
    profile_followers = follow_cursor.fetchone()
    profile_details['follows'] = profile_followers['total']

    following_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    following_cursor.execute(
        "SELECT COUNT(follower_id) AS total FROM ngma2_exc_followers WHERE (follower_user_id=%s AND follower_status=%s)",
        ([user_id], '1'))
    profile_following = following_cursor.fetchone()
    profile_details['following'] = profile_following['total']

    profile_posts_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    profile_posts_cursor.execute(
        "SELECT * FROM ngma2_posts WHERE (post_author=%s AND post_status=%s AND post_parent=%s) ORDER BY post_date DESC LIMIT 20",
        (user_id, 'publish', '0'))
    profile_posts = profile_posts_cursor.fetchall()

    # profile_liked_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # profile_liked_cursor.execute("SELECT * FROM ngma2_exc_votes WHERE user_id=%s", [user_id])
    # liked_posts = profile_liked_cursor.fetchall()

    # profile_liked_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    # profile_liked_cursor.execute("SELECT * FROM ngma2_posts INNER JOIN ngma2_exc_votes ON ngma2_posts.post_author=ngma2_exc_votes.user_id")
    # liked_posts = profile_liked_cursor.fetchall()


    for one_profile_post in profile_posts:
        profile_post_id = one_profile_post['ID']
        profile_post_like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_post_like_cursor.execute(
            "SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)",
            ([profile_post_id], '1'))
        profile_post_likes = profile_post_like_cursor.fetchone()
        one_profile_post['likes'] = profile_post_likes['total']
        profile_post_like_cursor.close()

        profile_photo_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_photo_cursor.execute("SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s)",
                                  (profile_post_id, 'attachment'))
        display_photo = profile_photo_cursor.fetchone()

        profile_view_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_view_cursor.execute("SELECT * FROM ngma2_postmeta WHERE(post_id=%s AND meta_key=%s)",(profile_post_id, '_exc_views_count'))
        profile_view_count = profile_view_cursor.fetchone()
        one_profile_post['views'] = profile_view_count['meta_value']

        if display_photo is not None:
            one_profile_post['guid'] = display_photo['guid']
        else:
            return str(profile_post_id)

    # for one_post in liked_posts:
    #     author_rn = one_post['post_author']
    #     profile_author_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    #     profile_author_cursor.execute("SELECT display_name FROM ngma2_users WHERE ID=%s", [author_rn])
    #     author_str = profile_author_cursor.fetchone()
    #     one_post['post_author_name'] = author_str['display_name']
    #     profile_author_cursor.close()
    #
    #     profile_pp_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    #     profile_pp_cursor.execute(
    #         "SELECT * FROM ngma2_posts WHERE(post_author=%s AND post_status=%s AND post_parent=%s)",
    #         (author_rn, 'inherit', '0'))
    #     profile_pic = profile_pp_cursor.fetchone()
    #     if profile_pic is not None:
    #         one_post['pp_link'] = profile_pic['guid']
    #     else:
    #         one_post[
    #             'pp_link'] = "https://plusvalleyadventure.com/wp-content/uploads/2020/11/default-user-icon-8.jpg"
    #     profile_pp_cursor.close()
    #
    #     post_id = one_post['ID']
    #     profile_like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    #     profile_like_cursor.execute("SELECT COUNT(vote_id) AS total FROM ngma2_exc_votes WHERE (post_id=%s AND status=%s)",
    #                         ([post_id], '1'))
    #     post_likes = profile_like_cursor.fetchone()
    #     one_post['likes'] = post_likes['total']
    #     like_cursor.close()
    #
    #     post_id = one_post['ID']
    #     profile_photo_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    #     profile_photo_cursor.execute(
    #         "SELECT * FROM ngma2_posts WHERE (post_parent=%s AND post_type=%s AND guid is NOT NULL)",
    #         (post_id, 'attachment'))
    #     display_photo = profile_photo_cursor.fetchone()
    #     # one_post['guid'] = display_photo['guid']
    #
    #     profile_view_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    #     profile_view_cursor.execute("SELECT * FROM ngma2_postmeta WHERE(post_id=%s AND meta_key=%s)",
    #                         (post_id, '_exc_views_count'))
    #     profile_view_count = profile_view_cursor.fetchone()
    #     one_post['views'] = profile_view_count['meta_value']
    #
    #     if display_photo is not None:
    #         one_post['guid'] = display_photo['guid']
    #     else:
    #         one_post['guid'] = "http://www.tgsin.in/images/joomlart/demo/default.jpg"


    return render_template("userProfile.html", profile_details=profile_details, posts=profile_posts) #, liked_posts = liked_posts)


@app.route('/profile/follow/<follower_author_id>', methods=['POST', 'GET'])
def follow(follower_author_id):
    if 'user' in session:
        follow_check_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        follow_check_cursor.execute(
            "SELECT * FROM ngma2_exc_followers WHERE (follower_author_id=%s AND follower_user_id=%s)",
            (follower_author_id, session['user_id']))
        followed = follow_check_cursor.fetchone()

        if followed is None:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            follow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            follow_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_followers(follower_author_id, follower_user_id, follower_status) VALUES(%s,%s,%s)",
                (follower_author_id, session['user_id'], '1'))
            db.connection.commit()

        elif followed['follower_status'] == 1:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            unfollow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            unfollow_cursor.execute(
                "UPDATE ngma2_exc_followers SET follower_status=%s WHERE (follower_user_id=%s AND follower_author_id=%s)",
                (0, session['user_id'], follower_author_id))
            db.connection.commit()

        else:

            if session['user_id'] == follower_author_id:
                return "You can't follow yourself!"

            refollow_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            refollow_cursor.execute("UPDATE ngma2_exc_followers SET follower_status=%s WHERE (follower_user_id=%s AND "
                                    "follower_author_id=%s)",
                                    (1, session['user_id'], follower_author_id))
            db.connection.commit()

        return redirect(url_for('profile', user_id=follower_author_id))
    else:
        return "Please log in!"


@app.route('/profile/profile_like/<author_id>/<post_id>', methods=['POST', 'GET'])
def profile_like(author_id, post_id):
    if 'user' in session:
        profile_like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        profile_like_cursor.execute("SELECT * FROM ngma2_exc_votes WHERE (post_id=%s AND user_id=%s)",
                                  (post_id, session['user_id']))
        liked = profile_like_cursor.fetchone()

        if liked is None:
            like_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            like_cursor.execute(
                "INSERT INTO sohamgu4_ngma_db.ngma2_exc_votes(author_id, post_id, user_id, status) VALUES(%s,%s,%s,%s)",
                (author_id, post_id, session['user_id'], '1'))
            db.connection.commit()

        elif liked['status'] == 1:
            profile_unlike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            profile_unlike_cursor.execute("UPDATE ngma2_exc_votes SET status=%s WHERE user_id=%s AND post_id=%s",
                                  (0, session['user_id'], post_id))
            db.connection.commit()

        else:
            profile_relike_cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            profile_relike_cursor.execute(
                "UPDATE ngma2_exc_votes SET status=%s WHERE (user_id=%s AND post_id=%s)",
                (1, session['user_id'], post_id))
            db.connection.commit()

        return redirect(url_for('profile', user_id= author_id))
    else:
        return "Please log in!"


# @app.route('/logout')
# def logout():
#     session.pop("user", None)
#     return redirect(url_for("/login"))


# Runs app
if __name__ == '__main__':
    app.debug = True
    app.run()

