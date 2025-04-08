# Streamlit Cloud Deployment Guide

This document provides instructions for deploying the Guangdong Population Flow Analysis application to Streamlit Cloud.

## Prerequisites

- A GitHub account
- The repository must be public or you must have a Streamlit Cloud account with access to private repositories

## Deployment Steps

1. Make sure your repository is pushed to GitHub
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in

3. Click on "New app"

4. Fill in the deployment details:
   - **Repository**: `https://github.com/mufasa78/guangdong`
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL or use the default

5. Click "Deploy"

## Configuration

The application is already configured for Streamlit Cloud with:

- Proper `requirements.txt` file with all dependencies
- `.streamlit/config.toml` with server settings
- Error handling for file operations that might not work in cloud environments

## Secrets Management

If you need to add API keys or other secrets:

1. Go to your app settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Add your secrets in TOML format, for example:
   ```toml
   [api_keys]
   some_api_key = "your-api-key-here"
   ```

4. Access secrets in your code with:
   ```python
   import streamlit as st
   api_key = st.secrets["api_keys"]["some_api_key"]
   ```

## Troubleshooting

- **File Access Issues**: The app has been modified to handle file access restrictions in cloud environments
- **Memory Limits**: If you encounter memory issues, consider optimizing data processing or using Streamlit's caching
- **Deployment Failures**: Check the logs in Streamlit Cloud for specific error messages

## Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)
