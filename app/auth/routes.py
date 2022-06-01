# flask generic imports
from flask import render_template, flash, redirect, url_for, request,\
        current_app, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_principal import identity_changed, Identity, AnonymousIdentity,\
        identity_loaded

# application-specific imports
from app import db, admin_permission
from app.auth.forms import LoginForm, AssignRolesForm
from app.models import UserTable, RolesTable, UserRolesTable
from app.auth import bp
from app.auth.email import email_newuser_login_admin,\
        email_newuser_login_user, email_newuser_approval_user
from app.helpers import filter_argtype_and_arg

# other imports
from werkzeug.urls import url_parse
import ldap


# =============================================================================
#       Login
# =============================================================================
@bp.route('/login', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():

        # query database for user name
        user = UserTable.query.filter_by(username=form.username.data).first()

        # set AD connection variables
        DN = form.username.data + current_app.config['LDAP_DN_END']
        secret = form.password.data
        server = current_app.config['LDAP_SERVER_URL']
        port = current_app.config['LDAP_PORT']
        base = current_app.config['LDAP_BASE']
        scope = ldap.SCOPE_SUBTREE
        ze_filter = "(&(objectClass=user)(sAMAccountName=" + form.username.data + "))"
        attrs = ["*"]

        if user is None:
            
            # check if the username/password is valid with AD
            try:

                # initialize connection object for accessing LDAP server
                l = ldap.initialize(server)
                l.protocol_version = ldap.VERSION3
                l.set_option(ldap.OPT_REFERRALS, 0)

                # bind with the ldap server using user credentials
                l.simple_bind_s(DN, secret)

                # query for information about user
                r = l.search(base, scope, ze_filter, attrs)
                type, user = l.result(r, 60)
                name, attrs = user[0]
                
                # lastname
                try:
                    lastname = attrs['sn'][0].decode('utf-8')
                except:
                    lastname = ''

                # firstname
                try:
                    firstname = attrs['givenName'][0].decode('utf-8')
                except:
                    firstname = ''

                # phone
                try:
                    phone = attrs['telephoneNumber'][0].decode('utf-8')
                except:
                    phone = None

                # email
                try:
                    email_addr = attrs['fixme'][0].decode('utf-8')
                except:
                    email_addr = ''

                # determine account entry status (active or requested)
                if current_app.config['ACCOUNTS_NEED_APPROVAL'] == True:
                    entry_status = 1
                else:
                    entry_status = 2

                # create user_table entry
                new_user = UserTable(
                    username = form.username.data,
                    lastname = lastname,
                    firstname = firstname,
                    email = email_addr,
                    phone = phone,
                    user_status = entry_status
                )
                db.session.add(new_user)
                db.session.commit()
                
                # be a good citizen and unbind from ldap server
                l.unbind_s()
                
                if current_app.config['ACCOUNTS_NEED_APPROVAL'] == True:
                    
                    # send emails to admin and requesting user
                    email_newuser_login_admin(new_user)
                    email_newuser_login_user(new_user)

                    flash('A request has been generated for your account to be created.',\
                            category='success')

                    return redirect(url_for('auth.login'))
                else:
                    user = new_user

            except:
                
                flash('Credentials not recognized.  Please enter your username and password.')
                return redirect(url_for('auth.login'))

        else:
            try:
                # initialize connection object for accessing LDAP server
                l = ldap.initialize(server)
                l.protocol_version = ldap.VERSION3
                l.set_option(ldap.OPT_REFERRALS, 0)

                # bind with the ldap server using user credentials
                l.simple_bind_s(DN, secret)
 
                # be a good citizen and unbind from ldap server
                l.unbind_s()

                if user.user_status == 1:
                    flash('Your account has not yet been approved.  You will be able to log in once the\
                    approval process is complete.')
                    return redirect(url_for('auth.login'))

                elif user.user_status == 3:
                    flash('Your account has been deactivated.  Please contact your admin for access')
                    return redirect(url_for('auth.login'))


            except:
                flash('You entered an incorrect password.  Please enter your AD (Windows)\
                password')
                return redirect(url_for('auth.login'))


        # if you made it here, the user must be 'Active' in the system and have been able
        #       to authenticate using their AD credentials, so log them in
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        # nofity Flask-Principal of user identity
        identity_changed.send(current_app._get_current_object(),
                identity=Identity(user.id))


        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)

    return render_template(
            'auth/login.html',
            title='Sign In',
            app_name = current_app.config['APPLICATION_NAME'],
            form=form
            )

