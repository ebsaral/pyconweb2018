from django.urls import path

from . import views

urlpatterns = [
    path('documents/',
         views.DocumentManagerView.as_view(),
         name='list_documents'),
    path('documents/download/<int:doc_id>/',
         views.download_document,
         name='download_document'),
    path('documents/delete/<int:doc_id>/',
         views.delete_document,
         name='delete_document'),
    path('handler/',
         views.handle_event,
         name='event_handler'),
]