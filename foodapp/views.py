import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
    Users,
    TblAdmin,
    Category,
    Recipe,
    RecipeImage,
    UserRecipe,
    UserRecipeImage,
    Notification,
    Feedback,
    RecipeLike,
    RecipeComment,
    UserRecipeLike,
    UserRecipeComment,
)
# Create your views here.

def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def register(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        phone = (request.POST.get("phone") or "").strip()
        password = request.POST.get("password") or ""
        address = (request.POST.get("address") or "").strip()

        errors = {}
        # Name: required, max 15 (matches model)
        if not name:
            errors["name"] = "Full name is required."
        elif len(name) > 15:
            errors["name"] = "Name must be at most 15 characters."

        # Email: required, valid format, unique
        if not email:
            errors["email"] = "Email is required."
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            errors["email"] = "Enter a valid email address."
        elif Users.objects.filter(email=email).exists():
            errors["email"] = "This email is already registered."

        # Phone: required, 10–15 digits (optional + at start)
        phone_digits = re.sub(r"\D", "", phone)
        if not phone:
            errors["phone"] = "Phone number is required."
        elif len(phone_digits) < 10 or len(phone_digits) > 15:
            errors["phone"] = "Enter a valid phone number (10–15 digits)."

        # Password: required, min 8, max 100 (matches model)
        if not password:
            errors["password"] = "Password is required."
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        elif len(password) > 100:
            errors["password"] = "Password must be at most 100 characters."

        # Address: required
        if not address:
            errors["address"] = "Address is required."

        if errors:
            return render(request, "register.html", {
                "errors": errors,
                "form_data": {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "address": address,
                },
            })

        Users.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            address=address,
        )
        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    return render(request, "register.html", {"errors": {}, "form_data": {}})

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"Login attempt: {email}")  # Debugging line

        # ✅ Check if user is an admin
        try:
            admin = TblAdmin.objects.get(email=email, password=password)
            request.session["user_id"] = admin.id  # Store admin session
            request.session["is_admin"] = True  # Mark as admin
            
            messages.success(request, "Admin login successful!")
            return redirect("admin_index")
        except TblAdmin.DoesNotExist:
            pass  # Continue checking Users table

        # ✅ Check if user exists in Users table
        try:
            user = Users.objects.get(email=email, password=password)
            request.session["user_id"] = user.id
            request.session["is_admin"] = False  # Mark as regular user

            messages.success(request, "User login successful!")
            return redirect("user_index")
        except Users.DoesNotExist:
            messages.error(request, "Invalid email or password!")
            print("Login failed: User not found")

        return redirect("login")

    return render(request, "login.html")

def logout(request):
    request.session.flush()  # Clear the session
    messages.success(request, "You have been logged out.")

    # Redirect based on user type
    if request.session.get('is_admin'):  
        return redirect("login")  
    return redirect("login") 

#admin
def admin_index(request):
    unread_count = Notification.objects.filter(is_read=False).count()

    return render(request, 'admin/admin_index.html', {
        'unread_count': unread_count
    })

def admin_view_about(request):
    return render(request,'admin/admin_view_about.html')

def add_category(request):

    if request.method == "POST":

        # ADD CATEGORY
        if "add_category" in request.POST:
            name = request.POST.get("name", "").strip()

            if not name:
                messages.error(request, "Category name cannot be empty.")
            elif Category.objects.filter(name__iexact=name).exists():
                messages.error(request, "Category already exists!")
            else:
                Category.objects.create(name=name)
                messages.success(request, "Category added successfully!")

            return redirect("add_category")

        # EDIT CATEGORY
        if "edit_category" in request.POST:
            cat_id = request.POST.get("cat_id")
            new_name = request.POST.get("new_name", "").strip()

            category = get_object_or_404(Category, id=cat_id)

            if not new_name:
                messages.error(request, "Category name cannot be empty.")
            elif Category.objects.filter(name__iexact=new_name).exclude(id=cat_id).exists():
                messages.error(request, "Category already exists!")
            else:
                category.name = new_name
                category.save()
                messages.success(request, "Category updated successfully!")

            return redirect("add_category")

        # DELETE CATEGORY
        if "delete_category" in request.POST:
            cat_id = request.POST.get("cat_id")
            category = get_object_or_404(Category, id=cat_id)
            category.delete()
            messages.success(request, "Category deleted successfully!")
            return redirect("add_category")

    categories = Category.objects.all().order_by("name")
    return render(request, "admin/add_category.html", {"categories": categories})

