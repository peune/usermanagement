import emails
from emails.template import JinjaTemplate
from typing import Dict, Any

from config import settings
import schemas

def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> bool:
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=("User Management System", "noreply@usermanagement.com"),
    )
    smtp_options = {
        "host": settings.SMTP_SERVER,
        "port": settings.SMTP_PORT,
        "user": settings.SMTP_USERNAME,
        "password": settings.SMTP_PASSWORD,
        "tls": True,
    }
    return message.send(to=email_to, render=environment, smtp=smtp_options)

def send_new_account_email(email_to: str, user: schemas.User): 
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {user.name}"
    with open("templates/new_account_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "username": user.name,
            "email": email_to,
            "user": user
        },
    )

def send_account_approval_request(admin_email: str, user: schemas.User): # , username: str, user_email: str):
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Approval required for new user {user.name}"
    with open("templates/approval_request_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=admin_email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "username": user.name,
            "user_email": user.email,
            "user": user
        },
    )

def send_password_reset_email(user: schemas.User, token: str):
    project_name = settings.PROJECT_NAME
    reset_link = f"{settings.MAIN_URL}/reset-password?token={token}"
    subject = f"{project_name} - Password Reset Request for {user.name}"
    with open("templates/password_reset.html") as f:
        template_str = f.read()
    send_email(
        email_to=user.email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "user_name": user.name,
            "reset_link": reset_link
        },
    )

