class InsuranceClaim(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="claims")
    policy = models.ForeignKey(UserPolicyPurchase, on_delete=models.CASCADE, related_name="claims")
    reason = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")], 
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Amount claimed
    documents = models.FileField(upload_to="claim_documents/", null=True, blank=True)  # Supporting documents
    incident_date = models.DateField(null=True, blank=True)  # Date of incident
    approval_date = models.DateField(null=True, blank=True)  # When the claim was approved
    rejection_reason = models.TextField(null=True, blank=True)  # If rejected, reason for rejection
    processing_notes = models.TextField(null=True, blank=True)  # Internal notes about claim processing
    payment_status = models.CharField(
        max_length=20, 
        choices=[("Unpaid", "Unpaid"), ("Processing", "Processing"), ("Paid", "Paid")], 
        default="Unpaid"
    )  # Payment status for claim  # Final payout amount after approval
    payout_date = models.DateField(null=True, blank=True)  # Date when the payout was made

    def __str__(self):
        return f"Claim #{self.id} - {self.user.username} ({self.status})"
