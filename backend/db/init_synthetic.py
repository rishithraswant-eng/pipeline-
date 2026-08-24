import asyncio
import aiosqlite
import json
import os
import sys
import hashlib
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

DB_PATH = os.environ.get("SQLITE_DB_PATH", "/data/phantasm.db")
if DB_PATH.startswith("/data"):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DB_PATH = os.path.join(project_root, "data", "phantasm.db")

fake = Faker('en_IN')

async def init_synthetic_data():
    print(f"Initializing synthetic data in {DB_PATH}...")
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA foreign_keys=ON;")
        
        # 1. 100 AD users
        users_added = 0
        departments = ["IT", "HR", "Finance", "Retail Banking", "Corporate Banking", "Risk Management", "Compliance", "Operations"]
        pwd_pool = ['P@ssw0rd123', 'BankName@2024', 'Admin@2024!', 'Welcome@1', 'India@2026']
        
        for i in range(100):
            is_svc = i < 5
            is_priv = i < 10
            
            if is_svc:
                sam_base = f"svc_{fake.user_name()[:10]}"
            else:
                sam_base = fake.user_name()
                
            sam = f"{sam_base}{i}"
                
            pwd = fake.random_element(elements=pwd_pool)
            ntlm = hashlib.md5(f"BOOTSTRAP{sam}PHANTASM_SYNTHETIC_SALT".encode()).hexdigest()
            dept = fake.random_element(elements=departments)
            
            try:
                await db.execute("""
                    INSERT INTO ad_synthetic_users (
                        sam_account_name, display_name, user_principal_name, distinguished_name,
                        department, employee_id, title, account_created, password_last_set, 
                        is_privileged, is_service_account, password_hash_ntlm, password_plaintext_fake, is_synthetic
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sam,
                    fake.name(),
                    f"{sam}@bankname-internal.local",
                    f"CN={sam},OU=Users,DC=bankname-internal,DC=local",
                    dept,
                    fake.numerify(text="EMP-#####"),
                    fake.job(),
                    fake.date_time_this_decade().isoformat(),
                    fake.date_time_this_year().isoformat(),
                    is_priv,
                    is_svc,
                    ntlm,
                    pwd,
                    True
                ))
                users_added += 1
            except Exception as e:
                pass
                
        # To insert db_synthetic_records, we need a fake_host to reference.
        cursor = await db.execute("""
            INSERT INTO topology_snapshots (snapshot_type, created_at, node_count, topology_json) 
            VALUES ('base', datetime('now'), 1, '{}')
        """)
        topology_pk = cursor.lastrowid
        
        cursor = await db.execute("""
            INSERT INTO fake_hosts (
                topology_snapshot_fk, hostname, ip_address, mac_address, subnet, subnet_cidr,
                host_role, declared_os, ttl_value, tcp_window_size, response_latency_baseline_ms,
                services_json, is_synthetic, created_at
            ) VALUES (?, 'FINACLE-PROD-DB', '192.168.30.11', '00:11:22:33:44:55', 'mgmt_vlan', 
            '192.168.30.0/24', 'database_server', 'Windows Server 2019', 128, 65535, 1.8, '[]', True, datetime('now'))
        """, (topology_pk,))
        host_pk = cursor.lastrowid

        # 100 customer_account DB records
        cust_added = 0
        for _ in range(100):
            record = {
                "account_no": fake.numerify(text="###########"),
                "name": fake.name(),
                "balance": str(round(fake.random.uniform(1000, 500000), 2)),
                "ifsc": "SBIN0001234",
                "pan": fake.bothify(text="?????####?")
            }
            await db.execute("""
                INSERT INTO db_synthetic_records (
                    host_fk, db_name, table_name, record_data_json, is_synthetic, created_at
                ) VALUES (?, 'FINACLE_PROD', 'customer_accounts', ?, True, datetime('now'))
            """, (host_pk, json.dumps(record)))
            cust_added += 1
            
        # 50 employee records
        emp_added = 0
        for _ in range(50):
            record = {
                "emp_id": fake.numerify(text="EMP-#####"),
                "name": fake.name(),
                "department": fake.job(),
                "salary": str(round(fake.random.uniform(30000, 150000), 2))
            }
            await db.execute("""
                INSERT INTO db_synthetic_records (
                    host_fk, db_name, table_name, record_data_json, is_synthetic, created_at
                ) VALUES (?, 'HR_SYSTEM', 'employees', ?, True, datetime('now'))
            """, (host_pk, json.dumps(record)))
            emp_added += 1

        # 200 transaction_log records
        txn_added = 0
        for _ in range(200):
            record = {
                "txn_id": fake.uuid4(),
                "account_no": fake.numerify(text="###########"),
                "amount": str(round(fake.random.uniform(10, 50000), 2)),
                "type": fake.random_element(elements=("CREDIT", "DEBIT")),
                "timestamp": fake.iso8601()
            }
            await db.execute("""
                INSERT INTO db_synthetic_records (
                    host_fk, db_name, table_name, record_data_json, is_synthetic, created_at
                ) VALUES (?, 'FINACLE_PROD', 'transaction_logs', ?, True, datetime('now'))
            """, (host_pk, json.dumps(record)))
            txn_added += 1
            
        await db.commit()
        
    print(f"Data initialized successfully.")
    print(f"Counts logged: {users_added} AD users, {cust_added + emp_added + txn_added} DB records")

if __name__ == "__main__":
    asyncio.run(init_synthetic_data())
