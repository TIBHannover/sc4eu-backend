"""Remove not_accept consensus type

Revision ID: b1a2c3d4e5f6
Revises: d7ef128d53ec
Create Date: 2026-09-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = 'd7ef128d53ec'
branch_labels = None
depends_on = None


def upgrade():
    # Any existing votes/decisions relying on the removed values are
    # reconciled before the enum types are recreated without them.
    # NOTE: sqlalchemy.Enum stores the Python enum *member name* (uppercase),
    # not the member .value, so the labels below must match the DB, e.g.
    # 'NOT_ACCEPT'/'REJECT', not 'not accept'/'reject'.
    op.execute("UPDATE sc3_vote_model SET status = 'CLOSED' WHERE status = 'NOT_ACCEPT'")
    op.execute("UPDATE sc3_vote_model SET type = 'ACCEPT' WHERE type = 'REJECT'")

    # Postgres does not support dropping enum values directly, so the enum
    # types are recreated without the removed values. 'DRAFT' is kept in
    # votestatus even though it is unused by the current model, to avoid
    # unrelated schema drift (it was added out-of-band in a prior migration).
    op.execute("ALTER TYPE votestatus RENAME TO votestatus_old")
    op.execute(
        "CREATE TYPE votestatus AS ENUM "
        "('UNDER_AGREEMENT', 'UNDER_REVISION', 'ACCEPT', 'CLOSED', 'DRAFT')"
    )
    op.execute(
        "ALTER TABLE sc3_vote_model ALTER COLUMN status TYPE votestatus "
        "USING status::text::votestatus"
    )
    op.execute("DROP TYPE votestatus_old")

    op.execute("ALTER TYPE votetype RENAME TO votetype_old")
    op.execute("CREATE TYPE votetype AS ENUM ('ACCEPT')")
    op.execute(
        "ALTER TABLE sc3_vote_model ALTER COLUMN type TYPE votetype "
        "USING type::text::votetype"
    )
    op.execute("DROP TYPE votetype_old")


def downgrade():
    op.execute("ALTER TYPE votetype RENAME TO votetype_old")
    op.execute("CREATE TYPE votetype AS ENUM ('ACCEPT', 'REJECT')")
    op.execute(
        "ALTER TABLE sc3_vote_model ALTER COLUMN type TYPE votetype "
        "USING type::text::votetype"
    )
    op.execute("DROP TYPE votetype_old")

    op.execute("ALTER TYPE votestatus RENAME TO votestatus_old")
    op.execute(
        "CREATE TYPE votestatus AS ENUM "
        "('UNDER_AGREEMENT', 'UNDER_REVISION', 'ACCEPT', 'NOT_ACCEPT', 'CLOSED', 'DRAFT')"
    )
    op.execute(
        "ALTER TABLE sc3_vote_model ALTER COLUMN status TYPE votestatus "
        "USING status::text::votestatus"
    )
    op.execute("DROP TYPE votestatus_old")
