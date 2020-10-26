#----------------------------------------------
# File with all api's urlspatterns in one place
#----------------------------------------------
from api.users.urls import urlpatterns as users_urlpattern

urlpatterns = []
urlpatterns += users_urlpattern
