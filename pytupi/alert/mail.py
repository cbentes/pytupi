import smtplib


class Mail:

    def __init__(self, user, password, user_email=None, smtp_server='smtp.gmail.com:587'):
        self.user = user
        self.password = password
        self.user_email = user_email if user_email is not None else user
        self.smtp_server = smtp_server

    def send(self, email_to, subject, msg):
        """ Send email message
        """
        msg_parts = list()
        msg_parts.append('From: {0}'.format(self.user_email))
        msg_parts.append('To: {0}'.format(email_to))
        msg_parts.append('Subject: {0}'.format(subject))
        msg_parts.append('')
        msg_parts.append(msg)
        email_msg = '\r\n'.join(msg_parts)
        server = smtplib.SMTP(self.smtp_server)
        server.ehlo()
        server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.user_email, email_to, email_msg)
        server.quit()
