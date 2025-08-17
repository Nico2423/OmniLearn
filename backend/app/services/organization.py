from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.organization import Organization, OrganizationInvite, organization_members
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationInviteCreate
from app.services.auth import create_organization_invite


def create_organization(db: Session, org_data: OrganizationCreate, creator_id: int) -> Organization:
    """Create a new organization with creator as admin"""
    org = Organization(
        name=org_data.name,
        description=org_data.description
    )
    db.add(org)
    db.flush()  # Get the ID without committing
    
    # Add creator as admin
    db.execute(
        organization_members.insert().values(
            organization_id=org.id,
            user_id=creator_id,
            role='admin'
        )
    )
    
    db.commit()
    db.refresh(org)
    return org


def get_organization_by_id(db: Session, org_id: int) -> Optional[Organization]:
    """Get organization by ID"""
    return db.query(Organization).filter(
        Organization.id == org_id,
        Organization.is_active == True
    ).first()


def get_user_organizations(db: Session, user_id: int) -> List[Organization]:
    """Get organizations where user is a member"""
    return db.query(Organization).join(
        organization_members,
        Organization.id == organization_members.c.organization_id
    ).filter(
        and_(
            organization_members.c.user_id == user_id,
            Organization.is_active == True
        )
    ).all()


def is_organization_admin(db: Session, org_id: int, user_id: int) -> bool:
    """Check if user is admin of organization"""
    result = db.query(organization_members).filter(
        and_(
            organization_members.c.organization_id == org_id,
            organization_members.c.user_id == user_id,
            organization_members.c.role == 'admin'
        )
    ).first()
    return result is not None


def is_organization_member(db: Session, org_id: int, user_id: int) -> bool:
    """Check if user is member of organization"""
    result = db.query(organization_members).filter(
        and_(
            organization_members.c.organization_id == org_id,
            organization_members.c.user_id == user_id
        )
    ).first()
    return result is not None


def update_organization(
    db: Session, 
    org_id: int, 
    org_update: OrganizationUpdate, 
    user_id: int
) -> Optional[Organization]:
    """Update organization (admin only)"""
    if not is_organization_admin(db, org_id, user_id):
        return None
    
    org = get_organization_by_id(db, org_id)
    if not org:
        return None
    
    update_data = org_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    db.commit()
    db.refresh(org)
    return org


def invite_user_to_organization(
    db: Session,
    org_id: int,
    invite_data: OrganizationInviteCreate,
    inviter_id: int
) -> Optional[OrganizationInvite]:
    """Invite user to organization (admin only)"""
    if not is_organization_admin(db, org_id, inviter_id):
        return None
    
    # Check if user is already a member
    existing_user = db.query(User).filter(User.email == invite_data.email).first()
    if existing_user and is_organization_member(db, org_id, existing_user.id):
        return None  # Already a member
    
    # Check for existing pending invite
    existing_invite = db.query(OrganizationInvite).filter(
        and_(
            OrganizationInvite.organization_id == org_id,
            OrganizationInvite.email == invite_data.email,
            OrganizationInvite.accepted_at.is_(None)
        )
    ).first()
    
    if existing_invite:
        return existing_invite  # Return existing invite
    
    return create_organization_invite(
        db, org_id, invite_data.email, invite_data.role, inviter_id
    )


def accept_organization_invite(db: Session, token: str, user_id: int) -> Optional[Organization]:
    """Accept organization invite"""
    from app.services.auth import get_invite_by_token
    from datetime import datetime
    
    invite = get_invite_by_token(db, token)
    if not invite:
        return None
    
    # Verify user email matches invite
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.email != invite.email:
        return None
    
    # Add user to organization
    db.execute(
        organization_members.insert().values(
            organization_id=invite.organization_id,
            user_id=user_id,
            role=invite.role
        )
    )
    
    # Mark invite as accepted
    invite.accepted_at = datetime.utcnow()
    
    db.commit()
    
    return get_organization_by_id(db, invite.organization_id)


def remove_organization_member(
    db: Session, 
    org_id: int, 
    member_id: int, 
    admin_id: int
) -> bool:
    """Remove member from organization (admin only)"""
    if not is_organization_admin(db, org_id, admin_id):
        return False
    
    # Can't remove yourself if you're the only admin
    admin_count = db.query(organization_members).filter(
        and_(
            organization_members.c.organization_id == org_id,
            organization_members.c.role == 'admin'
        )
    ).count()
    
    if admin_count == 1 and member_id == admin_id:
        return False
    
    # Remove member
    db.execute(
        organization_members.delete().where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == member_id
            )
        )
    )
    
    db.commit()
    return True


def update_member_role(
    db: Session, 
    org_id: int, 
    member_id: int, 
    new_role: str, 
    admin_id: int
) -> bool:
    """Update member role (admin only)"""
    if not is_organization_admin(db, org_id, admin_id):
        return False
    
    if new_role not in ['admin', 'member']:
        return False
    
    # Can't demote yourself if you're the only admin
    if member_id == admin_id and new_role == 'member':
        admin_count = db.query(organization_members).filter(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.role == 'admin'
            )
        ).count()
        
        if admin_count == 1:
            return False
    
    # Update role
    db.execute(
        organization_members.update().where(
            and_(
                organization_members.c.organization_id == org_id,
                organization_members.c.user_id == member_id
            )
        ).values(role=new_role)
    )
    
    db.commit()
    return True