def add_recipe(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        name = request.POST.get("name")
        description = request.POST.get("description")
        ingredients = request.POST.get("ingredients")
        instructions = request.POST.get("instructions")
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        multiple_images = request.FILES.getlist("multiple_images")

        if category_id and name and description and ingredients and instructions:
            category = Category.objects.get(id=category_id)

            recipe = Recipe.objects.create(
                category=category,
                name=name,
                description=description,
                ingredients=ingredients,
                instructions=instructions,
                image=image,
                video=video,
            )

            # Save multiple images
            for img in multiple_images:
                RecipeImage.objects.create(recipe=recipe, image=img)

            messages.success(request, "Recipe added successfully!")
            return redirect("add_recipe")

        messages.error(request, "All fields are required!")

    return render(request, "admin/add_recipe.html", {"categories": categories})


def view_recipe(request):
    recipes = Recipe.objects.all().prefetch_related(
        "likes__user",
        "comments__user",
        "images"
    )

    return render(request, "admin/view_recipe.html", {
        "recipes": recipes
    })


def edit_recipe(request):
    recipe_id = request.GET.get("id")  # Get recipe ID from URL
    if not recipe_id:
        messages.error(request, "Invalid request.")
        return redirect("view_recipe")

    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == "POST":
        # Update recipe details
        recipe.name = request.POST.get("name")
        recipe.description = request.POST.get("description")
        recipe.ingredients = request.POST.get("ingredients")
        recipe.instructions = request.POST.get("instructions")
        category_id = request.POST.get("category")
        recipe.category = get_object_or_404(Category, id=category_id)

        if "image" in request.FILES:
            recipe.image = request.FILES["image"]
        multiple_images = request.FILES.getlist("multiple_images")
        if "video" in request.FILES:
            recipe.video = request.FILES["video"]

        for img in multiple_images:
            RecipeImage.objects.create(recipe=recipe, image=img)

        recipe.save()
        messages.success(request, "Recipe updated successfully!")
        return redirect("view_recipe")  # Redirect after updating

    # If GET request, display the edit form
    categories = Category.objects.all()
    return render(request, "admin/edit_recipe.html", {"recipe": recipe, "categories": categories})

def delete_recipe(request):
    recipe_id=request.GET.get('id')
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    messages.success(request, 'Recipe deleted successfully!')
    return redirect('view_recipe')

def notifications(request):
    notifications = Notification.objects.select_related('user')\
                    .prefetch_related('user__user_recipes')\
                    .filter(is_read=False)\
                    .order_by('-created_at')

    return render(request, 'admin/notifications.html', {
        'notifications': notifications
    })

def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

#From notifiaction page
def user_recipes(request, user_id):
    user = get_object_or_404(Users, id=user_id)

    recipes = UserRecipe.objects.filter(user=user).prefetch_related(
        "likes__user",
        "comments__user",
        "images"
    )

    return render(request, 'admin/user_recipes.html', {
        'user': user,
        'recipes': recipes
    })

def user_feedback_view(request):
    feedbacks = Feedback.objects.select_related('user').all().order_by('-created_at')  # All feedbacks
    return render(request, 'admin/user_feedback.html', {'feedbacks': feedbacks})


def admin_all_user_recipes(request):
    recipes = UserRecipe.objects.select_related("user", "category") \
        .prefetch_related("likes__user", "comments__user", "images")

    return render(request, "admin/all_user_recipes.html", {
        "recipes": recipes
    })


def admin_view_users(request):
    # Optional: simple admin-only guard
    if not request.session.get("is_admin"):
        return redirect("login")

    if request.method == "POST":
        user_id = request.POST.get("delete_user_id")
        if user_id:
            user = get_object_or_404(Users, id=user_id)
            user.delete()
            messages.success(request, "User deleted successfully.")
            return redirect("admin_view_users")

    users = Users.objects.all().order_by("id")
    return render(request, "admin/admin_view_users.html", {"users": users})

#User
def user_index(request):
    return render(request,'user/user_index.html')

def user_view_about(request):
    return render(request,'user/user_view_about.html')

def search_recipes(request):
    query = request.GET.get("query")
    category_id = request.GET.get("category")

    if category_id:
        category_id = int(category_id)

    admin_recipes = Recipe.objects.all().prefetch_related("likes", "comments")
    user_recipes = UserRecipe.objects.all().prefetch_related("likes", "comments")

    if query:
        admin_recipes = admin_recipes.filter(name__icontains=query)
        user_recipes = user_recipes.filter(title__icontains=query)

    if category_id:
        admin_recipes = admin_recipes.filter(category_id=category_id)
        user_recipes = user_recipes.filter(category_id=category_id)

    return render(request, "user/search_recipes.html", {
        "admin_recipes": admin_recipes,
        "user_recipes": user_recipes,
        "categories": Category.objects.all(),
        "query": query,
        "selected_category": category_id
    })

def like_recipe(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = Users.objects.get(id=user_id)

    like, created = RecipeLike.objects.get_or_create(recipe=recipe, user=user)

    if not created:
        like.delete()  # Unlike

    return redirect(request.META.get('HTTP_REFERER'))
def add_recipe_comment(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = Users.objects.get(id=user_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            RecipeComment.objects.create(
                recipe=recipe,
                user=user,
                comment=comment_text
            )

    return redirect(request.META.get('HTTP_REFERER'))

def like_user_recipe(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(UserRecipe, id=recipe_id)
    user = Users.objects.get(id=user_id)

    like, created = UserRecipeLike.objects.get_or_create(recipe=recipe, user=user)

    if not created:
        like.delete()  # Unlike

    return redirect(request.META.get('HTTP_REFERER'))

def add_user_recipe_comment(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(UserRecipe, id=recipe_id)
    user = Users.objects.get(id=user_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            UserRecipeComment.objects.create(
                recipe=recipe,
                user=user,
                comment=comment_text
            )

    return redirect(request.META.get('HTTP_REFERER'))

def user_profile(request):
    user_id = request.session.get('user_id')  # Get user ID from session
    if not user_id:
        return redirect('login')  # Redirect to login if session is missing

    try:
        user = Users.objects.get(id=user_id)  # Fetch user from DB
    except Users.DoesNotExist:
        return redirect('login')  # Redirect if user not found

    return render(request, 'user/user_profile.html', {'user': user})


def edit_profile(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    user = get_object_or_404(Users, id=user_id)

    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        address = (request.POST.get("address") or "").strip()

        errors = {}

        # Name: optional but if provided must be <= 15
        if name and len(name) > 15:
            errors["name"] = "Name must be at most 15 characters."

        # Phone: optional but if provided, 10–15 digits
        if phone:
            phone_digits = re.sub(r"\D", "", phone)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                errors["phone"] = "Enter a valid phone number (10–15 digits)."

        # Address: optional (model allows blank), no extra rules

        if errors:
            return render(
                request,
                "user/edit_profile.html",
                {
                    "user": user,
                    "errors": errors,
                    "form_data": {
                        "name": name or user.name or "",
                        "phone": phone or user.phone or "",
                        "address": address or user.address or "",
                    },
                },
            )

        # Save updates
        user.name = name or user.name
        user.phone = phone or user.phone
        user.address = address or user.address
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("user_profile")

    # GET: pre-fill with current values
    form_data = {
        "name": user.name or "",
        "phone": user.phone or "",
        "address": user.address or "",
    }
    return render(
        request,
        "user/edit_profile.html",
        {"user": user, "errors": {}, "form_data": form_data},
    )

def upload_recipe(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        multiple_images = request.FILES.getlist('multiple_images')

        user = Users.objects.get(id=user_id)
        category = Category.objects.get(id=category_id) if category_id else None

        recipe = UserRecipe.objects.create(
            user=user,
            category=category,
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            image=image,
            video=video
        )

        for img in multiple_images:
            UserRecipeImage.objects.create(recipe=recipe, image=img)

        Notification.objects.create(
            user=user,
            message=f"{user.name} uploaded a new recipe: {title}"
        )

        messages.success(request, "Recipe uploaded successfully!")
        return redirect('view_recipes')

    return render(request, 'user/upload_recipe.html', {'categories': categories})

def view_recipes(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    user = get_object_or_404(Users, id=user_id)

    recipes = UserRecipe.objects.filter(user=user) \
        .prefetch_related("likes__user", "comments__user")

    return render(request, 'user/view_recipes.html', {
        'recipes': recipes,
        'user': user
    })

def user_edit_recipe(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(UserRecipe, id=recipe_id, user_id=user_id)
    categories = Category.objects.all()

    if request.method == "POST":
        recipe.title = request.POST.get("title")
        recipe.description = request.POST.get("description")
        recipe.ingredients = request.POST.get("ingredients")
        recipe.instructions = request.POST.get("instructions")

        category_id = request.POST.get("category")
        if category_id:
            recipe.category = Category.objects.get(id=category_id)

        # Update main image
        if request.FILES.get("image"):
            recipe.image = request.FILES.get("image")

        # Update video
        if request.FILES.get("video"):
            recipe.video = request.FILES.get("video")

        recipe.save()

        # Add new gallery images
        multiple_images = request.FILES.getlist("multiple_images")
        for img in multiple_images:
            UserRecipeImage.objects.create(recipe=recipe, image=img)

        messages.success(request, "Recipe updated successfully!")
        return redirect("view_recipes")

    return render(request, "user/edit_recipe.html", {
        "recipe": recipe,
        "categories": categories
    })

def user_delete_recipe(request, recipe_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    recipe = get_object_or_404(UserRecipe, id=recipe_id, user_id=user_id)

    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted successfully!")
        return redirect("view_recipes")

    return render(request, "user/delete_recipe.html", {"recipe": recipe})

# -----------------------------
# DELETE ADMIN RECIPE COMMENT
# -----------------------------
def delete_recipe_comment(request, comment_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    comment = get_object_or_404(RecipeComment, id=comment_id)

    # Only allow owner to delete
    if comment.user.id == user_id:
        comment.delete()

    return redirect(request.META.get("HTTP_REFERER"))

#-----------------------------
# DELETE USER RECIPE COMMENT
# -----------------------------
def delete_user_recipe_comment(request, comment_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    comment = get_object_or_404(UserRecipeComment, id=comment_id)

    # Only allow owner to delete
    if comment.user.id == user_id:
        comment.delete()

    return redirect(request.META.get("HTTP_REFERER"))

def feedback_view(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, 'You must be logged in to submit feedback.')
            return redirect('login')

        description = request.POST.get('description')
        rating = request.POST.get('rating')

        if not description or not rating:
            messages.error(request, 'All fields are required.')
            return redirect('feedback')

        user = Users.objects.get(id=user_id)
        Feedback.objects.create(user=user, description=description, rating=rating)
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('feedback')   # stay on same page

    # 👇 GET ALL FEEDBACKS
    feedbacks = Feedback.objects.select_related('user').order_by('-created_at')

    return render(request, 'user/feedback.html', {
        'feedbacks': feedbacks
    })
