import sys
from datetime import datetime
from .app import db, app
from .model import Paste


def cleaner(args):
    count = Paste.purge()
    app.logger.debug("Purged %d expired pastes" % count)
    sys.exit(0)
