"""Association tables for many-to-many relationships."""

from datetime import datetime
from .base import db


# Association table for Issue-Label many-to-many relationship
issue_labels = db.Table(
    'issue_labels',
    db.Column('issue_id', db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), primary_key=True),
    db.Column('label_id', db.Integer, db.ForeignKey('labels.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, nullable=False, default=datetime.now)
)


class ProjectMember(db.Model):
    """Association model for Project-User many-to-many relationship with role."""
    
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
        db.Index('idx_project_members_project', 'project_id'),
        db.Index('idx_project_members_user', 'user_id'),
    )
    
    def __repr__(self):
        return f'<ProjectMember project_id={self.project_id} user_id={self.user_id} role={self.role}>'


class Assignment(db.Model):
    """Association model for Issue-User many-to-many relationship (assignees)."""
    
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('issue_id', 'user_id', name='unique_assignment'),
        db.Index('idx_assignments_issue', 'issue_id'),
        db.Index('idx_assignments_user', 'user_id'),
    )
    
    def __repr__(self):
        return f'<Assignment issue_id={self.issue_id} user_id={self.user_id}>'
