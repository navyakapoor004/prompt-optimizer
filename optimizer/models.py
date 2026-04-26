from django.db import models

class PromptHistory(models.Model):
    raw_prompt = models.TextField()
    optimized_prompt = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prompt #{self.pk} - {self.created_at.strftime('%d %b %Y')}"
