from django.urls import path

from . import views

urlpatterns = [
    path('documents/',
         views.DocumentManagerView.as_view(),
         name='list_documents'),
    path('documents/<int:doc_id>/',
         views.DocumentView.as_view(),
         name='view_document'),
]