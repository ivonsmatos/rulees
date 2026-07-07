"""P3 enterprise: api_keys, integration_configs, dispatches, sso, byok, marketplace

Revision ID: 20260702_0014
Revises: 20260701_0013
Create Date: 2026-07-02 00:01:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0014"
down_revision: str | None = "20260701_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── API Keys ──────────────────────────────────────────────────────────────
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False, unique=True),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=False, server_default='"read"'),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"], unique=True)

    # ── Integration Configs ───────────────────────────────────────────────────
    op.create_table(
        "integration_configs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("provider", sa.String(40), nullable=False, index=True),
        sa.Column("label", sa.String(160), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "integration_dispatches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("integration_id", sa.String(36), nullable=False, index=True),
        sa.Column("document_id", sa.String(36), nullable=False, index=True),
        sa.Column("status", sa.String(40), nullable=False, server_default="pending", index=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("external_url", sa.String(1024), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("dispatched_by", sa.String(36), nullable=False),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── SSO ───────────────────────────────────────────────────────────────────
    op.create_table(
        "sso_configs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, unique=True, index=True),
        sa.Column("provider_name", sa.String(160), nullable=False, server_default="SAML IdP"),
        sa.Column("entity_id", sa.String(1024), nullable=False),
        sa.Column("sso_url", sa.String(1024), nullable=False),
        sa.Column("slo_url", sa.String(1024), nullable=True),
        sa.Column("x509_cert", sa.Text(), nullable=False),
        sa.Column("attribute_map", sa.Text(), nullable=False, server_default='{"email":"email","name":"name"}'),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("sp_entity_id", sa.String(1024), nullable=False, server_default=""),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "sso_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("relay_state", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("redirect_url", sa.String(1024), nullable=False, server_default="/"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── BYOK ─────────────────────────────────────────────────────────────────
    op.create_table(
        "customer_keys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, unique=True, index=True),
        sa.Column("kms_provider", sa.String(40), nullable=False, server_default="local"),
        sa.Column("kms_key_arn", sa.String(1024), nullable=True),
        sa.Column("encrypted_dek", sa.Text(), nullable=False),
        sa.Column("key_label", sa.String(160), nullable=False, server_default="primary"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ── Marketplace ───────────────────────────────────────────────────────────
    op.create_table(
        "marketplace_plugins",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("category", sa.String(80), nullable=False, index=True),
        sa.Column("config_schema", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("is_official", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("version", sa.String(40), nullable=False, server_default="1.0.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "tenant_plugins",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("plugin_id", sa.String(36), nullable=False, index=True),
        sa.Column("plugin_slug", sa.String(120), nullable=False, index=True),
        sa.Column("config_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("installed_by", sa.String(36), nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Seed: plugins oficiais do marketplace
    op.execute("""
        INSERT INTO marketplace_plugins (id, slug, name, description, category,
            config_schema, is_official, version, is_active, created_at)
        VALUES
        ('mp-001', 'jira-cloud', 'Jira Cloud', 'Exporta documentos e regras para Jira Cloud',
            'integration', '{}', TRUE, '1.0.0', TRUE, CURRENT_TIMESTAMP),
        ('mp-002', 'confluence', 'Confluence', 'Publica documentos no Confluence',
            'integration', '{}', TRUE, '1.0.0', TRUE, CURRENT_TIMESTAMP),
        ('mp-003', 'azure-devops', 'Azure DevOps', 'Cria work items no Azure DevOps',
            'integration', '{}', TRUE, '1.0.0', TRUE, CURRENT_TIMESTAMP),
        ('mp-004', 'ollama-local', 'Ollama (IA Local)', 'Usa modelos locais via Ollama',
            'ai', '{"base_url": "http://localhost:11434", "model": "llama3"}', TRUE, '1.0.0', TRUE, CURRENT_TIMESTAMP),
        ('mp-005', 'webhook-generic', 'Webhook Genérico', 'Envia eventos para qualquer endpoint HTTP',
            'notification', '{"url": "", "secret": ""}', TRUE, '1.0.0', TRUE, CURRENT_TIMESTAMP)
    """)


def downgrade() -> None:
    op.drop_table("tenant_plugins")
    op.drop_table("marketplace_plugins")
    op.drop_table("customer_keys")
    op.drop_table("sso_sessions")
    op.drop_table("sso_configs")
    op.drop_table("integration_dispatches")
    op.drop_table("integration_configs")
    op.drop_index("ix_api_keys_key_prefix", table_name="api_keys")
    op.drop_table("api_keys")
