from django.db import models
from django.contrib.auth.models import User

class Evaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    idea_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Evaluation factors
    urgency = models.IntegerField(null=True, blank=True)
    market_size = models.IntegerField(null=True, blank=True)
    pricing_potential = models.IntegerField(null=True, blank=True)
    customer_acquisition_cost = models.IntegerField(null=True, blank=True)
    value_delivery_cost = models.IntegerField(null=True, blank=True)
    uniqueness = models.IntegerField(null=True, blank=True)
    speed_to_market = models.IntegerField(null=True, blank=True)
    upfront_investment = models.IntegerField(null=True, blank=True)
    upsell_potential = models.IntegerField(null=True, blank=True)
    evergreen_potential = models.IntegerField(null=True, blank=True)
    
    @property
    def total_score(self):
        return sum([
            self.urgency or 0,
            self.market_size or 0,
            self.pricing_potential or 0,
            self.customer_acquisition_cost or 0,
            self.value_delivery_cost or 0,
            self.uniqueness or 0,
            self.speed_to_market or 0,
            self.upfront_investment or 0,
            self.upsell_potential or 0,
            self.evergreen_potential or 0
        ])
    
    @property
    def result_category(self):
        score = self.total_score
        if score <= 50:
            return "low"
        elif score <= 74:
            return "medium"
        else:
            return "high"
    
    def get_factors(self):
        return [
            ("Urgency", self.urgency),
            ("Market Size", self.market_size),
            ("Pricing Potential", self.pricing_potential),
            ("Customer Acquisition Cost", self.customer_acquisition_cost),
            ("Value Delivery Cost", self.value_delivery_cost),
            ("Uniqueness", self.uniqueness),
            ("Speed to Market", self.speed_to_market),
            ("Upfront Investment", self.upfront_investment),
            ("Upsell Potential", self.upsell_potential),
            ("Evergreen Potential", self.evergreen_potential),
        ]