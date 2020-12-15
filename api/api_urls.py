#----------------------------------------------
# File with all api's urlspatterns in one place
#----------------------------------------------
from api.users.urls import urlpatterns as users_urlpatterns
from api.chats.urls import urlpatterns as chats_urlpatterns

urlpatterns = []
urlpatterns += users_urlpatterns
urlpatterns += chats_urlpatterns
