import logging
import os
import uuid

from django.conf import settings

from issues.models import Issue

logger = logging.getLogger(__name__)


def get_issues_count():
    queryset = Issue.objects
    if settings.SHOW_ONLY_MODERATED:
        queryset = queryset.exclude(status__iexact='MODERATION')
    return queryset.count()


def attach_files_to_issue(request, issue, files):
    for file in files:
        abs_url = ''.join([request.build_absolute_uri('/')[:-1], settings.MEDIA_URL, file.file.name])
        media_url = MediaURL(issue=issue, media_url=abs_url)
        media_url.save()
        issue.media_urls.add(media_url)
        # Attach the file to issue - not needed if using external Open311!
        issue.media_files.add(file)

    # Update the single media_url field to point to the 1st image
    issue.media_url = issue.media_urls.all()[0].media_url
    issue.save()


def save_file_to_db(file, form_id):
    # Create new unique random filename preserving extension
    original_filename = file.name
    size = file.size
    extension = os.path.splitext(file.name)[1]
    file.name = uuid.uuid4().hex + extension
    f_object = MediaFile(file=file, form_id=form_id, original_filename=original_filename, size=size)
    f_object.save()
    return file.name
