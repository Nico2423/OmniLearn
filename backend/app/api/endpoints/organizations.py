from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.services.organization import (
    create_organization, get_organization_by_id, get_user_organizations,
    is_organization_admin, update_organization, invite_user_to_organization,
    accept_organization_invite, remove_organization_member, update_member_role
)
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationInviteCreate, OrganizationInviteResponse
)

router = APIRouter()


@router.post("/", response_model=OrganizationResponse)
def create_org(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization"""
    org = create_organization(db, org_data, current_user.id)
    return org


@router.get("/", response_model=List[OrganizationResponse])
def get_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organizations where current user is a member"""
    return get_user_organizations(db, current_user.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details"""
    org = get_organization_by_id(db, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Check if user is member
    from app.services.organization import is_organization_member
    if not is_organization_member(db, org_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_org(
    org_id: int,
    org_update: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization (admin only)"""
    org = update_organization(db, org_id, org_update, current_user.id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this organization"
        )
    return org


@router.post("/{org_id}/invites", response_model=OrganizationInviteResponse)
def invite_user(
    org_id: int,
    invite_data: OrganizationInviteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite user to organization (admin only)"""
    invite = invite_user_to_organization(db, org_id, invite_data, current_user.id)
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to invite users or user already a member"
        )
    return invite


@router.post("/invites/{token}/accept")
def accept_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept organization invite"""
    org = accept_organization_invite(db, token, current_user.id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite token"
        )
    return {"message": f"Successfully joined {org.name}"}


@router.delete("/{org_id}/members/{member_id}")
def remove_member(
    org_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove member from organization (admin only)"""
    success = remove_organization_member(db, org_id, member_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove members"
        )
    return {"message": "Member removed successfully"}


@router.put("/{org_id}/members/{member_id}/role")
def update_member_role_endpoint(
    org_id: int,
    member_id: int,
    new_role: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update member role (admin only)"""
    success = update_member_role(db, org_id, member_id, new_role, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update member roles"
        )
    return {"message": f"Member role updated to {new_role}"}