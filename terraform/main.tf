# Terraform Configuration for Africa Business Bridge on GCP
# This file automates the deployment of all infrastructure components

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "abb-terraform-state"
    prefix = "prod"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ============================================================================
# VARIABLES
# ============================================================================

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "nimble-service-475513-s1"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "europe-west1"
}

variable "domain" {
  description = "Domain name"
  type        = string
  default     = "africabusinessbridge.it"
}

variable "email" {
  description = "Email for SSL certificate"
  type        = string
  default     = "edoardo.ciech@gmail.com"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

# ============================================================================
# CLOUD SQL - PostgreSQL Database
# ============================================================================

resource "google_sql_database_instance" "main" {
  name             = "africa-business-bridge-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-f1-micro"
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = 20
    disk_autoresize   = true
    disk_autoresize_limit = 100

    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
    }

    ip_configuration {
      require_ssl = true
      
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    database_flags {
      name  = "log_statement"
      value = "all"
    }

    user_labels = {
      environment = "production"
      app         = "africa-business-bridge"
    }
  }

  deletion_protection = true

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "main" {
  name     = "africa_business_bridge"
  instance = google_sql_database_instance.main.name

  depends_on = [google_sql_database_instance.main]
}

resource "google_sql_user" "app_user" {
  name     = "abb_user"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# ============================================================================
# CLOUD STORAGE - File Uploads
# ============================================================================

resource "google_storage_bucket" "uploads" {
  name          = "abb-uploads-${var.project_id}"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["https://${var.domain}"]
    method          = ["GET", "HEAD", "DELETE", "POST", "PUT"]
    response_header = ["Content-Type", "x-goog-meta-*"]
    max_age_seconds = 3600
  }

  labels = {
    environment = "production"
    app         = "africa-business-bridge"
  }
}

resource "google_storage_bucket_iam_member" "uploads_access" {
  bucket = google_storage_bucket.uploads.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.manus_ai.email}"
}

# ============================================================================
# CLOUD RUN - Backend Service
# ============================================================================

resource "google_cloud_run_service" "backend" {
  name     = "africa-business-bridge-backend"
  location = var.region

  template {
    spec {
      service_account_name = data.google_service_account.manus_ai.email

      containers {
        image = "gcr.io/${var.project_id}/africa-business-bridge-backend:latest"

        env {
          name  = "ENVIRONMENT"
          value = "production"
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://abb_user:${var.db_password}@${google_sql_database_instance.main.private_ip_address}/africa_business_bridge"
        }

        env {
          name  = "SECRET_KEY"
          value = var.secret_key
        }

        env {
          name  = "BACKEND_CORS_ORIGINS"
          value = "https://${var.domain}"
        }

        env {
          name  = "UPLOAD_DIR"
          value = "gs://abb-uploads-${var.project_id}"
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }

      timeout_seconds = 3600
    }

    metadata {
      annotations = {
        "cloudsql-instances" = google_sql_database_instance.main.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true

  depends_on = [
    google_sql_database_instance.main,
    google_storage_bucket.uploads
  ]
}

resource "google_cloud_run_service_iam_member" "backend_public" {
  service = google_cloud_run_service.backend.name
  role    = "roles/run.invoker"
  member  = "allUsers"
  location = var.region
}

# ============================================================================
# CLOUD RUN - Frontend Service
# ============================================================================

resource "google_cloud_run_service" "frontend" {
  name     = "africa-business-bridge-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/africa-business-bridge-frontend:latest"

        env {
          name  = "VITE_API_URL"
          value = "https://api.${var.domain}/api/v1"
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "256Mi"
          }
        }
      }

      timeout_seconds = 300
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  service = google_cloud_run_service.frontend.name
  role    = "roles/run.invoker"
  member  = "allUsers"
  location = var.region
}

# ============================================================================
# LOAD BALANCER & CLOUD ARMOR
# ============================================================================

resource "google_compute_security_policy" "policy" {
  name = "abb-security-policy"

  # Allow all traffic by default
  rules {
    action   = "allow"
    priority = "65535"
    match {
      versioned_expr = "CEL"
      cel_expression = "true"
    }
    description = "Default rule"
  }

  # Rate limiting rule
  rules {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "CEL"
      cel_expression = "true"
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"

      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }

      ban_duration_sec = 600
    }
    description = "Rate limiting"
  }
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "google_service_account" "manus_ai" {
  account_id = "manus-ai"
}

# ============================================================================
# PRIVATE SERVICE CONNECTION (for Cloud SQL)
# ============================================================================

resource "google_compute_network" "private_network" {
  name = "abb-private-network"
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.private_network.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.private_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "backend_url" {
  description = "Backend service URL"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "Frontend service URL"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.uploads.name
}

output "next_steps" {
  description = "Next steps for deployment"
  value = <<-EOT
    1. Configure your domain DNS records:
       - api.${var.domain} -> ${google_cloud_run_service.backend.status[0].url}
       - ${var.domain} -> ${google_cloud_run_service.frontend.status[0].url}
    
    2. Set up SSL/TLS certificate for ${var.domain}
    
    3. Configure Cloud CDN for static assets
    
    4. Set up monitoring and alerting
    
    5. Configure backup policies
  EOT
}

