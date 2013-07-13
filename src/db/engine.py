from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import settings

engine = create_engine('mysql://%s:%s@%s/%s' % (settings.MYSQL_USER,
												settings.MYSQL_PASSWORD,
												settings.MYSQL_HOST,
												settings.MYSQL_DATABASE))
Base = declarative_base()

#Base.metadata.create_all(engine) 