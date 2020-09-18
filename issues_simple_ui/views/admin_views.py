from datetime import datetime, timedelta

from django import forms
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.utils.encoding import force_str
from django.utils.formats import localize
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from issues.models import Issue
from issues_log.models import LogEntry


class AdminListView(ListView):
    model = Issue
    queryset = Issue.objects.order_by("-id")
    template_name = "issues_simple_ui/admin_list.html"
    context_object_name = "issues"
    page_kwarg = "page"
    paginate_by = 50
    filter_specs = [
        dict(id='unmoderated', title=_('Unmoderated'), q=Q(moderation='unmoderated')),
        dict(id='open', title=_('Open'), q=Q(status='open')),
        dict(id='closed', title=_('Closed'), q=Q(status='closed')),
        dict(
            id='2wk',
            title=_('New (2 weeks)'),
            q=lambda qs: qs.filter(requested_datetime__gt=now() - timedelta(days=14))
        ),
    ]
    filter_specs_by_id = {f['id']: f for f in filter_specs}

    def get_queryset(self):
        qs = super().get_queryset()
        filter = self.filter_specs_by_id.get(self.request.GET.get('filter'))
        if filter:
            q = filter['q']
            if callable(q):
                qs = q(qs)
            else:
                qs = qs.filter(q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_specs'] = self.filter_specs
        context['filter'] = self.request.GET.get('filter')
        return context


class LogForm(forms.ModelForm):
    class Meta:
        model = LogEntry
        fields = ('status', 'note', 'handler')

    def __init__(self, **kwargs):
        issue = kwargs.pop('issue')
        user = kwargs.pop('user')
        super().__init__(**kwargs)
        self.instance.issue = issue
        self.initial['handler'] = force_str(user)


class AdminDetailView(DetailView):
    model = Issue

    template_name = "issues_simple_ui/admin_detail.html"
    context_object_name = "issue"

    auto_field_names = (
        "status",
        "moderation",
        "service_notice",
        "requested_datetime",
        "updated_datetime",
        "expected_datetime",
        "submitter_email",
        "submitter_first_name",
        "submitter_last_name",
        "submitter_phone",
        "address",
        "lat",
        "long",
    )

    def get_log_form(self):
        return LogForm(
            user=self.request.user,
            issue=self.object,
            data=(self.request.POST if (self.request.POST and self.request.POST.get('action') == 'log') else None)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        issue = context[self.context_object_name]
        data = self.build_issue_data(issue)
        context['data'] = data
        context['log_form'] = self.get_log_form()
        return context

    def build_issue_data(self, issue):
        data = []

        def put(title, value, **kwargs):
            if not value:
                return
            data.append(dict(title=title, value=value, **kwargs))

        put(_('service'), f'{issue.service} ({issue.service.service_code})')
        for field in Issue._meta.get_fields():
            if field.name in self.auto_field_names:
                value = getattr(issue, field.attname, None)
                if isinstance(value, datetime):
                    value = localize(value)
                put(field.verbose_name, value)
        return data

    def post(self, request, *args, **kwargs):
        issue = self.object = self.get_object()
        action = self.request.POST.get('action')
        if action.startswith('moderation:'):
            issue.moderation = action.split(':')[-1]
            issue.full_clean()
            issue.save(update_fields=('moderation',))

        elif action == 'log':
            form = self.get_log_form()
            if form.is_valid():
                log_entry = form.save()
                issue.updated_datetime = now()
                if log_entry.note:
                    issue.status_notes = log_entry.note
                if log_entry.status == 'done':
                    issue.status = 'closed'
                issue.save(update_fields=('updated_datetime', 'status_notes', 'status',))
        return HttpResponseRedirect(self.request.path)
