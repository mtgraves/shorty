# flask generic imports
from flask import render_template, flash, redirect, url_for, request,\
        current_app, g, Markup
from flask_login import current_user, login_user, logout_user, login_required

# application-specific imports
from app import db
from app.main.forms import SearchForm, NewLinkForm
from app.models import UserTable, RandomLinkTable, RequestedLinkTable
from app.main import bp

# other imports
from werkzeug.urls import url_parse
from hashids import Hashids
import datetime

# =============================================================================
#       Create search form instance for navigation bar
# =============================================================================
@bp.before_app_request
def before_request():
    '''
    create search form instance before the request, and have it persist until
    the end of the request using the flask g container.
    '''
    if current_user.is_authenticated:
        g.search_form = SearchForm()


# =============================================================================
#       Expose application name and URL to all templates
# =============================================================================
@bp.before_app_request
def inject_app_information():
    '''
    expose application name and URL
    '''
    g.app_name = current_app.config['APPLICATION_NAME']
    g.app_url = request.url_root


# =============================================================================
#       Expose current user roles
# =============================================================================
@bp.before_app_request
def inject_currentUserPermissions():
    '''
    expose current_user application roles to all templates
    '''
    try:
        if current_user.is_authenticated:

            rr = db.session.query(UserTable).filter_by(
                    id=current_user.id).first().roles
            r_name_list = []
            for r in rr:
                r_name_list.append(r.role_name)

            g.current_user_roles = r_name_list
        else:
            g.current_user_roles = []
    except:
        g.current_user_roles = []


# =============================================================================
#       Index
# =============================================================================
@bp.route('/', methods=['GET','POST'])
@bp.route('/<url_code>', methods=['GET','POST'])
@login_required
def index(url_code='index'):

    # filter what is passed as url_code
    if (url_code == 'index' or url_code == None or url_code == ''):
        pass
    else:
        # any url suffix with a leading dash was randomly generated
        if url_code[0] == '_':
            converted_link = db.session.query(
                    RandomLinkTable).filter_by(
                            new_url_suffix = url_code).first()

        # no leading dash means it was a requested url
        else:
            converted_link = db.session.query(
                    RequestedLinkTable).filter_by(
                            new_url_suffix = url_code).first()

        # redirect if we found a link in the database
        if converted_link != None:
            return redirect(converted_link.original_url)

        # otherwise notify the user
        else:
            flash('could not find your link', category='warning')
            return redirect(url_for('main.index'))

    # create form instance
    form = NewLinkForm()

    if form.validate_on_submit():
        
        # create hashids instance
        hashids = Hashids(salt=current_app.config['APPLICATION_NAME'])

        # is user requesting a url suffix
        if form.request_url_suffix_true.data == True:

            # check if underscore is first character
            if form.request_url_suffix.data[0] == '_':
                flash('The first character of your requested URL suffix cannot be an underscore.',
                        category='warning')

            else:
                # determine if url suffix is already in requested database
                link_suffix = db.session.query(
                        RequestedLinkTable).filter_by(
                                new_url_suffix = form.request_url_suffix.data).first()

                if link_suffix != None:
                    flash('This URL suffix is already taken and corresponds\
                            with: '+link_suffix.original_url, category='warning')
                else:
                    new_url_suffix = form.request_url_suffix.data
                    new_url = request.url_root+new_url_suffix

                    new_link_entry = RequestedLinkTable(
                            user_id = current_user.id,
                            original_url = form.enter_link.data,
                            new_url = new_url,
                            new_url_suffix = new_url_suffix,
                            date_created = datetime.datetime.now()
                            )
                    db.session.add(new_link_entry)
                    db.session.commit()
     
                    flash(Markup('you have a new lazy url created: <br/>'+\
                            '<span class="copy_to_clipboard_field" id="clipboard-'+new_url_suffix+'"><b>'+new_url+'</b> </span><button \
                            class="btn btn-default" id="clipboard_btn-'+new_url_suffix+'">\
                            <span class="fa fa-lg fa-clipboard"></span> Copy to \
                            clipboard</button>'), category='success')


        else:
            # check if link already exists
            cl = db.session.query(
                    RandomLinkTable).filter_by(
                            original_url = form.enter_link.data).first()
            if cl != None:
                flash('This URL already has an entry in the system: '+cl.new_url,\
                        category='warning')
            else:

                next_link = len(db.session.query(
                        RandomLinkTable).order_by('id').all())+1
                
                # put a dash on the front of any randomly generated url path endings
                new_url_suffix = '_'+hashids.encode(next_link)
                new_url = request.url_root+new_url_suffix

                new_link_entry = RandomLinkTable(
                        user_id = current_user.id,
                        original_url = form.enter_link.data,
                        new_url = new_url,
                        new_url_suffix = new_url_suffix,
                        date_created = datetime.datetime.now()
                        )
                db.session.add(new_link_entry)
                db.session.commit()
                
                flash(Markup('you have a new lazy url created: <br/>'+\
                        '<span class="copy_to_clipboard_field" id="clipboard-'+new_url_suffix+'"><b>'+new_url+'</b> </span><button \
                        class="btn btn-default" id="clipboard_btn-'+new_url_suffix+'">\
                        <span class="fa fa-lg fa-clipboard"></span> Copy to \
                        clipboard</button>'), category='success')


    return render_template(
            'index.html',
            title='Home',
            form=form
            )


# =============================================================================
#       Search
# =============================================================================
@bp.route('/search')
@login_required
def search():

    # if form doesnt validate then return to previous page
    if not g.search_form.validate():
        return redirect(request.referrer)
    
    # perform search functionality to get things to return to client 
    

    return render_template(
            'search.html', 
            title='Search'
            )

