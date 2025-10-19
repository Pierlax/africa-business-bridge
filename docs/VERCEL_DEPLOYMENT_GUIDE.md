# Vercel Deployment Guide - Africa Business Bridge

This document provides a comprehensive guide for deploying the Africa Business Bridge platform on Vercel. It covers connecting the GitHub repository, configuring environment variables, and setting up the custom domain.

## 1. Overview

The Africa Business Bridge platform consists of a React frontend (Vite) and a FastAPI backend. For Vercel deployment, the FastAPI backend will be deployed as Serverless Functions within the Vercel environment. The project structure is already optimized for this setup, with the backend code located in the `/api` directory.

## 2. Prerequisites

- A GitHub account with access to the `Pierlax/africa-business-bridge` repository.
- A Vercel account (`edoardo-ciech-s-projects`) linked to your GitHub account.
- Access to DNS settings for the `africabusinessbridge.it` domain.

## 3. Deployment Steps

### 3.1. Connect GitHub Repository to Vercel

1.  **Log in to Vercel**: Go to [vercel.com](https://vercel.com/) and log in with your GitHub account.
2.  **Import Project**: From the Vercel Dashboard, click on "Add New..." -> "Project".
3.  **Select GitHub Repository**: Choose the `Pierlax/africa-business-bridge` repository from your GitHub repositories list. If it's not listed, you may need to grant Vercel access to it via your GitHub settings.
4.  **Configure Project**: Vercel should automatically detect the project as a monorepo with a React frontend and a Python backend. Ensure the following settings:
    -   **Root Directory**: Leave empty or set to `/` if prompted.
    -   **Build & Output Settings**:
        -   **Framework Preset**: React (Vite)
        -   **Build Command**: `pnpm run build`
        -   **Output Directory**: `dist` (for frontend)
    -   **Serverless Functions (for FastAPI Backend)**:
        -   Vercel will automatically detect the `api` directory and treat it as a source for Serverless Functions. No specific configuration is usually needed here, but ensure the `api` directory is recognized as a Python project.

### 3.2. Configure Environment Variables

Environment variables are crucial for the application to connect to the database, blockchain, and payment services. These must be set in the Vercel project settings.

1.  **Navigate to Project Settings**: In your Vercel project dashboard, go to "Settings" -> "Environment Variables".
2.  **Add Environment Variables**: Add the following variables. Ensure to mark them for both "Development", "Preview", and "Production" environments as needed.

| Variable Name | Description | Example Value |
|---|---|---|
| `SECRET_KEY` | Used for JWT token signing. Generate a strong, random string. | `your_super_secret_jwt_key_here` |
| `DATABASE_URL` | PostgreSQL connection string. (e.g., from Google Cloud SQL) | `postgresql://user:password@host:port/database` |
| `POLYGON_RPC_URL` | URL for Polygon (Mumbai Testnet or Mainnet) RPC endpoint. | `https://polygon-mumbai.g.alchemy.com/v2/YOUR_ALCHEMY_KEY` |
| `CIRCLE_API_KEY` | API Key for Circle payment service. | `sk_test_...` |
| `TRANSAK_API_KEY` | API Key for Transak payment service. | `your_transak_api_key` |
| `MOONPAY_API_KEY` | API Key for MoonPay payment service. | `pk_test_...` |
| `GCP_PROJECT_ID` | Google Cloud Project ID. | `nimble-service-475513-s1` |
| `GCP_SERVICE_ACCOUNT_KEY` | JSON content of the GCP service account key file (base64 encoded or as a string if Vercel supports multi-line secrets). **Ensure this is handled securely.** | `{"type": "service_account", ...}` |
| `FRONTEND_URL` | The production URL of your frontend application. | `https://africabusinessbridge.it` |
| `BACKEND_URL` | The production URL of your backend API. (This will be the Vercel deployment URL for your /api folder) | `https://africabusinessbridge.vercel.app/api/v1` (Vercel automatically handles this for serverless functions) |

**Note on `GCP_SERVICE_ACCOUNT_KEY`**: Vercel typically handles multi-line secrets by allowing them to be pasted directly. If not, you might need to base64 encode the JSON content and decode it in your application, or store it in a secret manager and access it via Vercel integrations.

### 3.3. Configure Custom Domains

To use `africabusinessbridge.it` as your primary domain, you need to configure it in Vercel.

1.  **Add Domain**: In your Vercel project dashboard, go to "Settings" -> "Domains".
2.  **Enter Domain**: Type `africabusinessbridge.it` and click "Add".
3.  **Verify Domain**: Vercel will provide DNS records (usually A records and/or CNAME records) that you need to add to your domain registrar's DNS settings.
4.  **Update DNS Records**: Log in to your domain registrar (where `africabusinessbridge.it` is registered) and add the provided DNS records. This typically involves:
    -   Setting an `A` record for `@` (or your root domain) to Vercel's IP address.
    -   Setting a `CNAME` record for `www` to `cname.vercel-dns.com`.
5.  **SSL Configuration**: Vercel automatically provisions and renews SSL certificates for your custom domains. Ensure that the email `edoardo.ciech@gmail.com` is associated with the domain for any potential verification or notifications.
6.  **Wait for Propagation**: DNS changes can take up to 48 hours to propagate globally, though it often happens much faster.

## 4. Deployment Trigger

Once the GitHub repository is connected and environment variables are set, Vercel will automatically deploy your project on every push to the `main` branch. You can also trigger manual deployments from the Vercel dashboard.

## 5. Post-Deployment Checks

-   Verify that the frontend loads correctly at `https://africabusinessbridge.it`.
-   Confirm that API endpoints (e.g., `https://africabusinessbridge.it/api/v1/auth/me`) are accessible and functioning.
-   Test all major features: authentication, business matching, blockchain contracts, payments, and the newly implemented UX features (onboarding, progressive disclosure, analytics, alerts).
-   Monitor Vercel logs for any errors or warnings during deployment and runtime.

This guide should enable a smooth deployment of the Africa Business Bridge platform on Vercel. For any specific issues, refer to the Vercel documentation or contact Vercel support.
