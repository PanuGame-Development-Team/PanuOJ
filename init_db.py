from main import *
from uuid import uuid4
with app.app_context():
    db.create_all()
    Session.query.delete()
    if User.query.count() == 0:
        SYSTEM = User()
        SYSTEM.username = "SYSTEM"
        SYSTEM.access = 7
    else:
        SYSTEM = User.query.get(1)
    password = uuid4().hex.upper()
    print("SYSTEM password resetted:",password)
    SYSTEM.password = generate_password_hash(password)
    SYSTEM.access = 7
    db.session.add(SYSTEM)
    db.session.commit()