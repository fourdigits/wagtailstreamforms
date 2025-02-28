from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _


def get_file_storage():
    storage_class = getattr(settings, "WAGTAILSTREAMFORMS_FILE_STORAGE", None)
    return import_string(storage_class)() if storage_class else default_storage


class FormSubmissionFile(models.Model):
    """Data for a form submission file."""

    submission = models.ForeignKey(
        "FormSubmission",
        verbose_name=_("Submission"),
        on_delete=models.CASCADE,
        related_name="files",
    )
    field = models.CharField(verbose_name=_("Field"), max_length=255)
    file = models.FileField(
        verbose_name=_("File"), upload_to="streamforms/", storage=get_file_storage
    )

    def __str__(self):
        return self.file.name

    class Meta:
        ordering = ["field", "file"]
        verbose_name = _("Form submission file")

    @property
    def url(self):
        return self.file.url


def delete_file_from_storage(instance, **kwargs):
    """Cleanup deleted files from disk"""
    transaction.on_commit(lambda: instance.file.delete(False))


post_delete.connect(delete_file_from_storage, sender=FormSubmissionFile)
