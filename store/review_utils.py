from orders.models import OrderProduct

class ReviewStatus:
    def __init__(self, user, product):
        self.user = user
        self.product = product
        self.is_authenticated = user.is_authenticated
        
        # Initialize instance variables
        self.has_ordered = False
        self.has_reviewed = False
        self.can_review = False
        
        if self.is_authenticated:
            self.has_ordered = self.check_ordered()
            self.has_reviewed = self.check_reviewed()
            self.can_review = self.has_ordered and not self.has_reviewed
        
    def check_ordered(self):
        if not self.user.is_authenticated:
            return False
        return OrderProduct.objects.filter(user=self.user, product=self.product, ordered=True).exists()

    def check_reviewed(self):
        if not self.user.is_authenticated:
            return False
        return self.product.reviewrating_set.filter(user=self.user).exists()
        


def submit_review(request, product, form):
    # Check if user is authenticated before processing the review
    if not request.user.is_authenticated:
        return False, "You need to be logged in to submit a review."
    
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.ip = request.META.get('REMOTE_ADDR')
        review.save()
        return True, "Thank you! Your review has been submitted."
    else:
        return False, "Please correct the errors in the form."
    
    