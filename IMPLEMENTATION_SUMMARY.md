# Course Persistence and Multi-User System Implementation

## Overview
This implementation adds comprehensive course persistence and multi-user functionality to OmniLearn, including organization support and Google OAuth authentication.

## New Features Implemented

### 1. Course Management
- **Course Creation**: Users can create persistent courses with titles, descriptions, and topics
- **Course Visibility**: Three levels - Private (creator only), Organization (team members), Public (future)
- **Course Enrollment**: Users can enroll in accessible courses
- **Progress Tracking**: Detailed progress tracking per user per course

### 2. Multi-User Authentication
- **Email/Password**: Traditional authentication with hashed passwords
- **Google OAuth**: Single sign-on with Google accounts
- **JWT Tokens**: Secure token-based authentication
- **User Profiles**: Support for avatars and user metadata

### 3. Organization System
- **Organization Creation**: Users can create organizations for team learning
- **Role-Based Access**: Admin and Member roles with different permissions
- **Invitation System**: Secure token-based invitations with expiration
- **Member Management**: Add, remove, and update member roles

### 4. Enhanced Database Schema
- **Users Table**: Extended with OAuth fields and activity tracking
- **Organizations Table**: Organization metadata and member relationships
- **Courses Table**: Course information with ownership and visibility
- **Enrollments Table**: User-course relationships with progress tracking
- **Progress Records**: Detailed subsection-level progress tracking

## Database Models

### Core Models
- `User`: Enhanced with OAuth support and organization relationships
- `Organization`: Team management with member associations
- `Course`: Persistent courses with visibility controls
- `CourseEnrollment`: User enrollment tracking
- `UserProgressRecord`: Detailed progress tracking
- `OrganizationInvite`: Secure invitation system

### Relationships
- Users ↔ Organizations (many-to-many with roles)
- Users → Courses (one-to-many for created courses)
- Users ↔ Courses (many-to-many through enrollments)
- Courses → KnowledgeTree (one-to-one)
- Organizations → Courses (one-to-many for org courses)

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Email/password registration
- `POST /login` - Email/password login
- `POST /google` - Google OAuth authentication
- `GET /me` - Get current user info

### Organizations (`/api/v1/organizations`)
- `POST /` - Create organization
- `GET /` - Get user's organizations
- `GET /{id}` - Get organization details
- `PUT /{id}` - Update organization (admin only)
- `POST /{id}/invites` - Invite user (admin only)
- `POST /invites/{token}/accept` - Accept invitation
- `DELETE /{id}/members/{user_id}` - Remove member (admin only)
- `PUT /{id}/members/{user_id}/role` - Update member role (admin only)

### Courses (`/api/v1/courses`)
- `POST /` - Create course
- `GET /` - Get accessible courses
- `GET /{id}` - Get course details
- `PUT /{id}` - Update course (creator/admin only)
- `POST /{id}/enroll` - Enroll in course
- `GET /{id}/enrollment` - Get enrollment details
- `POST /{id}/progress` - Update progress
- `GET /{id}/progress` - Get progress records

## Access Control

### Course Access Rules
1. **Private Courses**: Only creator can access
2. **Organization Courses**: All organization members can access
3. **Public Courses**: Anyone can access (future feature)

### Organization Permissions
- **Admin**: Can invite users, manage members, create org courses, update org settings
- **Member**: Can access org courses, view org details

### Course Modification Rules
- **Creator**: Can always modify their courses
- **Organization Admin**: Can modify organization courses
- **Members**: Read-only access to org courses

## Security Features
- Password hashing with bcrypt
- JWT token authentication
- Secure invitation tokens with expiration
- Role-based access control
- OAuth integration with Google

## Environment Variables
New environment variables added:
- `SECRET_KEY`: JWT signing key
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

## Database Migration
- Alembic configuration added for database migrations
- All new models integrated with existing schema
- Backward compatibility maintained

## Next Steps
1. Generate and run initial database migration
2. Update frontend to use new authentication system
3. Implement organization management UI
4. Add course creation and enrollment interfaces
5. Build progress tracking dashboard
6. Add email notifications for invitations
7. Implement course content curation features

## Testing Recommendations
1. Test authentication flows (email/password and Google OAuth)
2. Test organization creation and member management
3. Test course creation with different visibility levels
4. Test enrollment and progress tracking
5. Test access control for different user roles
6. Test invitation system end-to-end