import models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///sqlite.db')
Session = sessionmaker(bind=engine)
models.Base.metadata.create_all(engine)
session = Session()
user = models.User(user_id=0, email='user@example.com')
session.add(user)
session.commit()
session.add(models.Session(user_id=user.id))
session.commit()
