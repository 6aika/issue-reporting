from iso8601.iso8601 import parse_date

from issues.api.utils import XMLList
from issues.extensions import IssueExtension


class HelExtension(IssueExtension):
    identifier = 'hel'
    prefetch_name = 'tasks'

    def get_extended_attributes(self, issue, context=None):
        from issues_hel.serializers import TaskSerializer
        tasks = TaskSerializer(many=True, read_only=True)
        return {
            'tasks': XMLList(tasks.to_representation(issue.tasks.all()), 'task')
        }

    def parse_extended_attributes(self, issue, extended_attributes):
        task_list = extended_attributes.pop('tasks', ())
        if task_list:
            self._import_task_list(issue, task_list)
        super().parse_extended_attributes(issue, extended_attributes)

    def _import_task_list(self, issue, task_list):
        from issues_hel.models import Task
        extant_tasks = Task.objects.filter(issue=issue)

        if extant_tasks.count() == len(task_list):
            # No change in number... maybe mtimes have changed?
            extant_mtimes = set(extant_tasks.values_list('task_modified', flat=True))
            new_mtimes = {parse_date(task_data.get('task_modified', '')) for task_data in task_list}
            if extant_mtimes == new_mtimes:
                # Nothing to do!
                return
        extant_tasks.delete()  # Have to wipe everything out first, sigh
        for task_data in task_list:
            Task.objects.create(
                issue_id=issue.id,
                task_state=task_data.get('task_state', ''),
                task_type=task_data.get('task_type', ''),
                owner_name=task_data.get('owner_name', ''),
                task_modified=parse_date(task_data.get('task_modified', '')),
                task_created=parse_date(task_data.get('task_created', '')),
            )
