from main import *
from uuid import uuid4
with app.app_context():
    db.create_all()
    Session.query.delete()
    print("Session flushed")
    if User.query.count() == 0:
        SYSTEM = User()
        SYSTEM.username = "SYSTEM"
    else:
        SYSTEM = User.query.get(1)
    SYSTEM.verified = 1
    SYSTEM.email = "SYSTEM@PanuOJ.local"
    password = uuid4().hex.upper()
    print("SYSTEM password resetted:",password)
    SYSTEM.password = generate_password_hash(password)
    for access in ACCESS:
        SYSTEM.access |= ACCESS[access]
    db.session.add(SYSTEM)
    db.session.commit()