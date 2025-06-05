import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from main import *
with app.app_context():
    for i in User.query.all():
        if not i.verified:
            i.verified = 1
            i.email = i.username + "@PanuOJ.local"
            i.icon = "/static/usericon.png"
        db.session.add(i)
    db.session.commit()