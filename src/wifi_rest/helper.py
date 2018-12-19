import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from db_models import *


connstr_engine_map = {}


def get_sql_engine_by_connstr(conn_str):
    engine = connstr_engine_map.get(conn_str, None)
    if engine is None:
        logging.debug(' *** create engine ***')
        # NOTE: monetdb dialect does not support setting 'max_overflow'
        engine = create_engine(conn_str, echo=False, pool_size=2)
        connstr_engine_map[conn_str] = engine
    return engine


class ConnStrDBSession(object):
    def __init__(self, connstr):
        self.connstr = connstr

    def __enter__(self):
        self.engine = get_sql_engine_by_connstr(self.connstr)
        self._session_factory = scoped_session(sessionmaker(bind=self.engine, autoflush=False))
        self._session = self._session_factory()
        return self._session

    def __exit__(self, *exc):
        self._session.close()
        self._session_factory.remove()
        return False

# if __name__ == "__main__":
#     with ConnStrDBSession("mysql+pymysql://jame:khvdqt@127.0.0.1:3306/emqtt") as session:
#         res = session.execute("select * from mqtt_acl where username = 'jame'")
#         for info in res:
#             acl_obj = Acl(username=info.username,
#                             topic=info.topic,
#                             access= info.access)
# 
#             print (acl_obj)
#             acl_obj.username = 'lemon'
# 
#             #adding:
#             session.add(acl_obj)
#             session.commit()