# =============================================================================
#       Logout
# =============================================================================
@bp.route('/logout')
def logout():
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is now anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('auth.login'))


# =============================================================================
#       User Admin
# =============================================================================
@bp.route('/useradmin', methods=['GET','POST'])
@bp.route('/useradmin/<req_type>')
@bp.route('/useradmin/<req_type>/<req_arg>', methods=['GET','POST'])
@login_required
@admin_permission.require(http_exception=401)
def useradmin(req_type=None, req_arg=None):
    '''
    route for user administration
    '''
    # re-route request if item_type is anything undesired or if only item_type is passed
    allowed_req_types = [
            None, 
            'enable_account', 
            'disable_account', 
            'edit_account'
            ]

    # perform pre-filter on passed URL components
    is_base, passed_args_ok = filter_argtype_and_arg(
            passed_arg_type = req_type,
            allowed_arg_types = allowed_req_types,
            passed_arg = req_arg
            )
    
    if passed_args_ok == False:
        return redirect(url_for('auth.useradmin'))

    if is_base == False:
        
        # make sure req_arg is an id of an existing user
        try:
            user = db.session.query(
                    UserTable).filter_by(
                            id=req_arg).first()
            if user == None:
                return redirect(url_for('auth.useradmin'))
        except:
            return redirect(url_for('auth.useradmin'))

        
        if req_type == 'enable_account':
            
            # set user status to 'active' in the database
            user.user_status = 2
            db.session.commit()
            
            # send notification email to user
            email_newuser_approval_user(user)

            return redirect(url_for('auth.useradmin'))

        elif req_type == 'disable_account':
            
            # set user status to 'disabled' in the database
            user.user_status = 3
            db.session.commit()

            return redirect(url_for('auth.useradmin'))
        
        elif req_type == 'edit_account':

            # instantiate roles form
            roles_form = AssignRolesForm(
                    roles=[role.id for role in user.roles]
                    )

            # set role choices from roles_table
            roles_form.roles.choices = [
                (row.id, row.role_name) for row in RolesTable.query.all()]

            if roles_form.validate_on_submit():
                
                new_roles = roles_form.roles.data
                user_roles = db.session.query(
                        UserRolesTable).filter_by(
                                user_id = user.id).all()
                user_roles_roleids = [r.role_id for r in user_roles]

                # add new roles
                for r in new_roles:
                    if r not in user_roles_roleids:
                        new_role = UserRolesTable(
                                user_id = user.id,
                                role_id = r
                                )
                        db.session.add(new_role)
                        db.session.flush()

                # remove roles
                for r in user_roles:
                    if r.role_id not in new_roles:
                        db.session.delete(r)
                        db.session.flush()

                # commit any changes made
                db.session.commit()


            return render_template(
                    'auth/user_edit.html',
                    title='Edit User',
                    user = user,
                    roles_form = roles_form
                    )

    else:
        # get, from the database, all user accounts...
        # pending approval
        pending_accounts = db.session.query(
                UserTable).filter_by(user_status=1).all()
        # active
        active_accounts = db.session.query(
                UserTable).filter_by(user_status=2).all()
        # disabled/denied
        disabled_accounts = db.session.query(
                UserTable).filter_by(user_status=3).all()


        return render_template(
                'auth/user_admin.html',
                title='User Administration',
                pending_accounts = pending_accounts,
                active_accounts = active_accounts,
                disabled_accounts = disabled_accounts
                )



