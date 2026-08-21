from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    # Admin
    path("admin_index/", views.admin_index, name="admin_index"),
    path('admin_view_about/',views.admin_view_about,name='admin_view_about'),
    path("add_category/", views.add_category, name="add_category"),
    path("add_recipe/", views.add_recipe, name="add_recipe"),
    path("view_recipe/", views.view_recipe, name="view_recipe"),
    path("edit_recipe/", views.edit_recipe, name="edit_recipe"),
    path("delete_recipe/", views.delete_recipe, name="delete_recipe"),
    path("notifications", views.notifications, name="notifications"),
    path("notifications/read/<int:notification_id>/",views.mark_notification_read,name="mark_notification_read",),
    path("user_recipes/<int:user_id>/", views.user_recipes, name="user_recipes"),
    path("all-user-recipes/",views.admin_all_user_recipes,name="admin_all_user_recipes",),
    path("admin_view_users/", views.admin_view_users, name="admin_view_users"),
    path("user_feedback/", views.user_feedback_view, name="user_feedback"),

    # User
    path("user_index/", views.user_index, name="user_index"),
    path("user_view_about/",views.user_view_about,name="user_view_about"),
    path("search_recipes/", views.search_recipes, name="search_recipes"),
    path("like-recipe/<int:recipe_id>/", views.like_recipe, name="like_recipe"),
    path("add-comment/<int:recipe_id>/",views.add_recipe_comment,name="add_recipe_comment",),
    path("like-user-recipe/<int:recipe_id>/",views.like_user_recipe,name="like_user_recipe",),
    path("add-user-comment/<int:recipe_id>/",views.add_user_recipe_comment,name="add_user_recipe_comment", ),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("upload-recipe/", views.upload_recipe, name="upload_recipe"),
    path("view_recipes", views.view_recipes, name="view_recipes"),
    path("user_edit_recipe/<int:recipe_id>/", views.user_edit_recipe, name="user_edit_recipe"),
    path("user_delete_recipe/<int:recipe_id>/",views.user_delete_recipe,name="user_delete_recipe",),
    path("delete-recipe-comment/<int:comment_id>/",views.delete_recipe_comment,name="delete_recipe_comment",),
    path("delete-user-recipe-comment/<int:comment_id>/",views.delete_user_recipe_comment,name="delete_user_recipe_comment",),
    path('feedback/', views.feedback_view, name='feedback'),
    path("ai-recipe-recommendation/",views.ai_recipe_recommendation,name="ai_recipe_recommendation",),
]
