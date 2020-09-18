from django.dispatch import Signal

#: Signal fired when a new issue is posted via the API.
issue_posted = Signal()  # Provides arguments: ('request', 'issue')
