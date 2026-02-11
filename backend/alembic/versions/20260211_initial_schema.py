"""Initial schema with all models

Revision ID: 001_initial
Revises:
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=False),
    sa.Column('user_type', sa.Enum('STUDENT', 'PARENT', name='usertype'), nullable=False),
    sa.Column('is_active', sa.String(length=1), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)

    # Create students table
    op.create_table('students',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('grade', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )

    # Create parents table
    op.create_table('parents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )

    # Create parent_student_links table
    op.create_table('parent_student_links',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('parent_id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('relationship_type', sa.Enum('MOTHER', 'FATHER', 'GUARDIAN', name='relationshiptype'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

    # Create subjects table
    op.create_table('subjects',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('grade', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subjects_grade'), 'subjects', ['grade'], unique=False)

    # Create topics table
    op.create_table('topics',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('subject_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_subject_id'), 'topics', ['subject_id'], unique=False)

    # Create learning_sessions table
    op.create_table('learning_sessions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_sessions_student_id'), 'learning_sessions', ['student_id'], unique=False)

    # Create worksheets table
    op.create_table('worksheets',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('questions', sa.JSON(), nullable=False),
    sa.Column('difficulty_level', sa.Enum('EASY', 'MEDIUM', 'HARD', name='difficultylevel'), nullable=True),
    sa.Column('total_points', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_worksheets_student_id'), 'worksheets', ['student_id'], unique=False)

    # Create worksheet_submissions table
    op.create_table('worksheet_submissions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('worksheet_id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('answers', sa.JSON(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('max_score', sa.Integer(), nullable=True),
    sa.Column('feedback', sa.JSON(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('graded_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['worksheet_id'], ['worksheets.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_worksheet_submissions_student_id'), 'worksheet_submissions', ['student_id'], unique=False)

    # Create quizzes table
    op.create_table('quizzes',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('questions', sa.JSON(), nullable=False),
    sa.Column('total_points', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quizzes_topic_id'), 'quizzes', ['topic_id'], unique=False)

    # Create quiz_attempts table
    op.create_table('quiz_attempts',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('quiz_id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('answers', sa.JSON(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('max_score', sa.Integer(), nullable=True),
    sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_attempts_student_id'), 'quiz_attempts', ['student_id'], unique=False)

    # Create conversations table
    op.create_table('conversations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_student_id'), 'conversations', ['student_id'], unique=False)

    # Create messages table
    op.create_table('messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.Enum('USER', 'ASSISTANT', name='messagerole'), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sources', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    # Create progress_records table
    op.create_table('progress_records',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('mastery_level', sa.Float(), nullable=True),
    sa.Column('total_time_spent_seconds', sa.Integer(), nullable=True),
    sa.Column('quiz_count', sa.Integer(), nullable=True),
    sa.Column('worksheet_count', sa.Integer(), nullable=True),
    sa.Column('average_quiz_score', sa.Float(), nullable=True),
    sa.Column('average_worksheet_score', sa.Float(), nullable=True),
    sa.Column('last_practiced_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progress_records_student_id'), 'progress_records', ['student_id'], unique=False)
    op.create_index(op.f('ix_progress_records_topic_id'), 'progress_records', ['topic_id'], unique=False)

    # Create weak_areas table
    op.create_table('weak_areas',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('student_id', sa.String(length=36), nullable=False),
    sa.Column('topic_id', sa.String(length=36), nullable=False),
    sa.Column('mastery_level', sa.Float(), nullable=True),
    sa.Column('identified_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weak_areas_student_id'), 'weak_areas', ['student_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_weak_areas_student_id'), table_name='weak_areas')
    op.drop_table('weak_areas')

    op.drop_index(op.f('ix_progress_records_topic_id'), table_name='progress_records')
    op.drop_index(op.f('ix_progress_records_student_id'), table_name='progress_records')
    op.drop_table('progress_records')

    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_table('messages')

    op.drop_index(op.f('ix_conversations_student_id'), table_name='conversations')
    op.drop_table('conversations')

    op.drop_index(op.f('ix_quiz_attempts_student_id'), table_name='quiz_attempts')
    op.drop_table('quiz_attempts')

    op.drop_index(op.f('ix_quizzes_topic_id'), table_name='quizzes')
    op.drop_table('quizzes')

    op.drop_index(op.f('ix_worksheet_submissions_student_id'), table_name='worksheet_submissions')
    op.drop_table('worksheet_submissions')

    op.drop_index(op.f('ix_worksheets_student_id'), table_name='worksheets')
    op.drop_table('worksheets')

    op.drop_index(op.f('ix_learning_sessions_student_id'), table_name='learning_sessions')
    op.drop_table('learning_sessions')

    op.drop_index(op.f('ix_topics_subject_id'), table_name='topics')
    op.drop_table('topics')

    op.drop_index(op.f('ix_subjects_grade'), table_name='subjects')
    op.drop_table('subjects')

    op.drop_table('parent_student_links')
    op.drop_table('parents')
    op.drop_table('students')

    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS messagerole')
    op.execute('DROP TYPE IF EXISTS difficultylevel')
    op.execute('DROP TYPE IF EXISTS relationshiptype')
    op.execute('DROP TYPE IF EXISTS usertype')
