# Bucket the reconciliation partner reads exported payment records from.
resource "aws_s3_bucket" "payment_exports" {
  bucket = "payment-agent-payment-exports"
  acl    = "public-read"
}

resource "aws_s3_bucket_public_access_block" "payment_exports" {
  bucket                  = aws_s3_bucket.payment_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
