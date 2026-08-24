async def get_health_status(db):
    try:
        cursor = await db.execute("SELECT 1")
        await cursor.fetchone()
        return "ok"
    except Exception:
        return "error"
