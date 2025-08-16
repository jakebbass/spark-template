import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres:postgres@db:5432/fantasy')
    print('DB Connection Successful')
    await conn.close()

asyncio.run(main())
