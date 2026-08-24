import os
import ipaddress
import random
from typing import Dict, List, Any

class TopologyGenerator:
    def __init__(self):
        self.subnets = [
            os.environ.get("SHADOWMESH_SUBNET_1", "192.168.10.0/24"),
            os.environ.get("SHADOWMESH_SUBNET_2", "192.168.20.0/24"),
            os.environ.get("SHADOWMESH_SUBNET_3", "192.168.30.0/24"),
        ]
        self.topology = {
            "nodes": [],
            "edges": [],
            "subnets": self.subnets
        }
        self._generate()

    def _generate(self):
        random.seed(hash(os.environ.get("PHANTASM_DOMAIN", "bankname-internal.local")))
        roles = [
            {"name": "Web Server", "services": {"http": 80, "ssh": 22}, "prefix": "web-srv"},
            {"name": "Database Server", "services": {"mysql": 3306, "ssh": 22}, "prefix": "db-srv"},
            {"name": "Domain Controller", "services": {"smb": 445, "ldap": 389, "ssh": 22}, "prefix": "dc-srv"},
            {"name": "File Server", "services": {"smb": 445, "ssh": 22}, "prefix": "fs-srv"},
            {"name": "MSSQL Database", "services": {"mssql": 1433, "ssh": 22}, "prefix": "mssql-srv"}
        ]
        
        locations = ["ny", "ldn", "tok", "sfo"]
        
        node_id = 1
        for i, subnet_str in enumerate(self.subnets):
            try:
                network = ipaddress.ip_network(subnet_str, strict=False)
            except ValueError:
                continue
            
            num_hosts = random.randint(5, 7)
            ips = [str(ip) for ip in list(network.hosts())[10:10+num_hosts]]
            
            for ip in ips:
                role = random.choice(roles)
                loc = random.choice(locations)
                hostname = f"{loc}-core-{role['prefix']}-{node_id:02d}"
                
                self.topology["nodes"].append({
                    "id": f"node_{node_id}",
                    "ip": ip,
                    "hostname": hostname,
                    "role": role["name"],
                    "subnet": subnet_str,
                    "services": role["services"]
                })
                node_id += 1

        nodes = self.topology["nodes"]
        for i, node in enumerate(nodes):
            if i > 0:
                target = random.choice(nodes[:i])
                self.topology["edges"].append({
                    "source": node["id"],
                    "target": target["id"]
                })

    def get_topology(self) -> Dict[str, Any]:
        return self.topology
