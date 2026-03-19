from .models import AuditEvent

def log_audit_event(request, action, target_type, target_id, organization=None, metadata=None):
    """
    Utility to log audit events. Safely handles missing request or user.
    """
    if metadata is None:
        metadata = {}

    actor = None
    ip_address = None

    if request:
        actor = getattr(request, 'user', None)
        if actor and not actor.is_authenticated:
            actor = None
        ip_address = request.META.get('REMOTE_ADDR')

    # Try to get organization from actor if not provided
    if organization is None and actor and hasattr(actor, 'organization'):
        organization = actor.organization

    return AuditEvent.objects.create(
        actor=actor,
        organization=organization,
        target_type=target_type,
        target_id=str(target_id),
        action=action,
        metadata=metadata,
        ip_address=ip_address
    )
