from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'feedbacks', views.FeedbackViewSet, base_name='feedback')
router.register(r'services', views.ServiceViewSet, base_name='service')
