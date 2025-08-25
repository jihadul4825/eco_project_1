from django.db import models
from django.db.models import Avg, Count
from category.models import Category
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Account
# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='photos/products')
    stock           = models.IntegerField()
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def get_reviews_with_users(self):
        #Get all reviews for this product with user data (solves N+1)
        return self.reviewrating_set.select_related('user').filter(status=True)
    
    
    def get_average_rating(self):
        # Get average rating with a single query
        from django.db.models import Avg
        result = self.reviewrating_set.filter(status=True).aggregate(avg_rating=Avg('rating'))
        return result['avg_rating'] or 0
    
    def get_review_count(self):
        # Get review count with a single query
        return self.reviewrating_set.filter(status=True).count()
    
    def __str__(self):
        return self.product_name
    
        
    
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
    