# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
from gluon.tools import Service
import pandas as pd


def index():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

# ---- API (example) -----


@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET':
        raise HTTP(403)
    return response.json({'status': 'success', 'email': auth.user.email})

# ---- Smart Grid (example) -----


# can only be accessed by members of admin groupd
@auth.requires_membership('admin')
def grid():
    response.view = 'generic.html'  # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables:
        raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[
                             tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----


def wiki():
    auth.wikimenu()  # add the wiki to the menu
    return auth.wiki()

# ---- Action for login/register/etc (required for auth) -----


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


service = Service()


def call():
    return service()


def load_recommendations():
    item_similarity_df = pd.read_csv(
        "applications/matchingPets/static/item_similarity_df33.csv", index_col=0)
    print("item_similarity_df cached in memory")
    return item_similarity_df


item_similarity_df = cache.ram(
    'item_similarity_df3', load_recommendations, None)
print(item_similarity_df.head())


def check_liked(recommended_user, liked_users):
    for userId, user in liked_users.items():
        if recommended_user == user["displayName"]:
            return True
    return False


def get_similar_users(displayName, rating):
    try:
        similar_score = item_similarity_df[displayName]*(rating-2.5)
        similar_users = similar_score.sort_values(ascending=False)
    except:
        print("don't have user in model")
        similar_users = pd.Series([])

    return similar_users


def CORS(f):
    """
    Enables CORS for any action
    """
    def wrapper(*args, **kwds):
        if request.env.http_origin and request.env.request_method == 'OPTIONS':
            response.view = 'generic.json'
            return dict()
        return f(*args, **kwds)
    return wrapper


@CORS
@service.json
def get_recommendations(liked_users):

    print(liked_users.items())
    similar_users = pd.DataFrame()

    for userId, user in liked_users.items():
        similar_users = similar_users.append(get_similar_users(
            user["displayName"], user["rating"]), ignore_index=True)

    all_recommend = similar_users.sum().sort_values(ascending=False)

    recommended_users = []
    for user, score in all_recommend.iteritems():
        if not check_liked(user, liked_users):
            recommended_users.append(user)

    if len(recommended_users) > 10:
        recommended_users = recommended_users[0:5]
        return recommended_users


# def api():
#     def GET():
#         if not request.env.request_method == 'GET':
#         raise HTTP(403)
#         return response.json({'status': 'success', 'email': auth.user.email})
#     return locals()
