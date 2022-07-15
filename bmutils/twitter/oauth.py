import appdirs
import datetime
import json
import os
import tweepy
import webbrowser

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing import Process, Queue
from pathlib import Path
from ssl import SSLContext, PROTOCOL_TLS_SERVER


class LocalHTTPSServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, cert, ipc_queue):
        super().__init__(server_address, RequestHandlerClass)
        self.cert = cert
        self.queue = ipc_queue

        ssl_context = SSLContext(PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert)
        self.socket = ssl_context.wrap_socket(self.socket, server_side=True)


class LocalOAuthHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)

    def log_request(code='-', size='-'):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.server.queue.put(f"https://127.0.0.1:8000{self.path}".encode("utf-8"))  # noqa: E501
        self.wfile.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>bmutils Twitter Authentication Landing Page</title>
</head>

<body>
<h1><code>bmutils</code> Twitter Authentication Landing Page</h1>
<p><code>bmutils</code> has received a response from Twitter. Twitter is
expecting the following string from <code>bmutils</code>:<p>
<pre>https://127.0.0.1:8000{self.path}</pre>
<p>Your data will be collected and/or deleted after Twitter receives this
string. Note that getting Twitter data <em>may</em> take several minutes due to
API limits.</p>
<p>You can close your browser window/tab now.</p>
</body>
</html>
""".encode("utf-8"))  # noqa: E501


def get_credentials(username, force_update):
    config = Path(appdirs.user_config_dir("bmutils", "", roaming=True)) / "twitter.json"  # noqa: E501

    if not config.exists():
        print(f"{config} does not exist. You need a Twitter developer account.")  # noqa: E501
        creds = credential_prompt(username)

        os.makedirs(config.parent, exist_ok=True)
        with open(config, "w") as fp:
            json.dump(creds, fp, indent=4, separators=(',', ': '))
    else:
        with open(config, "r") as fp:
            creds = json.load(fp)

        if force_update:
            print("Credential update requested. You need a Twitter developer account.")  # noqa: E501
        else:
            try:
                our_creds = creds[username]
            except KeyError:
                print(f"{username} key in {config} does not exist. You need a Twitter developer account.")  # noqa: E501
                force_update = True

        if force_update:
            our_creds = credential_prompt(username)
            creds.update(our_creds)
            with open(config, "w") as fp:
                json.dump(creds, fp, indent=4, separators=(',', ': '))

        return our_creds


# Because of how OAuth 2.0 PKCE works (on Twitter?), we must use SSL, and
# we must redirect to a HTTPS link on localhost.
# A lot of this was taken from:
# https://www.misterpki.com/python-self-signed-certificate/ and
# https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#key-serialization  # noqa: E501
def create_certificate(cert_path):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Some Where"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u""),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"BMUtils"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"127.0.0.1"),
    ])
    cert = x509.CertificateBuilder() \
               .subject_name(subject) \
               .issuer_name(issuer) \
               .public_key(key.public_key()) \
               .serial_number(x509.random_serial_number()) \
               .not_valid_before(datetime.datetime.utcnow()) \
               .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365)) \
               .add_extension(x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),  # noqa: E501
                              critical=False,).sign(key, hashes.SHA256())

    with open(cert_path, "w") as fp:
        fp.write(key.private_bytes(
                 encoding=serialization.Encoding.PEM,
                 format=serialization.PrivateFormat.TraditionalOpenSSL,
                 encryption_algorithm=serialization.NoEncryption())
                 .decode("utf-8"))
        fp.write(cert.public_bytes(serialization.Encoding.PEM).decode("utf-8"))


def spawn_https_server(cert, q):
    server = LocalHTTPSServer(("", 8000), LocalOAuthHandler, cert, q)
    server.serve_forever()


def get_client(creds):
    fake_cert = Path(appdirs.user_config_dir("bmutils", "", roaming=True)) / "cert.pem"  # noqa: E501

    if not fake_cert.exists():
        create_certificate(fake_cert)

    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=creds["client_id"],
        redirect_uri="https://127.0.0.1:8000/",
        scope=["tweet.read", "users.read", "bookmark.read",
               "bookmark.write", "list.read"],
        client_secret=creds["client_secret"]
    )

    q = Queue()  # Use a process so we don't block main thread.
    server_process = Process(target=spawn_https_server, args=(fake_cert, q), daemon=True)  # noqa: E501
    server_process.start()

    https_url = oauth2_user_handler.get_authorization_url()
    webbrowser.open(https_url)

    print("If your web browser complains about security risk, accept the risk and continue.")  # noqa: E501
    auth_response = q.get()
    access_token = oauth2_user_handler.fetch_token(auth_response.decode("utf-8"))  # noqa: E501

    server_process.terminate()

    return tweepy.Client(access_token["access_token"], wait_on_rate_limit=True)


def credential_prompt(username):
    print("If you have a Developer Account, go to Projects & Apps.")
    print("You will need to enable OAuth 2.0 under your project settings (click the gear).")  # noqa: E501
    print("Use https://127.0.0.1:8000/ for Redirect URL")
    print("Use your Twitter account for Website")
    webbrowser.open("https://developer.twitter.com/en/apply-for-access")

    client_id = input("Client ID: ")
    client_secret = input("Client Secret: ")

    creds = {
        username: {
            "client_id": client_id,
            "client_secret": client_secret
        }
    }

    return creds
