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

    # Bolt Optimization: use organization_id directly from actor to avoid redundant DB lookup
    if organization is None and actor and hasattr(actor, 'organization_id'):
        organization_id = actor.organization_id
    else:
        organization_id = getattr(organization, 'id', organization)

    return AuditEvent.objects.create(
        organization_id=organization_id,
        actor=actor,
        target_type=target_type,
        target_id=str(target_id),
        action=action,
        metadata=metadata,
        ip_address=ip_address
    )
