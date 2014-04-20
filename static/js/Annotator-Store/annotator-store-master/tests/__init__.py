import os
from flask import Flask, g, request

from annotator import es, auth, authz, annotation, store, document

from .helpers import MockUser, MockConsumer

here = os.path.dirname(__file__)


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join(here, 'test.cfg'))

    # Travis provides elasticsearch 0.90.x
    if os.environ.get('TRAVIS') == 'true':
        app.config['ELASTICSEARCH_COMPATIBILITY_MODE'] = 'pre-1.0.0'

    es.init_app(app)

    @app.before_request
    def before_request():
        g.auth = auth.Authenticator(MockConsumer)
        g.authorize = authz.authorize

    app.register_blueprint(store.store, url_prefix='/api')

    return app


class TestCase(object):
    @classmethod
    def setup_class(cls):
        cls.app = create_app()
        with cls.app.app_context():
            annotation.Annotation.drop_all()
            document.Document.drop_all()

    def setup(self):
        with self.app.app_context():
            annotation.Annotation.create_all()
            document.Document.create_all()
            es.conn.cluster.health(wait_for_status='yellow')
        self.cli = self.app.test_client()

    def teardown(self):
        with self.app.app_context():
            annotation.Annotation.drop_all()
            document.Document.drop_all()