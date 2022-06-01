from app import db
from app.models import UserRolesTable
from app.email import send_email
from flask import render_template, current_app

# =============================================================================
#       new user login email - admin
# =============================================================================
def email_newuser_login_admin(the_user):
    '''
    send email to admin(s) whenever a new user first authenticates 
    successfully with their AD credentials.
    '''
    sender = current_app.config['EMAIL_HANDLE']

    subject = 'New '+str(current_app.config['APPLICATION_NAME'])+\
            ' user account needs review'

    # grab appropriate administrator user(s)
    recipient_users = db.session.query(
            UserRolesTable
        ).filter(
                UserRolesTable.role_id == 3
        ).all()

        #FIXME
    recipients = []
    for u in recipient_users:
        recipients.extend([u.associated_user.email])

    recipients = []

    text_body = render_template(
            'email/email_newuser_login_admin.txt', 
            the_user = the_user
            )
    html_body = render_template(
            'email/email_newuser_login_admin.html', 
            the_user = the_user
            )

    send_email(subject, sender, recipients, text_body, html_body)


# =============================================================================
#       new user login email - requesting user
# =============================================================================
def email_newuser_login_user(the_user):
    '''
    send email to user whenever they first authenticate
    successfully with their AD credentials.
    '''
    sender = current_app.config['EMAIL_HANDLE']

    subject = 'Your '+str(current_app.config['APPLICATION_NAME'])+\
            ' account request has been submitted'

    recipients = [the_user.email]

    text_body = render_template(
            'email/email_newuser_login_user.txt')
    html_body = render_template(
            'email/email_newuser_login_user.html')

    send_email(subject, sender, recipients, text_body, html_body)

# =============================================================================
#       new user account approved email - requesting user
# =============================================================================
def email_newuser_approval_user(the_user):
    '''
    send email to user whenever their account has been approved.
    '''
    sender = current_app.config['EMAIL_HANDLE']

    subject = 'Your '+str(current_app.config['APPLICATION_NAME'])+\
            ' account request has been approved'

    recipients = [the_user.email]

    text_body = render_template(
            'email/email_newuser_approval_user.txt')
    html_body = render_template(
            'email/email_newuser_approval_user.html')

    send_email(subject, sender, recipients, text_body, html_body)
