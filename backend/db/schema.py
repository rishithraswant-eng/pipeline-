TABLE_TOPOLOGY_SNAPSHOTS = """
CREATE TABLE IF NOT EXISTS topology_snapshots (
    snapshot_pk         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER REFERENCES sessions(session_pk),
    snapshot_type       TEXT NOT NULL,
    created_at          TEXT NOT NULL,
    trigger_reason      TEXT,
    trigger_profile_fk  INTEGER, -- FK added post-session, not enforced at creation
    node_count          INTEGER NOT NULL,
    topology_json       TEXT NOT NULL
);
"""

TABLE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    session_pk          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          TEXT NOT NULL UNIQUE,
    created_at          TEXT NOT NULL,
    ended_at            TEXT,
    duration_seconds    INTEGER,
    session_state       TEXT NOT NULL DEFAULT 'active',
    attacker_source_ip  TEXT,
    attacker_source_port INTEGER,
    entry_protocol      TEXT,
    total_commands      INTEGER DEFAULT 0,
    unique_techniques   INTEGER DEFAULT 0,
    engagement_score    REAL DEFAULT 0.0,
    dwell_baseline_s    INTEGER DEFAULT 120,
    dwell_multiplier    REAL DEFAULT 1.0,
    topology_version_id INTEGER REFERENCES topology_snapshots(snapshot_pk),
    dossier_generated   BOOLEAN DEFAULT FALSE,
    dossier_path        TEXT,
    dossier_json_path   TEXT,
    operator_human      BOOLEAN DEFAULT TRUE,
    notes               TEXT
);
"""

TABLE_FAKE_HOSTS = """
CREATE TABLE IF NOT EXISTS fake_hosts (
    host_pk             INTEGER PRIMARY KEY AUTOINCREMENT,
    topology_snapshot_fk INTEGER NOT NULL REFERENCES topology_snapshots(snapshot_pk),
    hostname            TEXT NOT NULL,
    ip_address          TEXT NOT NULL,
    mac_address         TEXT NOT NULL,
    subnet              TEXT NOT NULL,
    subnet_cidr         TEXT NOT NULL,
    host_role           TEXT NOT NULL,
    declared_os         TEXT NOT NULL,
    declared_os_version TEXT,
    ttl_value           INTEGER NOT NULL,
    tcp_window_size     INTEGER NOT NULL,
    response_latency_baseline_ms REAL NOT NULL,
    response_latency_jitter_pct REAL NOT NULL DEFAULT 0.30,
    is_crown_jewel      BOOLEAN DEFAULT FALSE,
    is_mutation_added   BOOLEAN DEFAULT FALSE,
    mutation_trigger    TEXT,
    services_json       TEXT NOT NULL,
    ad_object_json      TEXT,
    is_synthetic        BOOLEAN DEFAULT TRUE,
    created_at          TEXT NOT NULL
);
"""

TABLE_SYNTHETIC_DATA_OBJECTS = """
CREATE TABLE IF NOT EXISTS synthetic_data_objects (
    sdo_pk              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER REFERENCES sessions(session_pk),
    object_type         TEXT NOT NULL,
    generation_trigger  TEXT,
    served_to_attacker  BOOLEAN DEFAULT FALSE,
    served_at           TEXT,
    parent_host_fk      INTEGER REFERENCES fake_hosts(host_pk),
    object_schema_version INTEGER DEFAULT 1,
    object_data_json    TEXT NOT NULL,
    is_synthetic        BOOLEAN DEFAULT TRUE,
    believability_score REAL DEFAULT 0.85,
    was_queried         BOOLEAN DEFAULT FALSE,
    query_count         INTEGER DEFAULT 0,
    last_queried_at     TEXT,
    mutation_count      INTEGER DEFAULT 0,
    parent_sdo_pk       INTEGER REFERENCES synthetic_data_objects(sdo_pk),
    created_at          TEXT NOT NULL
);
"""

TABLE_AD_SYNTHETIC_USERS = """
CREATE TABLE IF NOT EXISTS ad_synthetic_users (
    user_pk             INTEGER PRIMARY KEY AUTOINCREMENT,
    sdo_fk              INTEGER REFERENCES synthetic_data_objects(sdo_pk),
    sam_account_name    TEXT NOT NULL UNIQUE,
    display_name        TEXT NOT NULL,
    user_principal_name TEXT NOT NULL,
    distinguished_name  TEXT NOT NULL,
    department          TEXT NOT NULL,
    employee_id         TEXT NOT NULL,
    title               TEXT NOT NULL,
    manager_sam         TEXT,
    account_created     TEXT NOT NULL,
    last_logon          TEXT,
    password_last_set   TEXT NOT NULL,
    is_privileged       BOOLEAN DEFAULT FALSE,
    is_service_account  BOOLEAN DEFAULT FALSE,
    password_hash_ntlm  TEXT,
    password_plaintext_fake TEXT,
    is_synthetic        BOOLEAN DEFAULT TRUE,
    groups_json         TEXT,
    was_dumped          BOOLEAN DEFAULT FALSE,
    dumped_in_session   INTEGER REFERENCES sessions(session_pk)
);
"""

TABLE_DB_SYNTHETIC_RECORDS = """
CREATE TABLE IF NOT EXISTS db_synthetic_records (
    record_pk           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER REFERENCES sessions(session_pk),
    host_fk             INTEGER NOT NULL REFERENCES fake_hosts(host_pk),
    db_name             TEXT NOT NULL,
    table_name          TEXT NOT NULL,
    record_data_json    TEXT NOT NULL,
    generation_trigger  TEXT,
    was_queried         BOOLEAN DEFAULT FALSE,
    query_sql           TEXT,
    exfil_attempted     BOOLEAN DEFAULT FALSE,
    is_synthetic        BOOLEAN DEFAULT TRUE,
    created_at          TEXT NOT NULL
);
"""

TABLE_COMMANDS = """
CREATE TABLE IF NOT EXISTS commands (
    command_pk          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    command_seq         INTEGER NOT NULL,
    received_at         TEXT NOT NULL,
    session_elapsed_ms  INTEGER NOT NULL,
    raw_command         TEXT NOT NULL,
    normalised_command  TEXT,
    command_type        TEXT,
    target_ip           TEXT,
    target_port         INTEGER,
    target_hostname     TEXT,
    ici_ms              INTEGER,
    is_first_command    BOOLEAN DEFAULT FALSE,
    is_stress_trigger   BOOLEAN DEFAULT FALSE,
    is_automation_signal BOOLEAN DEFAULT FALSE,
    protocol_layer      TEXT,
    payload_hash        TEXT
);
"""

TABLE_COMMAND_TECHNIQUES = """
CREATE TABLE IF NOT EXISTS command_techniques (
    ct_pk               INTEGER PRIMARY KEY AUTOINCREMENT,
    command_fk          INTEGER NOT NULL REFERENCES commands(command_pk),
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    technique_id        TEXT NOT NULL,
    technique_name      TEXT NOT NULL,
    tactic              TEXT NOT NULL,
    confidence          REAL NOT NULL,
    is_primary          BOOLEAN DEFAULT TRUE,
    first_occurrence    BOOLEAN DEFAULT FALSE,
    classified_at       TEXT NOT NULL
);
"""

TABLE_OPERATOR_PROFILES = """
CREATE TABLE IF NOT EXISTS operator_profiles (
    profile_pk          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    snapshot_at         TEXT NOT NULL,
    session_elapsed_s   INTEGER NOT NULL,
    command_count_at_snapshot INTEGER NOT NULL,
    expertise_level     TEXT NOT NULL,
    expertise_confidence REAL NOT NULL,
    primary_objective   TEXT NOT NULL,
    objective_confidence REAL NOT NULL,
    objective_scores_json TEXT,
    operational_state   TEXT NOT NULL,
    state_onset_s       INTEGER,
    top_apt_group       TEXT,
    top_apt_score       REAL,
    attribution_json    TEXT,
    tool_signatures_json TEXT,
    avg_ici_ms          REAL,
    min_ici_ms          INTEGER,
    max_ici_ms          INTEGER,
    stress_events_count INTEGER DEFAULT 0,
    engagement_score_at_snapshot REAL
);
"""

TABLE_HOST_INTERACTIONS = """
CREATE TABLE IF NOT EXISTS host_interactions (
    interaction_pk      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    host_fk             INTEGER NOT NULL REFERENCES fake_hosts(host_pk),
    first_interaction_at TEXT NOT NULL,
    last_interaction_at  TEXT,
    interaction_type    TEXT NOT NULL,
    access_level        TEXT NOT NULL DEFAULT 'none',
    interaction_depth   TEXT NOT NULL DEFAULT 'shallow',
    commands_on_host    INTEGER DEFAULT 0,
    credential_used     TEXT,
    credential_is_synthetic BOOLEAN DEFAULT TRUE,
    data_access_attempted BOOLEAN DEFAULT FALSE,
    data_exfil_attempted  BOOLEAN DEFAULT FALSE,
    node_status_at_end  TEXT
);
"""

TABLE_IOCS = """
CREATE TABLE IF NOT EXISTS iocs (
    ioc_pk              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    command_fk          INTEGER REFERENCES commands(command_pk),
    observed_at         TEXT NOT NULL,
    ioc_type            TEXT NOT NULL,
    ioc_value           TEXT NOT NULL,
    ioc_port            INTEGER,
    ioc_protocol        TEXT,
    context_command     TEXT,
    is_synthetic        BOOLEAN NOT NULL DEFAULT FALSE,
    confidence          REAL DEFAULT 1.0,
    tlp_classification  TEXT DEFAULT 'TLP:AMBER',
    shared_with_cert    BOOLEAN DEFAULT FALSE
);
"""

TABLE_TOPOLOGY_MUTATIONS = """
CREATE TABLE IF NOT EXISTS topology_mutations (
    mutation_pk         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    triggered_at        TEXT NOT NULL,
    trigger_condition   TEXT NOT NULL,
    trigger_profile_snapshot_fk INTEGER REFERENCES operator_profiles(profile_pk),
    mutation_type       TEXT NOT NULL,
    nodes_added_json    TEXT NOT NULL,
    pre_mutation_node_count INTEGER NOT NULL,
    post_mutation_node_count INTEGER NOT NULL,
    mutation_latency_ms INTEGER,
    dashboard_notified  BOOLEAN DEFAULT FALSE,
    rate_limit_applied  BOOLEAN DEFAULT FALSE
);
"""

TABLE_STRESS_TIMELINE = """
CREATE TABLE IF NOT EXISTS stress_timeline (
    stress_pk           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    command_fk          INTEGER NOT NULL REFERENCES commands(command_pk),
    recorded_at         TEXT NOT NULL,
    session_elapsed_s   INTEGER NOT NULL,
    ici_ms              INTEGER NOT NULL,
    ici_moving_avg_ms   REAL,
    stress_state        TEXT NOT NULL DEFAULT 'normal',
    stress_annotation   TEXT
);
"""

TABLE_DOSSIERS = """
CREATE TABLE IF NOT EXISTS dossiers (
    dossier_pk          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    generated_at        TEXT NOT NULL,
    generation_duration_s REAL,
    generation_method   TEXT NOT NULL DEFAULT 'llm_api',
    session_id_ref      TEXT NOT NULL,
    dossier_full_json   TEXT NOT NULL,
    narrative_text      TEXT,
    pdf_path            TEXT,
    cert_in_mis_json    TEXT,
    top_technique_id    TEXT,
    top_apt_attribution TEXT,
    apt_confidence      REAL,
    ioc_count           INTEGER DEFAULT 0,
    tlp_classification  TEXT DEFAULT 'TLP:AMBER',
    submitted_to_cert   BOOLEAN DEFAULT FALSE,
    submission_timestamp TEXT
);
"""

TABLE_OPERATOR_FINGERPRINTS = """
CREATE TABLE IF NOT EXISTS operator_fingerprints (
    fingerprint_pk      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_fk          INTEGER NOT NULL REFERENCES sessions(session_pk),
    computed_at         TEXT NOT NULL,
    fingerprint_vector  TEXT NOT NULL,
    fingerprint_version TEXT NOT NULL,
    similarity_matches_json TEXT
);
"""

# Ordered as requested by the user
ORDERED_TABLES = [
    TABLE_TOPOLOGY_SNAPSHOTS,
    TABLE_SESSIONS,
    TABLE_FAKE_HOSTS,
    TABLE_SYNTHETIC_DATA_OBJECTS,
    TABLE_AD_SYNTHETIC_USERS,
    TABLE_DB_SYNTHETIC_RECORDS,
    TABLE_COMMANDS,
    TABLE_COMMAND_TECHNIQUES,
    TABLE_OPERATOR_PROFILES,
    TABLE_HOST_INTERACTIONS,
    TABLE_IOCS,
    TABLE_TOPOLOGY_MUTATIONS,
    TABLE_STRESS_TIMELINE,
    TABLE_DOSSIERS,
    TABLE_OPERATOR_FINGERPRINTS
]
