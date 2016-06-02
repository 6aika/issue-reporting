from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from issues.api.utils import XMLList
from issues.extensions import IssueExtension


class MediaExtension(IssueExtension):
    identifier = 'media'
    prefetch_name = 'media'

    def post_create_issue(self, request, issue, data):
        from issues_media.models import IssueMedia
        for file in request.FILES.getlist('media', ()):
            assert isinstance(file, UploadedFile)
            if file.size > 100 * 1024 * 1024:
                raise ValidationError("File %s is too large" % file)
            # TODO: Add mimetype validation somewhere around here
            IssueMedia.objects.create(
                issue=issue,
                file=file
            )

    def get_extended_attributes(self, issue, context=None):
        request = context['request']._request  # `_request` to access the actual WSGIRequest...
        return {
            'media_urls': XMLList([
                request.build_absolute_uri(im.file.url)
                for im
                in issue.media.all()
            ], 'media_url')
        }
