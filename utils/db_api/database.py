import aiomysql
from data.config import SERVER, DBUSERNAME_FRONT, DBPASSWORD_FRONT, DATABASE


async def db_create_pool():
    return await aiomysql.create_pool(
        host=SERVER,
        user=DBUSERNAME_FRONT,
        password=DBPASSWORD_FRONT,
        db=DATABASE)
