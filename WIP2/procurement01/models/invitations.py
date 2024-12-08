from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class RFXInvitation(models.Model):
    rfx = models.ForeignKey("RFX", on_delete=models.CASCADE, related_name="invitations")
    supplier = models.ForeignKey(
        "Company", on_delete=models.CASCADE, related_name="rfx_invitations"
    )
    token = models.CharField(max_length=64, unique=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(64)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
