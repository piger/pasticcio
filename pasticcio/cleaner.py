import sys
from datetime import datetime
from .app import db, app
from .model import Paste


def cleaner(args):
    now = datetime.utcnow()
    query = Paste.query.filter(Paste.expire_on < now)
    count = query.count()
    query.delete()
    db.session.commit()
    app.logger.debug("Purged %d expired pastes" % count)
    sys.exit(0)
