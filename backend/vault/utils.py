from .models import AuditEvent

def log_audit_event(request, action, target_type, target_id, organization=None, metadata=None):
    """
    Utility to log audit events.
    """
    if metadata is None:
        metadata = {}

    actor = getattr(request, 'user', None)
    if actor and not actor.is_authenticated:
        actor = None

    ip_address = request.META.get('REMOTE_ADDR') if request else None

    # Try to get organization from actor if not provided
    organization_id = None
    if organization:
        organization_id = organization.id if hasattr(organization, 'id') else organization
    elif actor and hasattr(actor, 'organization_id'):
        organization_id = actor.organization_id

    # Bolt Optimization: Use organization_id directly to avoid redundant database queries for logging events.
    return AuditEvent.objects.create(
        actor=actor,
        organization_id=organization_id,
        target_type=target_type,
        target_id=str(target_id),
        action=action,
        metadata=metadata,
        ip_address=ip_address
    )
