from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.crypto import get_random_string

def print_box(write, title, contents):
    title = "===== %s =====" % title
    box_width = len(title)
    write(title)
    for line in contents:
        write("# %s #" % str(line).center(box_width - 4))
    write("#" * box_width)


class Command(BaseCommand):
    help = 'create a superuser if one does not exist'

    def handle(self, *args, **options):
        if not get_user_model().objects.filter(is_superuser=True).exists():
            self.create_new_superuser()

    def create_new_superuser(self):
        username = 'admin%s' % get_random_string(3)
        password = get_random_string(8)
        get_user_model().objects.create_superuser(
            username=username,
            password=password,
            email='',
        )
        print_box(self.stderr.write, "SUPERUSER CREDENTIALS", [
            "Username: %s" % username,
            "Password: %s" % password,
        ])
