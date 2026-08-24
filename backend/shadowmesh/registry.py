import aiosqlite
import os

class IdentityRegistry:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.initialized = False
        self.users = []
        
    async def initialize(self):
        if not os.path.exists(self.db_path):
            raise RuntimeError("Synthetic data not initialized. Run init_synthetic.py first.")
            
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            try:
                async with db.execute("SELECT user_pk as id, sam_account_name as username, display_name, department, password_plaintext_fake, is_privileged FROM ad_synthetic_users LIMIT 100") as cursor:
                    rows = await cursor.fetchall()
                    if not rows:
                        raise RuntimeError("Synthetic data not initialized. Run init_synthetic.py first.")
                    for r in rows:
                        self.users.append(dict(r))
                self.initialized = True
            except aiosqlite.OperationalError:
                raise RuntimeError("Synthetic data not initialized. Run init_synthetic.py first.")

    def get_random_user(self):
        import random
        if not self.users:
            return None
        return random.choice(self.users)
