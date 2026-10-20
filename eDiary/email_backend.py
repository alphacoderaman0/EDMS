"""SMTP backend compatible with Python 3.12+ (Django 3.2 still passes keyfile)."""
import ssl
import threading

import smtplib
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.core.mail.utils import DNS_NAME


class EmailBackend(BaseEmailBackend):
    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        fail_silently=False,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        **kwargs,
    ):
        super().__init__(fail_silently=fail_silently)
        self.host = host or settings.EMAIL_HOST
        self.port = port or settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER if username is None else username
        self.password = settings.EMAIL_HOST_PASSWORD if password is None else password
        self.use_tls = settings.EMAIL_USE_TLS if use_tls is None else use_tls
        self.use_ssl = getattr(settings, 'EMAIL_USE_SSL', False) if use_ssl is None else use_ssl
        self.timeout = getattr(settings, 'EMAIL_TIMEOUT', None) if timeout is None else timeout
        self.ssl_keyfile = getattr(settings, 'EMAIL_SSL_KEYFILE', None) if ssl_keyfile is None else ssl_keyfile
        self.ssl_certfile = getattr(settings, 'EMAIL_SSL_CERTFILE', None) if ssl_certfile is None else ssl_certfile
        if self.use_ssl and self.use_tls:
            raise ValueError('EMAIL_USE_TLS and EMAIL_USE_SSL are mutually exclusive.')
        self.connection = None
        self._lock = threading.RLock()

    def _ssl_context(self):
        ctx = ssl.create_default_context()
        if self.ssl_certfile:
            ctx.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
        return ctx

    def open(self):
        if self.connection:
            return False

        connection_params = {'local_hostname': DNS_NAME.get_fqdn()}
        if self.timeout is not None:
            connection_params['timeout'] = self.timeout

        try:
            if self.use_ssl:
                self.connection = smtplib.SMTP_SSL(
                    self.host,
                    self.port,
                    context=self._ssl_context(),
                    **connection_params,
                )
            else:
                self.connection = smtplib.SMTP(self.host, self.port, **connection_params)
                if self.use_tls:
                    self.connection.starttls(context=self._ssl_context())

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                self.connection.close()
            except smtplib.SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                return 0
            num_sent = 0
            for message in email_messages:
                if self._send(message):
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep='\r\n'))
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
