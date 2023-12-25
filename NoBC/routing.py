from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from user import consumers

websocket_urlpatterns = [
    path('<str:user_email>/message', consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": SessionMiddlewareStack(URLRouter(websocket_urlpatterns))
})

