from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db import models

class Users(models.Model):
    name=models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    password = models.CharField(max_length=100)  # Plain text (not recommended for security)

    def __str__(self):
        return self.email

class TblAdmin(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100)  # Plain text (not recommended)

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=100)
    
class Recipe(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)  # main image
    video = models.FileField(upload_to="recipes/videos/", blank=True, null=True)  # NEW
    created_at = models.DateTimeField(auto_now_add=True)

class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="recipes/multiple/")

class UserRecipe(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="user_recipes")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to='user_recipes/main/', null=True, blank=True)
    video = models.FileField(upload_to='user_recipes/videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class UserRecipeImage(models.Model):
    recipe = models.ForeignKey(UserRecipe, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='user_recipes/gallery/')

class Notification(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

class Feedback(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    description = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}"
# --------------------------
# ADMIN RECIPE LIKE + COMMENT
# --------------------------

class RecipeLike(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'user')

class RecipeComment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# --------------------------
# USER RECIPE LIKE + COMMENT
# --------------------------
class UserRecipeLike(models.Model):
    recipe = models.ForeignKey(UserRecipe, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'user')

class UserRecipeComment(models.Model):
    recipe = models.ForeignKey(UserRecipe, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)