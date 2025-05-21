# Google API Tool Documentation

A Python package for easy interaction with Google Drive, Sheets, and Slides APIs.

## Prerequisites
- GCP (Google Cloud Platform) account
- GCP project with the Google Drive API enabled
- Service account with enambled permissions for selected Google Drive or Google Drive Folder

## Installation

You can install the package directly from PyPI:

```bash
pip install goopy
```

Or install from source:

```bash
git clone https://github.com/yourusername/goopy.git
cd goopy
pip install -e .
```

## Package Structure

```text
goopy/
├── src/
│   ├── BaseGoogleServiceAPI.py (Base class for Google API services)
│   ├── DriveServiceAPI.py (Google Drive API wrapper)
│   ├── SheetServiceAPI.py (Google Sheets API wrapper)
│   └── SlidesServiceApi.py (Google Slides API wrapper)
├── examples/
│   └── examples.py (Example usage of the API wrappers)
├── requirements.txt
└── README.md
```

## Usage

```python
from goopy import DriveService

drive = DriveService()

file_id = drive.create_file(
    file_name="My Document", 
    file_type="document",
    folder_link="https://drive.google.com/drive/folders/your-folder-id"
)
```

For more detailed examples, see the `examples` directory.


# Authentication with google services

This guide explains how to set up and use the Google API tool with proper authentication.

## Setting Up Google API Credentials

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown near the top of the page.
3. Click **New Project**.
4. Enter a project name and click **Create**.
5. Wait for the project to be created and select it from the project dropdown.

### 2. Enable Required APIs

1. From your project dashboard, navigate to **APIs & Services > Library**.
2. Search for and enable the following APIs:
   - Google Drive API
   - Google Sheets API (if needed)
   - Any other Google APIs your tool requires

### 3. Create Credentials

1. Navigate to **APIs & Services > Credentials**.
2. Click **Create Credentials** and select the appropriate type:
   - **OAuth 2.0 Client ID**: For applications that access user data
   - **Service Account**: For server-to-server interactions
   - **API Key**: For simple API calls not requiring user data access

#### For OAuth 2.0 Client ID:
1. Configure the OAuth consent screen if prompted.
2. Select application type (Web application, Desktop app, etc.).
3. Add authorized redirect URIs if necessary.
4. Click **Create**.
5. Download the JSON file containing your credentials.

#### For Service Account:
1. Enter a name and description for the service account.
2. Click **Create**.
3. Assign roles to the service account (e.g., Editor, Viewer).
4. Create a key (JSON format) and download it.
5. Keep this file secure as it grants access to your resources.

## Configuring Google Drive Access

### For Service Accounts:

1. Open your Google Drive.
2. Navigate to or create the folder you want to share.
3. Right-click on the folder and select **Share**.
4. In the "Add people and groups" field, enter the service account email (found in your JSON credentials file or in the Google Cloud Console).
5. Choose the appropriate permission level:
   - **Viewer**: Can only view files
   - **Commenter**: Can view and comment on files
   - **Editor**: Can view, comment, and edit files
   - **Content manager**: Can edit, delete, and add files
6. Click **Send**.

### For OAuth 2.0:

When your application uses OAuth 2.0, users will be prompted to grant the requested permissions the first time they authenticate.

## Using the Tool

1. Place your credentials file in a secure location accessible by the tool.
2. Configure the tool to use the credentials file path.
3. When running the tool for the first time with OAuth, you'll need to complete the authentication flow in a browser.
4. The tool should now have access to the specified Google Drive resources.

## Security Best Practices

- Never commit credentials to version control systems
- Use environment variables or secure secrets management
- Apply the principle of least privilege when assigning roles
- Regularly review and audit access permissions

## Troubleshooting

- **Access Denied Errors**: Verify the email address has been correctly shared with the resource
- **Authentication Errors**: Ensure credentials are valid and have not expired
- **API Quota Errors**: Check your usage limits in the Google Cloud Console

For more detailed information, refer to the [Google Cloud Documentation](https://cloud.google.com/docs).
