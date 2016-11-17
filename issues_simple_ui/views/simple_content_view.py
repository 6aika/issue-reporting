from django.views.generic import TemplateView

from issues_simple_ui.models import Content


class SimpleContentView(TemplateView):
    """
    Base class for views that inject `title` and `content` into the context based on Content objects.
    """
    content_identifier = None

    def get_context_data(self, **kwargs):
        context = super(SimpleContentView, self).get_context_data(**kwargs)
        context.update(Content.retrieve(self.content_identifier))
        return context
