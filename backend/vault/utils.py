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

    # Bolt Optimization: Use organization_id directly from the actor or provided organization object,
    # avoiding redundant database queries for logging events.
    org_id = None
    if organization:
        org_id = organization.id if hasattr(organization, 'id') else organization
    elif actor and hasattr(actor, 'organization_id'):
        org_id = actor.organization_id

    return AuditEvent.objects.create(
        actor=actor,
        organization_id=org_id,
        target_type=target_type,
        target_id=str(target_id),
        action=action,
        metadata=metadata,
        ip_address=ip_address
    )
