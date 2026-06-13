"""init all tables

Revision ID: 4139444aeb74
Revises:
Create Date: 2026-06-01 18:46:22.579071

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4139444aeb74'
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('USER', 'GENEALOGIST', 'ADMIN', name='user_role', native_enum=False), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'BLOCKED', 'PENDING_VERIFICATION', name='user_status', native_enum=False), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('middle_name', sa.String(length=100), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('birth_place', sa.String(length=255), nullable=True),
    sa.Column('region', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table('archive_request_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('storage_path', sa.String(length=500), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by_user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'version', name='uq_archive_request_templates_name_version')
    )

    op.create_table('documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('uploaded_by_user_id', sa.UUID(), nullable=True),
    sa.Column('document_kind', sa.Enum('ARCHIVE_SCAN', 'REQUEST_DRAFT', 'REQUEST_FINAL', 'BOOK_RESULT', 'ATTACHMENT', name='document_kind', native_enum=False), nullable=False),
    sa.Column('source_type', sa.Enum('USER_UPLOAD', 'GENEALOGIST_UPLOAD', 'SYSTEM_GENERATED', 'ARCHIVE_RECEIVED', name='document_source_type', native_enum=False), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
    sa.Column('storage_path', sa.String(length=500), nullable=False),
    sa.Column('checksum_sha256', sa.String(length=64), nullable=True),
    sa.Column('original_created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_document_kind'), 'documents', ['document_kind'], unique=False)
    op.create_index(op.f('ix_documents_uploaded_by_user_id'), 'documents', ['uploaded_by_user_id'], unique=False)

    op.create_table('notification_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('notification_type', sa.Enum('REQUEST_STATUS_CHANGED', 'REQUEST_NEEDS_CLARIFICATION', 'DOCUMENT_UPLOADED', 'BOOK_READY', 'SYSTEM', name='notification_type', native_enum=False), nullable=False),
    sa.Column('channel', sa.String(length=50), nullable=False),
    sa.Column('subject_template', sa.String(length=255), nullable=True),
    sa.Column('body_template', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by_user_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('notification_type', 'channel', name='uq_notification_templates_type_channel')
    )

    op.create_table('profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED', name='profile_status', native_enum=False), nullable=False),
    sa.Column('started_at', sa.Date(), nullable=True),
    sa.Column('completed_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profiles_owner_user_id'), 'profiles', ['owner_user_id'], unique=False)
    op.create_index(op.f('ix_profiles_status'), 'profiles', ['status'], unique=False)

    op.create_table('archive_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('created_by_user_id', sa.UUID(), nullable=False),
    sa.Column('assigned_genealogist_user_id', sa.UUID(), nullable=True),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('request_goal', sa.Text(), nullable=True),
    sa.Column('current_status', sa.Enum('DRAFT', 'PREPARED', 'SENT', 'IN_PROGRESS', 'RESPONSE_RECEIVED', 'COMPLETED', 'CANCELLED', name='archive_request_status', native_enum=False), nullable=False),
    sa.Column('requested_archive_name', sa.String(length=255), nullable=True),
    sa.Column('outgoing_number', sa.String(length=100), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_genealogist_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['template_id'], ['archive_request_templates.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_archive_requests_assigned_genealogist_user_id'), 'archive_requests', ['assigned_genealogist_user_id'], unique=False)
    op.create_index(op.f('ix_archive_requests_created_by_user_id'), 'archive_requests', ['created_by_user_id'], unique=False)
    op.create_index(op.f('ix_archive_requests_current_status'), 'archive_requests', ['current_status'], unique=False)
    op.create_index(op.f('ix_archive_requests_profile_id'), 'archive_requests', ['profile_id'], unique=False)

    op.create_table('generated_books',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('requested_by_user_id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'SUCCEEDED', 'FAILED', name='book_status', native_enum=False), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['requested_by_user_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_books_profile_id'), 'generated_books', ['profile_id'], unique=False)

    op.create_table('persons',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('last_name', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=255), nullable=False),
    sa.Column('middle_name', sa.String(length=255), nullable=True),
    sa.Column('sex', sa.Enum('MALE', 'FEMALE', 'UNKNOWN', name='person_sex', native_enum=False), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('death_date', sa.Date(), nullable=True),
    sa.Column('birth_place', sa.String(length=255), nullable=True),
    sa.Column('death_place', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_living', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('profile_persons',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('person_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_id', 'person_id', name='uq_profile_persons')
    )
    op.create_index(op.f('ix_profile_persons_person_id'), 'profile_persons', ['person_id'], unique=False)
    op.create_index(op.f('ix_profile_persons_profile_id'), 'profile_persons', ['profile_id'], unique=False)

    op.create_table('archive_request_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('archive_request_id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('relation_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['archive_request_id'], ['archive_requests.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('archive_request_id', 'document_id', 'relation_type', name='uq_archive_request_documents_unique')
    )
    op.create_index(op.f('ix_archive_request_documents_archive_request_id'), 'archive_request_documents', ['archive_request_id'], unique=False)

    op.create_table('archive_request_status_history',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('archive_request_id', sa.UUID(), nullable=False),
    sa.Column('from_status', sa.Enum('DRAFT', 'PREPARED', 'SENT', 'IN_PROGRESS', 'RESPONSE_RECEIVED', 'COMPLETED', 'CANCELLED', name='archive_request_status', native_enum=False), nullable=True),
    sa.Column('to_status', sa.Enum('DRAFT', 'PREPARED', 'SENT', 'IN_PROGRESS', 'RESPONSE_RECEIVED', 'COMPLETED', 'CANCELLED', name='archive_request_status', native_enum=False), nullable=False),
    sa.Column('changed_by_user_id', sa.UUID(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['archive_request_id'], ['archive_requests.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_archive_request_status_history_req_created', 'archive_request_status_history', ['archive_request_id', 'created_at'], unique=False)

    op.create_table('facts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('person_id', sa.UUID(), nullable=False),
    sa.Column('fact_type', sa.Enum('BIRTH', 'DEATH', 'MARRIAGE', 'RESIDENCE', 'SERVICE', 'NOTE', name='fact_type', native_enum=False), nullable=False),
    sa.Column('fact_date', sa.Date(), nullable=True),
    sa.Column('place', sa.String(length=255), nullable=True),
    sa.Column('value_text', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('confidence', sa.Enum('UNVERIFIED', 'HYPOTHESIS', 'PROBABLE', 'CONFIRMED', name='fact_confidence', native_enum=False), nullable=False),
    sa.Column('verified_by_user_id', sa.UUID(), nullable=True),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['verified_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facts_confidence'), 'facts', ['confidence'], unique=False)
    op.create_index(op.f('ix_facts_fact_type'), 'facts', ['fact_type'], unique=False)
    op.create_index(op.f('ix_facts_person_id'), 'facts', ['person_id'], unique=False)

    op.create_table('notifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('recipient_user_id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('notification_type', sa.Enum('REQUEST_STATUS_CHANGED', 'REQUEST_NEEDS_CLARIFICATION', 'DOCUMENT_UPLOADED', 'BOOK_READY', 'SYSTEM', name='notification_type', native_enum=False), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('related_archive_request_id', sa.UUID(), nullable=True),
    sa.Column('related_document_id', sa.UUID(), nullable=True),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['related_archive_request_id'], ['archive_requests.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['related_document_id'], ['documents.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_recipient_read', 'notifications', ['recipient_user_id', 'read_at'], unique=False)
    op.create_index(op.f('ix_notifications_related_archive_request_id'), 'notifications', ['related_archive_request_id'], unique=False)

    op.create_table('person_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('person_id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('relation_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('person_id', 'document_id', 'relation_type', name='uq_person_documents_unique')
    )
    op.create_index(op.f('ix_person_documents_person_id'), 'person_documents', ['person_id'], unique=False)

    op.create_table('relationships',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('source_person_id', sa.UUID(), nullable=False),
    sa.Column('target_person_id', sa.UUID(), nullable=False),
    sa.Column('relationship_type', sa.Enum('PARENT_CHILD', 'SPOUSE', name='relationship_type', native_enum=False), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('source_person_id <> target_person_id', name='ck_relationships_no_self_ref'),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['source_person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['target_person_id'], ['persons.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_id', 'source_person_id', 'target_person_id', 'relationship_type', name='uq_relationships_unique')
    )
    op.create_index(op.f('ix_relationships_profile_id'), 'relationships', ['profile_id'], unique=False)

    op.create_table('fact_documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('fact_id', sa.UUID(), nullable=False),
    sa.Column('document_id', sa.UUID(), nullable=False),
    sa.Column('relation_type', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['fact_id'], ['facts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('fact_id', 'document_id', 'relation_type', name='uq_fact_documents_unique')
    )
    op.create_index(op.f('ix_fact_documents_fact_id'), 'fact_documents', ['fact_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_fact_documents_fact_id'), table_name='fact_documents')
    op.drop_table('fact_documents')
    op.drop_index(op.f('ix_relationships_profile_id'), table_name='relationships')
    op.drop_table('relationships')
    op.drop_index(op.f('ix_person_documents_person_id'), table_name='person_documents')
    op.drop_table('person_documents')
    op.drop_index(op.f('ix_notifications_related_archive_request_id'), table_name='notifications')
    op.drop_index('ix_notifications_recipient_read', table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_facts_person_id'), table_name='facts')
    op.drop_index(op.f('ix_facts_fact_type'), table_name='facts')
    op.drop_index(op.f('ix_facts_confidence'), table_name='facts')
    op.drop_table('facts')
    op.drop_index('ix_archive_request_status_history_req_created', table_name='archive_request_status_history')
    op.drop_table('archive_request_status_history')
    op.drop_index(op.f('ix_archive_request_documents_archive_request_id'), table_name='archive_request_documents')
    op.drop_table('archive_request_documents')
    op.drop_index(op.f('ix_profile_persons_profile_id'), table_name='profile_persons')
    op.drop_index(op.f('ix_profile_persons_person_id'), table_name='profile_persons')
    op.drop_table('profile_persons')
    op.drop_table('persons')
    op.drop_index(op.f('ix_generated_books_profile_id'), table_name='generated_books')
    op.drop_table('generated_books')
    op.drop_index(op.f('ix_archive_requests_profile_id'), table_name='archive_requests')
    op.drop_index(op.f('ix_archive_requests_current_status'), table_name='archive_requests')
    op.drop_index(op.f('ix_archive_requests_created_by_user_id'), table_name='archive_requests')
    op.drop_index(op.f('ix_archive_requests_assigned_genealogist_user_id'), table_name='archive_requests')
    op.drop_table('archive_requests')
    op.drop_index(op.f('ix_profiles_status'), table_name='profiles')
    op.drop_index(op.f('ix_profiles_owner_user_id'), table_name='profiles')
    op.drop_table('profiles')
    op.drop_table('notification_templates')
    op.drop_index(op.f('ix_documents_uploaded_by_user_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_document_kind'), table_name='documents')
    op.drop_table('documents')
    op.drop_table('archive_request_templates')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
